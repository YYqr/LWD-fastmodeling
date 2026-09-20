# lhlwdem

## lwdfast binary distribution

The empymod-derived files `scripts/__init__.py`, `scripts/fdesign.py`, and
`scripts/tmtemod.py` are also distributed as compiled extensions in the
lwdfast Windows release. Copyright 2016 The emsig community. These modules
remain under the Apache License 2.0; the accompanying LICENSE and NOTICE
apply to their binary form as well. Their development sources retain the
original attribution headers. The local DLF coefficient tables are embedded
in the compiled forward_model module during the binary build.

`lhlwdem` is a project-local derivative of `empymod` 2.5.1, copied for the
LWD electromagnetic forward-model workflow and renamed to avoid importing the
environment-installed package accidentally.

Upstream project: https://github.com/emsig/empymod

Copyright remains with the emsig community and other upstream contributors.
The copied source is distributed under the Apache License 2.0; see `LICENSE`
and `NOTICE` in this directory. Local modifications must retain those files
and this provenance statement.

The local derivative also contains an optional C++17/OpenMP backend under
`lhlwdem/cpp`. It accelerates selected numerical kernels while retaining the
NumPy/Numba implementations as correctness references and runtime fallbacks.

The `lhlwdem._recovered_curve` backend is the project-local paired moving-tool
solver recovered and validated in `lwd_reverse`.  It provides
`lhlwdem.magnetic_components_curve`: source and receiver rows are paired
one-to-one, modal/reflection terms are reused by layer pair, and no quadratic
source/receiver Cartesian product is formed.  The recovered 120/140-point DLF
tables and TE/TM implementation are stored inside this package so callers do
not depend on the comparison-project directory at runtime.

## Project-reference compatibility

The magnetic-source `loop` path is regression-tested against the project
reference package at `1_exe_kill/cnooc_DR_LWD/lwdempy`.  Validation uses
five-parameter infinitesimal source/receiver inputs, for which both packages
evaluate a unit point magnetic source and a point magnetic receiver
(`msrc=True`, `mrec=True` internally).  The published nominal 0 degree curve
follows the legacy ACPRem convention: it is evaluated at 0.1 degree with a
1e-6 m minimum horizontal offset to avoid the old zero-offset singularity.

Production point-source workflows call `lhlwdem.magnetic_dipole` explicitly.
This fast entry point accepts only five-entry infinitesimal source/receiver
coordinates and delegates to the C++/OpenMP-accelerated magnetic loop kernel;
six-entry finite segments remain available through `loop` and `bipole` for
geometry studies, but cannot be selected accidentally by the fast API.
