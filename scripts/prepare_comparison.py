"""Generate local comparison inputs; datasets/target manifests are never committed."""
import argparse
import hashlib
import json
from pathlib import Path
import h5py


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--profile', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--flow-precision', choices=['bf16', 'fp16', 'tf32', 'fp32'], default='fp32')
    p.add_argument('--decoder-precision', choices=['bf16', 'fp16', 'tf32', 'fp32'], default='fp32')
    a = p.parse_args()
    profile = json.loads(a.profile.read_text())
    if profile['status'] != 'passed':
        raise ValueError('requires a completed profile that passes the utilization gate')
    with h5py.File(a.source/'data/phase1_dataset/dataset_exp_val_esmc.h5', 'r') as h:
        ids = sorted(h['val'])
    if len(ids) != 626:
        raise ValueError('development target count changed')
    models = {}
    for name, checkpoint in [('pair', 'last_pf_459M_p128x8_long512_scratch.ckpt'),
                             ('pair_free', 'best_lf_459M_nopair_long512_r4b.pt')]:
        rows = [r for r in profile['selected'] if r['checkpoint'] == checkpoint]
        if {r['padded_length'] for r in rows} != {128, 256, 384, 512}:
            raise ValueError('missing profiled length bucket')
        models[name] = dict(checkpoint=checkpoint,
                           batches={str(r['padded_length']): r['batch'] for r in rows})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    ids_file = a.output.parent/'development626_ids.txt'
    ids_text = '\n'.join(ids)+'\n'
    config = dict(experiment='existing frozen heads: accuracy vs sampling cost',
        expected_targets=626, target_manifest=ids_file.name,
        target_manifest_sha256=hashlib.sha256(ids_text.encode()).hexdigest(), target_ids=ids,
        seed=0, samples=3, flow_steps=[10, 25, 50], guidance=[1.0, 2.0], decoder_steps=3,
        flow_precision=a.flow_precision, decoder_precision=a.decoder_precision,
        internal_minutes=80, models=models, profile_report=str(a.profile),
        profile_report_sha256=hashlib.sha256(a.profile.read_bytes()).hexdigest(),
        batching_control=dict(max_ca_rmsd_A=0.2, min_self_ca_lddt=0.99,
                              max_reference_ca_lddt_change=0.005), max_gpus_this_project=8)
    if a.output.exists():
        raise FileExistsError(a.output)
    ids_file.write_text(ids_text)
    a.output.write_text(json.dumps(config, indent=2)+'\n')


if __name__ == '__main__':
    main()
