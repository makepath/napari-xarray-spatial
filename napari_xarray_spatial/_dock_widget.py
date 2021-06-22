"""
This module is an example of a barebones QWidget plugin for napari

It implements the ``napari_experimental_provide_dock_widget`` hook specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs.
"""
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox
from xrspatial.multispectral import ndvi, arvi

AVAILABLE_FUNCS = ['ndvi', 'arvi']

class MultispectralFunctions(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.func_dropdown = QComboBox(self)
        self.func_dropdown.addItems(['ndvi', 'arvi'])
        self.func_dropdown.currentIndexChanged.connect(self.selectionchange)


        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.func_dropdown)

    def selectionchange(self, i):
        print(f"Selected option #{i}, {self.func_dropdown.currentText}")



@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return [MultispectralFunctions]
