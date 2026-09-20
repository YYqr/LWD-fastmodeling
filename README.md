# lwdfast

Efficient Forward Modeling for Multicomponent Logging-While-Drilling Electromagnetic Responses

## Overview

`lwdfast` computes frequency-domain electromagnetic responses for
logging-while-drilling (LWD) tools in horizontally layered formations,
including vertically transversely isotropic (VTI) media.

The main features are:

- Five complex magnetic-field components: `Hxx`, `Hyy`, `Hzz`, `Hxz`, and `Hzx`.
- User-defined layer interfaces, horizontal resistivity, and anisotropy
  (`sqrt(vertical resistivity / horizontal resistivity)`).
- Configurable source and receiver positions, tool orientation, frequency,
  and source strength.
- Paired source-receiver evaluation for individual measurement points or
  complete logging curves.
- Batch processing, configurable worker threads, and reuse of numerical
  caches for repeated calculations.

The curve interface returns a dictionary of complex response arrays, one
for each requested component. With `mrec=True`, the responses are magnetic
fields in A/m. Coordinates and layer depths are specified in metres,
resistivity in ohm metres, and frequency in hertz.

## Runtime environment

The supplied release is intended for:

- Windows x64.
- CPython 3.12 (64-bit).
- NumPy, SciPy, Numba, libdlf, and scooby.
- Microsoft Visual C++ Redistributable for x64.

Install the Python dependencies in your Python 3.12 environment:

```powershell
python -m pip install numpy scipy numba libdlf scooby
```

Keep the following files and folder together:

```text
README.md
example_lwdfast.py
lwdfast/
```

Place the `lwdfast` folder beside your calling program, or add its parent
directory to `PYTHONPATH`.

## Usage example

Run the included example:

```powershell
python example_lwdfast.py
```

The example defines a three-layer anisotropic formation, a tool inclination
of 60 degrees, and a source-receiver spacing of 0.4 m. It evaluates all five
components at 25 kHz for 2,000 depth samples in one batch.

The central call is:

```python
import lwdfast

response = lwdfast.magnetic_components_curve(
    src_centers=sources,       # Source coordinates, shape (N, 3), in metres.
    rec_centers=receivers,     # Paired receiver coordinates, shape (N, 3).
    basis=tool_basis,          # Tool x/y/z axes as rows of a (3, 3) array.
    depth=interfaces,         # N_layers - 1 interface depths, in metres.
    res=rho_h,                # Horizontal resistivity for each layer.
    aniso=anisotropy,         # sqrt(rho_v / rho_h) for each layer.
    freqtime=25_000.0,         # One frequency, in hertz.
    strength=1.0,
    mrec=True,
    chunk_size=64,
    workers=4,
)

hxx = response["Hxx"]
hzz = response["Hzz"]
```

See `example_lwdfast.py` for the complete model, geometry, and tool-basis
arrays. Each source row is paired with the corresponding receiver row.
`chunk_size` controls the number of points per block, and `workers` controls
how many blocks can be evaluated concurrently. Set `workers=1` for serial
block evaluation.

## Timing repeated calculations

In a local benchmark, batch evaluation with hot caches and four worker
threads achieved approximately **33,623 points per second**, computing all
five components at each point. For the 2,000-point example, the median of
five timed runs was approximately **0.0595 seconds**, after one complete
warm-up call. This is a measured result for the tested machine and model;
performance varies with hardware and calculation parameters.

The example clears the curve caches and evaluates the complete curve once
to warm up the solver. It then repeats the same calculation five times
without clearing the caches between calls.

It prints the warm-up time, all five hot-cache timings, the median time,
throughput in points per second, average time per point, and the first
three complex responses for each component. Timing includes only the
forward-model calls; imports, geometry construction, result checks, and
printing are excluded.

Hot-cache throughput represents repeated evaluation of the same curve.
Changing the formation model, measurement positions, or frequency may
reduce cache reuse. Average time per point is derived from batch
throughput and is not the latency of an independent single-point call.

The example uses the system temporary directory for the Numba cache unless
`NUMBA_CACHE_DIR` is already set.

## Attribution

The package includes code derived from empymod. See `lwdfast/LICENSE`,
`lwdfast/NOTICE`, and `lwdfast/UPSTREAM.md` for licensing and attribution.
