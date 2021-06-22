from typing import TYPE_CHECKING

from enum import Enum
import numpy as np
from napari_plugin_engine import napari_hook_implementation
from xrspatial.multispectral import ndvi, arvi

if TYPE_CHECKING:
    import napari


@napari_hook_implementation
def napari_experimental_provide_function():
    return [image_arithmetic]


# using Enums is a good way to get a dropdown menu.  Used here to select from np functions
class Operation(Enum):
    ndvi = ndvi
    arvi = arvi


def image_arithmetic(
    layerA: "napari.types.ImageData", operation: Operation, layerB: "napari.types.ImageData"
) -> "napari.types.LayerDataTuple":
    """Adds, subtracts, multiplies, or divides two same-shaped image layers."""
    return (operation.value(layerA, layerB), {"colormap": "turbo"})
