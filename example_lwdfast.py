"""Run a three-layer multicomponent LWD forward-model example."""

import os
from pathlib import Path
import tempfile
from time import perf_counter

import numpy as np

# Keep Numba's cache path short even when the package lives in a deep folder.
os.environ.setdefault('NUMBA_CACHE_DIR', str(Path(tempfile.gettempdir()) / 'lwdfast-numba'))

import lwdfast


def main():
    # Interface depths (m), horizontal/vertical resistivities (ohm m).
    interfaces = np.array([3.81, 5.94])
    rho_h = np.array([80.0, 1.0, 10.0])
    rho_v = np.array([80.0, 100.0, 10.0])
    anisotropy = np.sqrt(rho_v / rho_h)

    # Tool inclination measured from vertical; rows are local x/y/z axes.
    inclination_deg = 60.0
    angle = np.deg2rad(inclination_deg - 90.0)
    tool_basis = np.array([
        [-np.sin(angle), 0.0, np.cos(angle)],
        [0.0, 1.0, 0.0],
        [np.cos(angle), 0.0, np.sin(angle)],
    ])
    depths = np.linspace(2.5, 7.0, 2000)
    sources = np.column_stack((np.zeros_like(depths), np.zeros_like(depths), depths))
    receivers = sources - 0.4 * tool_basis[2]  # 0.4 m source-receiver spacing.

    parameters = dict(
        src_centers=sources,
        rec_centers=receivers,
        basis=tool_basis,
        depth=interfaces,
        res=rho_h,
        aniso=anisotropy,
        freqtime=25_000.0,
        strength=1.0,
        mrec=True,
        chunk_size=64,
        workers=4,
    )

    # Submit the entire curve once to initialize the solver and populate caches.
    # The timed calls reuse exactly the same model, geometry and frequency.
    lwdfast.clear_curve_cache()
    warm_start = perf_counter()
    reference = lwdfast.magnetic_components_curve(**parameters)
    warm_seconds = perf_counter() - warm_start

    # Keep numerical caches between calls. Time only the forward calculation.
    elapsed = []
    for _ in range(5):
        start = perf_counter()
        response = lwdfast.magnetic_components_curve(**parameters)
        elapsed.append(perf_counter() - start)
        for name in reference:
            np.testing.assert_allclose(response[name], reference[name],
                                       rtol=1e-10, atol=1e-13)
    median_seconds = float(np.median(elapsed))

    print(f"Package: {lwdfast.__file__}")
    print(f"Curve backend: {lwdfast.fast.__file__}")
    print(f"Frequency: 25000 Hz; depth samples: {depths.size}")
    print(f"Batch size: {depths.size}; chunk_size: 64; workers: 4")
    print(f"Warm-up (excluded from hot-cache timing): {warm_seconds:.6f} s")
    print("Hot-cache runs (s): " + ", ".join(f"{value:.6f}" for value in elapsed))
    print(f"Hot-cache median: {median_seconds:.6f} s; "
          f"throughput: {depths.size / median_seconds:,.0f} points/s; "
          f"average: {1000 * median_seconds / depths.size:.6f} ms/point")
    print("Hot-cache timing reuses the same curve; new models/positions may be slower.")
    for name in ('Hxx', 'Hyy', 'Hzz', 'Hxz', 'Hzx'):
        values = np.asarray(response[name])
        if values.shape != depths.shape or not np.all(np.isfinite(values)):
            raise RuntimeError(f"Unexpected {name} response: {values.shape}")
        print(f"{name}: shape={values.shape}; first three values (A/m): {values[:3]}")
    return depths, response


if __name__ == '__main__':
    main()
