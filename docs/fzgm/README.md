# Reproducible FZGPUModules installations

The `fzgpumodules@2.0.0` recipe uses the published release source tarball and its
SHA-256 checksum. It does not follow `main`. The obsolete moving `2.0` and `1.0`
recipe entries have been removed; the old `refactor` branch is no longer available.

Two libpressio snapshots are explicitly paired with compatible SDKs:

| libpressio version | FZGM SDK | Interface |
| --- | --- | --- |
| `develop-fzgm-v2` | `2.0.0` release | Verified original v2 integration; `fzgm_helper.Chain`; same-instance decoding |
| `develop-fzgm-support` | `archive-support` pinned commit | `libpressio.FZGPUModulesChain`; independent archive decoding |

The snapshots are development integrations, not upstream libpressio releases.
The support pair pins libpressio `41d44c72114e15ef7868a462bce2893a3c51fb40`
and stable-main FZGM `8f73a3988a2e1efd3192850c192f489e253a1a2e`.
This SDK contains the stable module catalog plus the unreleased `fromHeader()` API;
it must not be described as the v2.0.0 release.
Both source revisions are fixed commits. Use the release row when reproducing
v2.0.0 behavior; use the support row for the new Python API and save/load workflow.

## Install

Add this repository using a Spack installation that supports its v2 repository
layout, then create an environment. The templates use SM90 for H100; set
`cuda_arch=80` for A100 before concretizing.

```bash
source /path/to/spack/share/spack/setup-env.sh
cd /path/to/spack_packages
spack repo add /path/to/spack_packages/spack_repo/robertu94
spack env create -d ./fzgm-python docs/fzgm/spack-support.yaml
spack env activate ./fzgm-python
spack concretize
spack install -j8
python spack_repo/robertu94/packages/libpressio/fzgm_smoke.py
```

For the released SDK, substitute `spack-v2.yaml`. For SDK-only installation:

```bash
spack install fzgpumodules@2.0.0 +cuda cuda_arch=80
```

Keep the generated `spack.lock` together with the package repository commit and
Spack/builtin repository revisions. The lock captures exact dependency versions,
variants, compiler, and architecture; changing the target machine may require
reconcretization. The templates pin application revisions, CUDA, Python, NumPy,
numcodecs, and SWIG; they do not promise identical binaries on every platform.

## Python and GPU checks

The FZGM Python recipe supplies NumPy and numcodecs and selects the same Python
interpreter for compilation and installation. A patch restricted to FZGM Python
builds uses SWIG's portable output macro and Python 3 type checks so modern SWIG
runtime signatures work.
No global libpressio wrapper changes are required by this packaging patch.
CUDA and `cuda_arch` propagate to the SDK. Incompatible SDK selections and
`+fzgpumodules~cuda` are rejected during concretization.

The smoke test requires a CUDA GPU. It checks an error-bounded partial-block
round trip with specialization Off and Auto. For the support snapshot it also
checks a fresh decoder restores dtype/shape without a chain or output allocation.
Use `spack test run libpressio` for the package's installed tests.

The minimal environment contains neither notebook software nor SDRBench.
Those demo dependencies can be added separately after the compression interface
passes its smoke test; dataset downloads should happen before demo timing.

## Validation

Both pinned pairs were installed through Spack on an H100 with CUDA 12.9.86,
GCC 13.3.0, Python 3.14.5, NumPy 2.5.2, numcodecs 0.16.5, and SWIG 4.5.0.
The Python Off/Auto smoke test passed for both pairs, including fresh-decoder
reconstruction for the support snapshot. The refreshed support pair also passed
the installed native/Python package tests, six archive tests (including
cross-process decoding), and the Off/Auto smoke test under Compute Sanitizer
memcheck with zero errors. Incompatible SDK and missing-CUDA
specifications were rejected by the concretizer. The ordinary non-FZGM
libpressio specification still selects the upstream 1.0.6 release.

Testing on this machine does not establish A100 performance or compatibility
with every Python/SWIG combination. The generated lockfiles are retained with
the local validation records; generate a lock for the intended demo machine.
