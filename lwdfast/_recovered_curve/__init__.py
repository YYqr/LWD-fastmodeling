"""Independent executable-derived LWD forward-model package.

The public entry point combines recovered material/TE/TM recursion, distinct
120/140-point Hankel filters, Cartesian tensor assembly and tool projection.
The production path does not import lwdfast or lwdempy.
"""

from .forward_model import (
    BACKEND_DESCRIPTION, clear_curve_cache, magnetic_components,
    magnetic_components_curve,
)

__all__ = [
    "BACKEND_DESCRIPTION", "clear_curve_cache", "magnetic_components",
    "magnetic_components_curve",
]
