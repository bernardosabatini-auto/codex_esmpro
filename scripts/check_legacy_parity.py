"""Compare extracted architectures against isolated legacy definitions on CPU.

Only selected class/function AST nodes are evaluated. No old module imports,
top-level statements, trainers, file writes, CUDA setup, or compilation execute.
"""
import argparse
import ast
import json
import math
import os
from pathlib import Path
from types import SimpleNamespace
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint
from latentfold.model import LatentFlowNet
from latentfold.pair_model import PairFlowNet


def definitions(path, names, namespace):
    tree = ast.parse(path.read_text())
    selected = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    if {n.name for n in selected} != set(names):
        raise ValueError("missing legacy definitions")
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(2)
    os.environ["PAIR_COMPILE"] = "0"
    os.environ["PAIR_CKPT"] = "0"
    ns = dict(torch=torch, nn=nn, F=F, math=math, os=os, checkpoint=checkpoint,
              D_LAT=8, D_ESM=1280, MAX_LEN=16, DIT_COMPILE=False,
              G7=SimpleNamespace(DIT_COMPILE=False))
    definitions(args.source / "code/gate7_latent_flow.py",
                ["timestep_embedding", "Attention", "DiTBlock", "LatentFlowNet"], ns)
    definitions(args.source / "code/gate10_pair_flow.py",
                ["PairAttention", "PairDiTBlock", "TriangleMultiply", "TriangleMultiplyFused", "PairBlock", "PairTrack", "PairFlowNet"], ns)
    result = {}
    for name, cls in (("LatentFlowNet", LatentFlowNet), ("PairFlowNet", PairFlowNet)):
        torch.manual_seed(81)
        kwargs = dict(d_model=32, n_layers=2, n_heads=4, d_cond=12)
        if name == "PairFlowNet":
            kwargs.update(d_pair=8, n_pair_blocks=1, pair_fused=True)
        legacy, current = ns[name](**kwargs).eval(), cls(**kwargs, max_len=16).eval()
        with torch.no_grad():
            for parameter in legacy.parameters():
                parameter.normal_(0, 0.1)
        current.load_state_dict(legacy.state_dict(), strict=True)
        x, esm, sc = torch.randn(2, 8, 8), torch.randn(2, 8, 12), torch.randn(2, 8, 8)
        mask = torch.arange(8)[None] < torch.tensor([5, 8])[:, None]
        t = torch.tensor([0.3, 0.7])
        drop = torch.tensor([True, False])
        with torch.no_grad():
            old = legacy(x, t, esm, mask, drop, sc)
            new = current(x, t, esm, mask, drop, sc)
        torch.testing.assert_close(old, new, rtol=0, atol=0)
        result[name] = {"state_keys": len(current.state_dict()), "max_absolute_difference": float((old-new).abs().max()),
                        "device": "cpu", "small_test_architecture": kwargs}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
