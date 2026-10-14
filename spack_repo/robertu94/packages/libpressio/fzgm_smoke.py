"""Run inside the activated Spack environment on a CUDA GPU."""
import numpy as np
import libpressio as lp

builder = getattr(lp, "FZGPUModulesChain", None)
if builder is None:
    from fzgm_helper import Chain as builder

x = np.sin(np.arange(131, dtype=np.float32))
for policy in ("off", "auto"):
    comp = (builder().add("quantizer:float:uint32", linear_mode=True)
        .add("lorenzo:int32", from_port="codes", block_size=32)
        .add("adaptive_bitpack:int32", block_size=32)
        .configure(memory_strategy="preallocate", specialization=policy)
        .compressor(eb=1e-3))
    encoded = comp.encode(x)
    forward = comp.get_metrics()["fzgpumodules:specialization_forward_groups"]
    if hasattr(lp, "FZGPUModulesChain"):
        dec = lp.PressioCompressor.from_config({"compressor_id": "fzgpumodules",
            "compressor_config": {"fzgpumodules:memory_strategy": "preallocate",
                                  "fzgpumodules:specialization": policy}})
        y = dec.decode(encoded)
    else:
        dec = comp
        y = comp.decode(encoded, np.empty_like(x))
    inverse = dec.get_metrics()["fzgpumodules:specialization_inverse_groups"]
    error = float(np.max(np.abs(x-y)))
    assert y.shape == x.shape and y.dtype == x.dtype and np.isfinite(y).all()
    assert error <= 1e-3 + 1e-6
    assert forward == inverse == (1 if policy == "auto" else 0)
    print(f"{policy}: max_error={error:.8g}, specialization={forward}/{inverse}")
