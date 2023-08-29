from omlt.dependencies import (
    onnx_available,
    keras_available,
    torch_available,
    torch_geometric_available,
)

if onnx_available:
    from omlt.io.onnx import (
        load_onnx_neural_network,
        load_onnx_neural_network_with_bounds,
        write_onnx_model_with_bounds,
    )

if keras_available:
    from omlt.io.keras import load_keras_sequential

if torch_available and torch_geometric_available:
    from omlt.io.torch_geometric import (
        load_torch_geometric_sequential,
        gnn_with_fixed_graph,
        gnn_with_non_fixed_graph,
    )
