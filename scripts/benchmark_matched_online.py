"""Alternating same-H200 sequence-to-selected-backbone comparison."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import time

import h5py
import torch
from latentfold.batching import requests_by_bucket
from latentfold.checkpoints import load_legacy
from latentfold.data import read_record
from latentfold.decoder import load_proteinae
from latentfold.embedding import FinalESMC
from latentfold.flow import SampleConfig
from latentfold.metrics import ca_metrics
from latentfold.online_inputs import sequence_noise_batch, select_trios
from collect_comparison import infer, write_batch
from matched_online_analysis import ORDER, VARIANTS, fingerprint
from predict import file_identity
from profile_gpu import atomic_json, Telemetry
from score_comparison import score_batch, write_scores


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'config', 'output', 'usalign'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    for path_key in ('target_manifest', 'development_clusters', 'protocol'):
        if hashlib.sha256(Path(config[path_key]).read_bytes()).hexdigest() != config[path_key+'_sha256']:
            raise ValueError('changed frozen input: '+path_key)
    ids = Path(config['target_manifest']).read_text().splitlines()
    if len(ids) != 626 or len(set(ids)) != 626 or config['batches'] != {'128':126,'256':63,'384':30,'512':30}:
        raise ValueError('unexpected development coverage or batch sizes')
    all_ids = ids[:]
    shard = int(os.environ.get('SLURM_ARRAY_TASK_ID', '0'))
    if config.get('shards') != 4 or not 0 <= shard < 4:
        raise ValueError('expected four predeclared target shards')
    config.update(all_target_ids=all_ids, samples=3, guidance=[2], shard=shard)
    args.output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(4)
    torch.cuda.set_device(0)
    torch.cuda.set_per_process_memory_fraction(.85)
    started = time.monotonic()
    manifest = dict(status='running', config=config, source=str(args.source), passes=[], variants=VARIANTS,
        timing_scope='sequences to selected backbone: tokenization, fresh ESMC, deterministic input construction, head, decoder, coordinate transfer and CPU CA-lDDT medoid; excludes loading, controls, scoring and artifact writes',
        memory_scope='Both ESMC precisions resident; not standalone deployment peak memory', order=ORDER)
    atomic_json(args.output/'manifest.json', manifest)
    telemetry = None
    scorers = None
    children = {}
    try:
        dataset = args.source/'data/phase1_dataset/dataset_exp_val_esmc.h5'
        records = [read_record(dataset, 'val', name, embedding_dim=2560) for name in all_ids]
        # Balance each padded-length bucket deterministically, using sequences only.
        selected = []
        for length in (128,256,384,512):
            group = sorted([r for r in records if next(b for b in (128,256,384,512) if len(r['sequence'])<=b)==length], key=lambda r:r['id'])
            selected.extend(group[shard::4])
        records = selected
        ids = [r['id'] for r in records]
        config['target_ids'] = ids
        atomic_json(args.output/'manifest.json', manifest)
        ckpt = args.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt'
        ae = args.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt'
        manifest.update(dataset=file_identity(dataset), checkpoint=file_identity(ckpt, hash_contents=True),
            decoder_checkpoint=file_identity(ae, hash_contents=True),
            embedding_artifacts=[file_identity(p, hash_contents=True) for p in sorted((args.source/'data/esmc6b').glob('*')) if p.is_file() and p.suffix in ('.json', '.safetensors')])
        model, _ = load_legacy(ckpt, trusted_pickle=True)
        model.cuda().eval().requires_grad_(False)
        decoder = load_proteinae(args.source/'ProteinAE_v1', ae).cuda()
        embeddings = {name: FinalESMC(args.source/'data/esmc6b', precision=v['embedding']) for name,v in VARIANTS.items()}
        manifest['dual_resident_parameters'] = sum(p.numel() for m in (model, decoder, *[e.model for e in embeddings.values()]) for p in m.parameters())
        manifest['active_pipeline_parameters'] = sum(p.numel() for m in (model, decoder, embeddings['reference'].model) for p in m.parameters())
        batches = {int(k):v for k,v in config['batches'].items()}
        buckets = requests_by_bucket(records, batches, 3)
        telemetry = Telemetry(args.output, True)

        def predict(requests, length, name):
            variant = VARIANTS[name]
            unique = {r['id']:r for r,_ in requests}
            ordered = list(unique)
            index = {target:i for i,target in enumerate(ordered)}
            esm = embeddings[name]([unique[target]['sequence'] for target in ordered], length)
            esm = esm[torch.tensor([index[r['id']] for r,_ in requests], device='cuda')]
            rest = sequence_noise_batch(requests, length, seed=config['seed'], decoder_scale=decoder.fm.scale_ref)
            return infer(model, decoder, (esm,*rest), SampleConfig(steps=variant['steps'], guidance=2),
                flow_precision=variant['head'], decoder_precision='fp32',
                conditioning_ids=[r['id'] for r,_ in requests] if variant['reuse'] else None)

        def work_guard():
            if time.monotonic()-started > config['work_cap_seconds']:
                raise TimeoutError('work cap reached; no batch-size fallback')

        for name,variant in VARIANTS.items():
            directory = args.output/name
            directory.mkdir()
            child = dict(status='running', model=name, source=str(args.source), completed_predictions=0,
                config=dict(config, flow_steps=[variant['steps']], reuse_sample_conditioning=variant['reuse']),
                precision=dict(embedding=variant['embedding'], head=variant['head'], decoder='fp32'),
                controls=[], batches=[], timing_scope=manifest['timing_scope'],
                **{key:manifest[key] for key in ('dataset','checkpoint','decoder_checkpoint','embedding_artifacts')})
            children[name] = child
            for length,requests in buckets.items():
                work_guard()
                count = batches[length]
                chunk = requests[:count-3]+requests[-3:] if len(requests)>count else requests
                z,ca,backbone = predict(chunk, length, name)
                whole = ca.float().cpu().numpy()
                del z,ca,backbone
                for i in (0,len(chunk)-3):
                    r,k = chunk[i]
                    n = len(r['sequence'])
                    z,ca,backbone = predict([(r,k)], n, name)
                    alone = ca[0].float().cpu().numpy()
                    del z,ca,backbone
                    metrics = ca_metrics(whole[i,:n], alone)
                    delta = abs(ca_metrics(whole[i,:n], r['ca'].numpy())['ca_lddt']-ca_metrics(alone, r['ca'].numpy())['ca_lddt'])
                    control = dict(target_id=r['id'], bucket=length, batch=len(chunk), reference_ca_lddt_absolute_change=delta, **metrics)
                    child['controls'].append(control)
                    atomic_json(directory/'manifest.json', child)
                    print('control', name, json.dumps(control), flush=True)
                    if metrics['ca_rmsd']>.2 or metrics['ca_lddt']<.99 or delta>.005:
                        raise ValueError(name+' online batch/padding control failed')
                tail = len(requests)%count
                if tail:
                    warm = predict(requests[-tail:], length, name)
                    del warm
            torch.cuda.synchronize()
        manifest['setup_and_controls_seconds'] = time.monotonic()-started
        atomic_json(args.output/'manifest.json', manifest)
        scorers = ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context('spawn'))
        futures = {}
        first_fingerprints = {}
        first_choices = {}
        for repetition,order in enumerate(ORDER):
            for name in order:
                directory = args.output/name
                child = children[name]
                setting = f"steps{VARIANTS[name]['steps']}_cfg2"
                pass_record = dict(variant=name, repeat=repetition, batches=[], choices={}, fingerprints=[], status='running')
                manifest['passes'].append(pass_record)
                payloads = []
                output = h5py.File(directory/'predictions.h5', 'x') if repetition==0 else None
                try:
                    for length,requests in buckets.items():
                        for offset in range(0,len(requests),batches[length]):
                            work_guard()
                            chunk = requests[offset:offset+batches[length]]
                            identities = [(r['id'],k) for r,k in chunk]
                            lengths = [len(r['sequence']) for r,_ in chunk]
                            torch.cuda.synchronize()
                            torch.cuda.reset_peak_memory_stats()
                            nvtx = f'collect::matched::{name}::rep{repetition}::{length}::{offset}'
                            torch.cuda.nvtx.range_push(nvtx)
                            tick = time.monotonic()
                            try:
                                z,ca,backbone = predict(chunk, length, name)
                                z,ca,backbone = [x.float().cpu().numpy() for x in (z,ca,backbone)]
                                select_tick = time.monotonic()
                                choices = select_trios(identities, lengths, ca)
                                selection_seconds = time.monotonic()-select_tick
                                torch.cuda.synchronize()
                                seconds = time.monotonic()-tick
                            finally:
                                torch.cuda.nvtx.range_pop()
                            if set(choices)&set(pass_record['choices']):
                                raise ValueError('duplicate target across timed batches')
                            pass_record['choices'].update(choices)
                            pass_record['fingerprints'].append(fingerprint(identities, (z,ca,backbone)))
                            batch = dict(nvtx_range=nvtx, length=length, batch=len(chunk), proteins=len(chunk)//3,
                                seconds=seconds, selection_seconds=selection_seconds,
                                peak_allocated_bytes=torch.cuda.max_memory_allocated(), peak_reserved_bytes=torch.cuda.max_memory_reserved())
                            pass_record['batches'].append(batch)
                            if output is not None:
                                write_batch(output, setting, chunk, z,ca,backbone)
                                payloads.extend((setting,r['id'],k,ca[i,:n].copy(),r['ca'].numpy(),backbone[i,:n].copy(),str(args.usalign.resolve())) for i,((r,k),n) in enumerate(zip(chunk,lengths)))
                                child['completed_predictions'] += len(chunk)
                                child['batches'].append(batch)
                                atomic_json(directory/'manifest.json', child)
                            atomic_json(args.output/'manifest.json', manifest)
                    if set(pass_record['choices']) != set(ids):
                        raise ValueError('incomplete timed selection coverage')
                    if repetition==0:
                        first_fingerprints[name] = pass_record['fingerprints']
                        first_choices[name] = pass_record['choices']
                        atomic_json(directory/'choices.json', dict(rule='CA-lDDT medoid of three; native-free',
                            protocol_sha256=config['protocol_sha256'], choices=pass_record['choices'], fingerprints=pass_record['fingerprints']))
                        # Native scoring is submitted only after every choice has been frozen.
                        futures[name] = scorers.submit(score_batch, payloads)
                    pass_record['identical_to_first'] = (pass_record['fingerprints']==first_fingerprints[name] and pass_record['choices']==first_choices[name])
                    pass_record['status'] = 'complete'
                    print('timed pass',name,repetition,sum(b['seconds'] for b in pass_record['batches']), 'identical',pass_record['identical_to_first'],flush=True)
                    atomic_json(args.output/'manifest.json', manifest)
                finally:
                    if output is not None:
                        output.close()
        for name,future in futures.items():
            rows = future.result()
            if len(rows)!=3*len(ids) or {(r['target_id'],r['sample']) for r in rows}!={(n,k) for n in ids for k in range(3)}:
                raise ValueError('incomplete first-pass scores')
            child = children[name]
            write_scores(args.output/name, child, rows, time.monotonic()-started, str(args.usalign.resolve()), 'first-pass CPU scoring after native-free choices were frozen')
            child['status'] = 'complete'
            atomic_json(args.output/name/'manifest.json', child)
        manifest['status'] = 'complete'
    except BaseException as error:
        manifest.update(status='failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        if scorers:
            scorers.shutdown(wait=True, cancel_futures=True)
        if telemetry:
            telemetry.close()
        manifest['elapsed_seconds'] = time.monotonic()-started
        atomic_json(args.output/'manifest.json', manifest)


if __name__ == '__main__':
    main()
