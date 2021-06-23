import inspect
import toolz as tz
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QLabel
import xarray
from xrspatial.multispectral import (
    arvi,
    ebbi,
    evi,
    gci,
    nbr,
    nbr2,
    ndmi,
    ndvi,
    savi,
    sipi
)

AVAILABLE_FUNCS = {
    'arvi':  arvi,
    'ebbi':  ebbi,
    'evi' :  evi ,
    'gci' :  gci ,
    'nbr' :  nbr ,
    'nbr2':  nbr2,
    'ndmi':  ndmi,
    'ndvi':  ndvi,
    'savi':  savi,
    'sipi':  sipi,
}

class MultispectralFunctions(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.func_dropdown = QComboBox(self)
        self.func_dropdown.addItems(list(AVAILABLE_FUNCS.keys()))
        self.func_dropdown.currentIndexChanged.connect(self.selectionchange)


        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.func_dropdown)

        self.params = QWidget()
        self.run_btn = QPushButton("Run", self)
        self.run_btn.clicked.connect(self.on_click)

        self.params.setLayout(QVBoxLayout())
        self.params.layout().addWidget(self.run_btn)
        
        self.layout().addWidget(self.params)
        
    def selectionchange(self, i):
        self.clear_layout(self.params.layout())
        current_func = AVAILABLE_FUNCS[self.func_dropdown.currentText()]
        current_func_params = inspect.signature(current_func).parameters
        layer_params = []
        for param_name, param in current_func_params.items():
            if param.annotation is not param.empty and\
                param.annotation is xarray.core.dataarray.DataArray:
                layer_params.append(param_name)

        if layer_params:
            combos = {}
            for layer_name in layer_params:
                new_combo = self.add_layer_selection(layer_name)
                combos[layer_name] = new_combo

            run_btn = QPushButton('Compute Layer', self)
            run_func = compute_func_on_layers(layer_selection_combo=combos, func=current_func, viewer=self.viewer)
            run_btn.clicked.connect(run_func)
            self.params.layout().addWidget(run_btn)

        else:
            raise TypeError("Function {current_func} does not take any xarray.DataArray parameters.")

    def on_click(self, e):
        print(f"Clicked and current selection is {self.func_dropdown.currentText()}")
        new_label = QLabel(self)
        new_label.setText(self.func_dropdown.currentText())
        self.params.layout().addWidget(new_label)


    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    
    def add_layer_selection(self, layer_name):
        layer_row = QWidget()
        layer_row.setLayout(QHBoxLayout())
        
        layer_label = QLabel(self)
        layer_label.setText(layer_name)

        layer_combo = QComboBox(self)
        layer_combo.addItems([layer.name for layer in self.viewer.layers])
        
        layer_row.layout().addWidget(layer_label)
        layer_row.layout().addWidget(layer_combo)
        self.params.layout().addWidget(layer_row)

        return layer_combo

@tz.curry
def compute_func_on_layers(e, *args, layer_selection_combo, func, viewer):
    print(f"Computing {func}!")
    x_arr_args = {}
    for arg_name, combo in layer_selection_combo.items():
        layer_name = combo.currentText()
        given_layer_data = viewer.layers[layer_name].data
        if len(given_layer_data.shape) != 2:
            raise ValueError(f"{func} can only be applied to 2D data, but {layer_name} is of shape {given_layer_data.shape}")
        else:
            x_arr_args[arg_name] = xarray.DataArray(given_layer_data)
    computed_layer_data = func(**x_arr_args)
    viewer.add_image(computed_layer_data, name=func.__name__)


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return [MultispectralFunctions]
