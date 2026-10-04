"""Bounded CPU work overlapped with GPU inference, preserving record order."""
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import time


class OrderedCPUScoring:
    def __init__(self, enabled, limit=4):
        if type(enabled) is not bool or limit<1:raise ValueError('Invalid CPU scoring schedule')
        self.pool=ThreadPoolExecutor(max_workers=1) if enabled else None
        self.pending=deque();self.limit=limit;self.wait_seconds=0.

    def submit(self, function, *args):
        if self.pool is None:
            return [function(*args)]
        self.pending.append(self.pool.submit(function,*args))
        return self.drain(wait=len(self.pending)>=self.limit,one=True)

    def drain(self, *, wait=False, one=False):
        rows=[]
        while self.pending:
            future=self.pending[0]
            if not wait and not future.done():break
            start=time.monotonic();value=future.result();self.wait_seconds+=time.monotonic()-start
            self.pending.popleft();rows.append(value)
            if one:break
        return rows

    def close(self):
        if self.pool:self.pool.shutdown(wait=True,cancel_futures=True)
