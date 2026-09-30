# Backward profile

Status: failed

Profile draws are all conditioned, late time, and self-conditioned; capacity stress rather than representative training. Adam state and optimizer arithmetic are included; learning rate zero preserves checkpoint weights.

Failure: OutOfMemoryError: CUDA out of memory. Tried to allocate 512.00 MiB. GPU 0 has a total capacity of 139.79 GiB of which 20.59 GiB is free. Including non-PyTorch memory, this process has 119.20 GiB memory in use. 118.82 GiB allowed; Of the allocated memory 117.83 GiB is allocated by PyTorch, and 640.95 MiB is reserved by PyTorch but unallocated. If reserved but unallocated memory is large try setting PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True to avoid fragmentation.  See documentation for Memory Management  (https://docs.pytorch.org/docs/stable/notes/cuda.html#optimizing-memory-usage-with-pytorch-cuda-alloc-conf)
