class GradientBoostedTreeModel:
    def __init__(self, onnx_model, scaling_object=None, scaled_input_bounds=None):
        """
        Create a network definition object used to create the gradient-boosted trees
        formulation in Pyomo

        Args:
           onnx_model : ONNX Model
              An ONNX model that is generated by the ONNX convert function for
              lightgbm.
           scaling_object : ScalingInterface or None
              A scaling object to specify the scaling parameters for the
              tree ensemble inputs and outputs. If None, then no
              scaling is performed.
           scaled_input_bounds : dict or None
              A dict that contains the bounds on the scaled variables (the
              direct inputs to the tree ensemble). If None, then no bounds
              are specified or they are generated using unscaled bounds.
        """
        self.__model = onnx_model
        self.__n_inputs = _model_num_inputs(onnx_model)
        self.__n_outputs = _model_num_outputs(onnx_model)
        self.__scaling_object = scaling_object
        self.__scaled_input_bounds = scaled_input_bounds

    @property
    def onnx_model(self):
        """Returns underlying onnx model of the tree model being used"""
        return self.__model

    @property
    def n_inputs(self):
        """Returns the number of input variables"""
        return self.__n_inputs

    @property
    def n_outputs(self):
        """Returns the number of output variables"""
        return self.__n_outputs

    @property
    def scaling_object(self):
        """Return an instance of the scaling object that supports the ScalingInterface"""
        return self.__scaling_object

    @property
    def scaled_input_bounds(self):
        """Return a list of tuples containing lower and upper bounds of tree ensemble inputs"""
        return self.__scaled_input_bounds

    @scaling_object.setter
    def scaling_object(self, scaling_object):
        self.__scaling_object = scaling_object


def _model_num_inputs(model):
    """Returns the number of input variables"""
    graph = model.graph
    if len(graph.input) != 1:
        raise ValueError(f"Model graph input field is multi-valued {graph.input}. A single value is required.")
    return _tensor_size(graph.input[0])


def _model_num_outputs(model):
    """Returns the number of output variables"""
    graph = model.graph
    if len(graph.output) != 1:
        raise ValueError(f"Model graph output field is multi-valued {graph.output}. A single value is required.")
    return _tensor_size(graph.output[0])


def _tensor_size(tensor):
    """Returns the size of an input tensor"""
    tensor_type = tensor.type.tensor_type
    size = None
    dim_values = [dim.dim_value for dim in tensor_type.shape.dim if dim.dim_value is not None and dim.dim_value > 0]
    if len(dim_values) == 1:
        size = dim_values[0]
    elif dim_values == []:
        raise ValueError(f"Tensor {tensor} has no positive dimensions.")
    else:
        raise ValueError(f"Tensor {tensor} has multiple positive dimensions.")
    return size