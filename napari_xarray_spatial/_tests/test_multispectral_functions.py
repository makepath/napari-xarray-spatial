from qtpy import QtCore
from napari_xarray_spatial.MultispectralSpatialFunctions import AVAILABLE_FUNCS, MultispectralFunctions
import napari_xarray_spatial
import pytest
from xrspatial.datasets import get_data

# this is your plugin name declared in your napari.plugins entry point
MY_PLUGIN_NAME = "napari-xarray-spatial"
# the name of your widget(s)
MY_WIDGET_NAME = "Multispectral Functions"


def test_something_with_viewer(make_napari_viewer, napari_plugin_manager):
    napari_plugin_manager.register(napari_xarray_spatial, name=MY_PLUGIN_NAME)
    viewer = make_napari_viewer()
    num_dw = len(viewer.window._dock_widgets)
    viewer.window.add_plugin_dock_widget(
        plugin_name=MY_PLUGIN_NAME, widget_name=MY_WIDGET_NAME
    )
    assert len(viewer.window._dock_widgets) == num_dw + 1

@pytest.mark.parametrize("func", AVAILABLE_FUNCS)
def test_multispectral_funcs(func, make_napari_viewer, qtbot):
    viewer = make_napari_viewer()

    data = get_data('sentinel-2')
    for var_name, band_xarray in data.items():
        viewer.add_image(band_xarray, name=var_name)

    num_layers = len(viewer.layers)
    ms_function_widget = MultispectralFunctions(viewer)
    qtbot.addWidget(ms_function_widget)
    index = ms_function_widget.func_dropdown.findText(func)
    if index >= 0:
         ms_function_widget.func_dropdown.setCurrentIndex(index)
    qtbot.mouseClick(ms_function_widget.run_btn, QtCore.Qt.LeftButton)

    assert len(viewer.layers) == num_layers + 1
    assert func in viewer.layers
