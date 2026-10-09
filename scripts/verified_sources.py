"""Reuse content verification only within one audit, with immutable file identities."""
import hashlib
from pathlib import Path
from context_flow_generation import identity


class VerifiedSources:
    def __init__(self):self.checked={}

    def verify(self,row):
        path=str(Path(row['path']).resolve());before=identity(path)
        if path in self.checked:
            old,digest=self.checked[path]
            if before!=old:raise ValueError('Source changed during audit: '+path)
        else:
            h=hashlib.sha256()
            with Path(path).open('rb') as f:
                while block:=f.read(8*1024*1024):h.update(block)
            digest=h.hexdigest()
            if identity(path)!=before:raise ValueError('Source changed while hashing: '+path)
            self.checked[path]=(before,digest)
        if digest!=row['sha256']:raise ValueError('Source checksum mismatch: '+path)
