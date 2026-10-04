"""Bounded GPU inference sizing on real cached embeddings. No model training.

Measures both useful throughput and memory. Repeated targets in profiling
batches have independent noise. No profile output is an accuracy benchmark.
SM activity requires valid Nsight Systems or DCGM hardware counters.
"""
import argparse
import gc
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
import torch
import h5py
from torch.nn import functional as F
from latentfold.checkpoints import load_legacy
from latentfold.data import read_record, collate
from latentfold.decoder import load_proteinae
from latentfold.flow import SampleConfig, sample, target_noise


def atomic_json(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temp.replace(path)


class Telemetry:
    def __init__(self, output, nsys_metrics=False):
        self.processes, self.files = [], []
        self.info = {}
        properties = torch.cuda.get_device_properties(0)
        self.info.update(cuda_device_name=properties.name, cuda_visible_sm_count=properties.multi_processor_count,
                         cuda_total_memory_bytes=properties.total_memory,
                         mps_active_thread_percentage=os.environ.get('CUDA_MPS_ACTIVE_THREAD_PERCENTAGE'))
        uuid = str(properties.uuid)
        if not uuid.startswith("GPU-"):
            uuid = "GPU-" + uuid
        self.info["uuid"] = uuid
        smi = shutil.which("nvidia-smi")
        if smi:
            self.start([smi, "-i", uuid,
                        "--query-gpu=timestamp,uuid,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw",
                        "--format=csv,noheader,nounits", "--loop-ms=1000"], output / "nvml.csv")
            mapping = subprocess.run([smi, "-i", uuid, "--query-gpu=index,uuid", "--format=csv,noheader"],
                                     capture_output=True, text=True, timeout=10)
            indices = [line.split(",")[0].strip() for line in mapping.stdout.splitlines() if uuid in line]
        else:
            indices = []
        dcgmi = shutil.which("dcgmi")
        if os.environ.get('LATENTFOLD_GPU_COUNTERS') == 'dcgm':
            nsys_metrics = False
        self.info["dcgm_status"] = "unavailable"
        counters_off = os.environ.get('LATENTFOLD_GPU_COUNTERS') == 'off'
        if counters_off:
            self.info['dcgm_status'] = 'disabled by explicit job configuration'
            self.info['nsys_status'] = 'not requested; NVML-only telemetry, no SM-activity claim'
        elif nsys_metrics:
            self.info["dcgm_status"] = "disabled to avoid counter conflict with Nsight Systems"
            self.info["nsys_status"] = "requested by job wrapper; validate exported GPU_METRICS before claiming utilization"
        if dcgmi and not nsys_metrics and not counters_off:
            try:
                from scoped_gpu_counters import assigned_dcgm_gpu
                job_id = os.environ.get('SLURM_JOB_ID', '')
                if os.environ.get('SLURM_ARRAY_JOB_ID') and os.environ.get('SLURM_ARRAY_TASK_ID'):
                    job_id = os.environ['SLURM_ARRAY_JOB_ID'] + '_' + os.environ['SLURM_ARRAY_TASK_ID']
                index, identity = assigned_dcgm_gpu(Path(__file__).resolve().parents[1], job_id, uuid, dcgmi)
                (output / "dcgm_identity.txt").write_text(identity)
                self.info.update(dcgm_gpu_index=index, dcgm_uuid_verified=True, dcgm_job_id=job_id)
                catalog = subprocess.run([dcgmi, "profile", "-l", "-i", index],
                                         capture_output=True, text=True, timeout=5)
                (output / "dcgm_catalog.txt").write_text(catalog.stdout + catalog.stderr)
                if catalog.returncode == 0:
                    self.start([dcgmi, "dmon", "-i", index, "-e", "1001,1002,1004,1005", "-d", "1000"], output / "dcgm.txt")
                    self.info.update(dcgm_status="requested; counter output must be validated",dcgm_fields=[1001,1002,1004,1005])
                else:
                    self.info["dcgm_status"] = "profiling fields unavailable; no composite-utilization claim"
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                self.info["dcgm_status"] = "counter probe unavailable: " + type(error).__name__

        self.info["nvml_caveat"] = "GPU busy time is not SM activity or FLOP efficiency"

        atomic_json(output / "device_metadata.json", self.info)

    def start(self, command, path):
        handle = path.open("w")
        self.files.append(handle)
        self.processes.append(subprocess.Popen(command, stdout=handle, stderr=subprocess.STDOUT))

    def close(self):
        for process in self.processes:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for handle in self.files:
            handle.close()


def padded_batch(records, count, length, device):
    chosen = [dict(records[i % len(records)]) for i in range(count)]
    ids = []
    for i, record in enumerate(chosen):
        record["id"] = f"{record['id']}::profile-copy-{i}"
        ids.append(record["id"])
    batch = collate(chosen)
    delta = length - batch["esm"].shape[1]
    if delta < 0:
        raise ValueError("bucket shorter than sequence")
    batch["esm"] = F.pad(batch["esm"], (0, 0, 0, delta))
    batch["mask"] = F.pad(batch["mask"], (0, delta))
    noise = target_noise(ids, batch["lengths"], 8, seed=0)
    dn = target_noise(ids, [4*n for n in batch["lengths"]], 3, seed=0, stream="decoder")
    noise = F.pad(noise, (0, 0, 0, length-noise.shape[1]))
    dn = F.pad(dn, (0, 0, 0, 4*length-dn.shape[1]))
    # Profiling excludes disk I/O and H2D; these tensors are explicitly resident.
    return batch["esm"].to(device), batch["mask"].to(device), noise.to(device), dn.to(device), sum(batch["lengths"])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--checkpoints", nargs="+", required=True)
    p.add_argument("--lengths", nargs="+", type=int, default=[128, 256, 384, 512])
    p.add_argument("--batches", nargs="+", type=int, default=[1, 4, 16, 32, 64, 128, 256])
    p.add_argument("--steps", type=int, default=25)
    p.add_argument("--measure-seconds", type=float, default=5)
    p.add_argument("--max-repeats", type=int, default=12)
    p.add_argument("--memory-fraction", type=float, default=0.85)
    p.add_argument("--minutes", type=float, default=24)
    p.add_argument("--compile-blocks", action="store_true")
    p.add_argument("--nsys-metrics", action="store_true")
    p.add_argument("--allow-gpu", action="store_true")
    a = p.parse_args()
    if not a.allow_gpu:
        p.error("GPU profiling requires user permission and --allow-gpu")
    if not 0 < a.memory_fraction < 1 or min(a.batches+a.lengths) < 1 or a.max_repeats < 1 or a.minutes <= 0 or a.measure_seconds <= 0:
        p.error("invalid profiling limits")
    a.output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(8)
    torch.set_float32_matmul_precision("high")
    torch.cuda.set_device(0)
    torch.manual_seed(0)
    start = time.time()
    deadline = time.monotonic() + a.minutes * 60
    report = {"status": "running", "job_id": os.environ.get("SLURM_JOB_ID"), "gpu": torch.cuda.get_device_name(0),
              "torch": torch.__version__, "gpu_bytes": torch.cuda.get_device_properties(0).total_memory,
              "steps": a.steps, "guidance": 2.0, "decoder_steps": 3, "precision": "bf16 autocast",
              "scope": "cached embeddings to CA; fixed input tensors on GPU; excludes ESMC and I/O",
              "started_unix": start, "compile_blocks": a.compile_blocks, "rows": []}
    telemetry = None
    signal.signal(signal.SIGTERM, lambda signum, frame: (_ for _ in ()).throw(KeyboardInterrupt("Slurm termination")))
    try:
        telemetry = Telemetry(a.output, a.nsys_metrics)
        report["telemetry"] = telemetry.info
        atomic_json(a.output / "profile.json", report)
        h5 = a.source / "data/phase1_dataset/dataset_exp_val_esmc.h5"
        buckets = {length: [] for length in a.lengths}
        with h5py.File(h5, "r") as h:
            for name in h["val"]:
                n = len(h["val"][name].attrs["sequence"])
                fits = [length for length in sorted(buckets) if n <= length]
                if fits and len(buckets[fits[0]]) < 16:
                    buckets[fits[0]].append(name)
        records = {length: [read_record(h5, "val", name, embedding_dim=2560) for name in ids] for length, ids in buckets.items()}
        report["profile_target_ids"] = buckets
        decoder = load_proteinae(a.source / "ProteinAE_v1", a.source / "ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt").cuda()
        for checkpoint in a.checkpoints:
            if time.monotonic() >= deadline:
                break
            model, arch = load_legacy(a.source / "data/phase1_dataset" / checkpoint, trusted_pickle=True)
            model.cuda().eval()
            for parameter in model.parameters():
                parameter.requires_grad_(False)
            if a.compile_blocks:
                model.blocks = torch.nn.ModuleList([torch.compile(block, dynamic=True) for block in model.blocks])
            print(f"Loaded {checkpoint}: {sum(p.numel() for p in model.parameters()):,} parameters", flush=True)
            for length in a.lengths:
                if not records[length]:
                    continue
                last_peak, last_count = None, None
                baseline_bytes = torch.cuda.memory_allocated()
                for count in a.batches:
                    if time.monotonic() >= deadline:
                        break
                    if last_peak is not None:
                        predicted_peak = baseline_bytes + (last_peak-baseline_bytes)*count/last_count
                        if predicted_peak > a.memory_fraction * report["gpu_bytes"]:
                            break
                    tensors = None
                    gc.collect()
                    torch.cuda.empty_cache()
                    torch.cuda.reset_peak_memory_stats()
                    row = {"checkpoint": checkpoint, "padded_length": length, "batch": count, "start_unix": time.time()}
                    try:
                        tensors = padded_batch(records[length], count, length, "cuda")
                        esm, mask, noise, dn, residues = tensors
                        cfg = SampleConfig(steps=a.steps, guidance=2)
                        @torch.no_grad()
                        def execute(cache=True):
                            with torch.autocast("cuda", dtype=torch.bfloat16):
                                z = sample(model, esm, mask, cfg, noise=noise, cache_condition=cache)
                                return decoder(z.float(), mask, noise=dn)
                        # Check the optimization on real weights at a small batch.
                        if count == 1:
                            old = execute(False)
                            new = execute(True)
                            torch.testing.assert_close(old, new, rtol=1e-3, atol=0.02)
                            row["cache_coordinate_max_abs_A"] = float((old-new).abs().max())
                            del old, new
                        else:
                            execute()
                        torch.cuda.synchronize()
                        row["measure_start_unix"] = time.time()
                        range_name = f"measure::{checkpoint}::L{length}::B{count}"
                        row["nvtx_range"] = range_name
                        torch.cuda.nvtx.range_push(range_name)
                        t0 = time.perf_counter()
                        completed = 0
                        while completed < a.max_repeats:
                            ca = execute()
                            del ca
                            torch.cuda.synchronize()
                            completed += 1
                            if time.perf_counter()-t0 >= a.measure_seconds or time.monotonic() >= deadline:
                                break
                        torch.cuda.nvtx.range_pop()
                        seconds = (time.perf_counter()-t0)/completed
                        allocated = torch.cuda.max_memory_allocated()
                        row.update(status="ok", seconds_per_batch=seconds, proteins_per_second=count/seconds,
                                   real_residues_per_second=residues/seconds, padding_fraction=1-residues/(count*length),
                                   peak_allocated_bytes=allocated, peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                                   memory_fraction=allocated/report["gpu_bytes"], measured_batches=completed)
                        last_peak, last_count = allocated, count
                    except torch.cuda.OutOfMemoryError:
                        row["status"] = "oom"
                    finally:
                        row["end_unix"] = time.time()
                        report["rows"].append(row)
                        atomic_json(a.output / "profile.json", report)
                        print(json.dumps(row), flush=True)
                        if tensors is not None:
                            del esm, mask, noise, dn
                        tensors = None
                        # execute's closure references variable cells, not tensor snapshots.
                    if row["status"] == "oom" or row.get("memory_fraction", 0) >= a.memory_fraction:
                        break
            del model
            gc.collect()
            torch.cuda.empty_cache()
        report["status"] = "completed_profile" if time.monotonic() < deadline else "time_budget_reached"
        report["scaling_gate"] = "Requires measured SM activity >=0.50 and validated throughput; NVML busy time alone cannot pass"
    except BaseException as error:
        report["status"], report["error"] = "failed", f"{type(error).__name__}: {error}"
        raise
    finally:
        if telemetry:
            telemetry.close()
        report["ended_unix"] = time.time()
        atomic_json(a.output / "profile.json", report)


if __name__ == "__main__":
    main()
