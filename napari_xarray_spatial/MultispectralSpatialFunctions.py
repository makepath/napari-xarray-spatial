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
    """This widget handles setting up and populating the GUI layout with
    the available functions, and their parameters once a function is selected.
    """
    def __init__(self, napari_viewer):
        """Initializes the widget with the required layouts, buttons and selection
        tools

        # this QWidget.__init__ requests the napari viewer instance. 
        # This can be done in one of two ways:
        # 1. use a parameter called `napari_viewer`, as done here
        # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
        """
        super().__init__()
        self.viewer = napari_viewer

        # dropdown will hold all the available functions
        self.func_dropdown = QComboBox(self)
        self.func_dropdown.addItems(list(AVAILABLE_FUNCS.keys()))
        # when the index changes, the selectionchange callback handles
        # showing the correct parameters
        self.func_dropdown.currentIndexChanged.connect(self.selectionchange)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.func_dropdown)

        # the params widget will hold all the parameters for the chosen function
        self.params = QWidget()
        self.params.setLayout(QVBoxLayout())

        self.run_btn = QPushButton("Compute Layer", self)
        self.params.layout().addWidget(self.run_btn)

        self.layout().addWidget(self.params)
        self.selectionchange(0)
        
    def selectionchange(self, i):
        """Inspects parameters of function currently selected and 
        adds a dropdown for each one, with all napari layers as options

        Parameters
        ----------
        i : int
            Index currently selected

        Raises
        ------
        TypeError
            if the chosen function takes no xarray.DataArray parameters
        """
        # empty current selection
        self.clear_layout(self.params.layout())
        
        # inspect the function for its parameters, and only keep ones annotated
        # with xarray.DataArray
        current_func = AVAILABLE_FUNCS[self.func_dropdown.currentText()]
        current_func_params = inspect.signature(current_func).parameters
        layer_params = []
        for param_name, param in current_func_params.items():
            if param.annotation is not param.empty and\
                param.annotation is xarray.core.dataarray.DataArray:
                layer_params.append(param_name)

        # if we have any xarray parameters, build a new combo box for them
        if layer_params:
            combos = {}
            for layer_name in layer_params:
                new_combo = self.add_layer_selection(layer_name)
                combos[layer_name] = new_combo

            run_btn = QPushButton('Compute Layer', self)
            # we curry the callback function with the combo box, current function and viewer, so that
            # we can see what the user has chosen when they click "Compute Layer"
            run_func = compute_func_on_layers(layer_selection_combo=combos, func=current_func, viewer=self.viewer)
            run_btn.clicked.connect(run_func)
            self.params.layout().addWidget(run_btn)
            self.run_btn = run_btn

        else:
            raise TypeError("Function {current_func} does not take any xarray.DataArray parameters.")

    def clear_layout(self, layout):
        """Removes all widgets from the given layout

        Parameters
        ----------
        layout : QLayout
            Layout containing 0 or more widgets for deletion
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    
    def add_layer_selection(self, combo_label):
        """Adds combo box with all napari layers, labelled with given
        combo_label

        Parameters
        ----------
        combo_label : str
            label for this new combo box

        Returns
        -------
        QComboBox
            newly created combo box
        """
        layer_row = QWidget()
        layer_row.setLayout(QHBoxLayout())
        
        layer_label = QLabel(self)
        layer_label.setText(combo_label)

        layer_combo = QComboBox(self)
        layer_combo.addItems([layer.name for layer in self.viewer.layers])
        
        layer_row.layout().addWidget(layer_label)
        layer_row.layout().addWidget(layer_combo)
        self.params.layout().addWidget(layer_row)

        return layer_combo

@tz.curry
def compute_func_on_layers(e, *args, layer_selection_combo, func, viewer):
    """Compute given func on layers selected in layer_selection_combo and 
    add return value to viewer

    Parameters
    ----------
    e : event
        the button click event (given by Qt)
    layer_selection_combo : Dict[str, QComboBox]
        dictionary of argument name to QComboBox for selecting layers
    func : function
        function to run on the selected layers
    viewer : napari Viewer
        the napari viewer to add image to

    Raises
    ------
    ValueError
        if any of the layer data is not 2D
    """
    x_arr_args = {}
    for arg_name, combo in layer_selection_combo.items():
        layer_name = combo.currentText()
        # each layer is a layer object - its underlying data (whether it be numpy, dask, etc.) is always at layer.data
        given_layer_data = viewer.layers[layer_name].data
        if len(given_layer_data.shape) != 2:
            raise ValueError(f"{func} can only be applied to 2D data, but {layer_name} is of shape {given_layer_data.shape}")
        else:
            x_arr_args[arg_name] = xarray.DataArray(given_layer_data)
    computed_layer_data = func(**x_arr_args)
    viewer.add_image(computed_layer_data, name=func.__name__)


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # this is where napari looks to find your widget(s). You can return a list of widgets if desired.
    return MultispectralFunctions
