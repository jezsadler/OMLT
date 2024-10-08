import numpy as np
import pyomo.environ as pyo
import pytest
from omlt.dependencies import keras, keras_available
from pyomo.common.dependencies import DeferredImportError

if keras_available:
    from omlt.io import load_keras_sequential

from conftest import get_neural_network_data
from omlt import OmltBlock
from omlt.neuralnet import FullSpaceNNFormulation, ReducedSpaceNNFormulation
from omlt.neuralnet.activations import ComplementarityReLUActivation
from omlt.scaling import OffsetScaling

LESS_NEAR_EQUAL = 1e-3
NEAR_EQUAL = 1e-4
VERY_NEAR_EQUAL = 1e-5


@pytest.mark.skipif(keras_available, reason="Test only valid when keras not available")
def test_keras_not_available_exception(datadir):
    with pytest.raises(DeferredImportError):
        keras.models.load_model(datadir.file("keras_linear_131_relu"))


def _test_keras_linear_131(keras_fname, *, reduced_space=False):
    x, y, x_test = get_neural_network_data("131")

    nn = keras.models.load_model(keras_fname, compile=False)
    net = load_keras_sequential(nn, scaled_input_bounds=[(-1, 1)])
    m = pyo.ConcreteModel()
    m.neural_net_block = OmltBlock()
    if reduced_space:
        m.neural_net_block.build_formulation(ReducedSpaceNNFormulation(net))
    else:
        m.neural_net_block.build_formulation(FullSpaceNNFormulation(net))

    nn_outputs = nn.predict(x=x_test)
    for d in range(len(x_test)):
        m.neural_net_block.inputs[0].fix(x_test[d])
        status = pyo.SolverFactory("ipopt").solve(m, tee=False)
        pyo.assert_optimal_termination(status)
        assert (
            abs(pyo.value(m.neural_net_block.outputs[0]) - nn_outputs[d][0])
            < VERY_NEAR_EQUAL
        )


def _test_keras_mip_relu_131(keras_fname):
    x, y, x_test = get_neural_network_data("131")

    nn = keras.models.load_model(keras_fname, compile=False)
    net = load_keras_sequential(nn, scaled_input_bounds=[(-1, 1)])

    m = pyo.ConcreteModel()
    m.neural_net_block = OmltBlock()
    formulation = FullSpaceNNFormulation(net)
    m.neural_net_block.build_formulation(formulation)
    m.obj = pyo.Objective(expr=0)

    nn_outputs = nn.predict(x=x_test)
    for d in range(len(x_test)):
        m.neural_net_block.inputs[0].fix(x_test[d])
        status = pyo.SolverFactory("cbc").solve(m, tee=False)
        pyo.assert_optimal_termination(status)
        assert (
            abs(pyo.value(m.neural_net_block.outputs[0]) - nn_outputs[d][0])
            < VERY_NEAR_EQUAL
        )


def _test_keras_complementarity_relu_131(keras_fname):
    x, y, x_test = get_neural_network_data("131")

    nn = keras.models.load_model(keras_fname, compile=False)
    net = load_keras_sequential(nn)

    m = pyo.ConcreteModel()
    m.neural_net_block = OmltBlock()
    formulation = FullSpaceNNFormulation(
        net, activation_constraints={"relu": ComplementarityReLUActivation()}
    )
    m.neural_net_block.build_formulation(formulation)

    nn_outputs = nn.predict(x=x_test)
    for d in range(len(x_test)):
        m.neural_net_block.inputs[0].fix(x_test[d])
        status = pyo.SolverFactory("ipopt").solve(m, tee=False)
        pyo.assert_optimal_termination(status)
        assert (
            abs(pyo.value(m.neural_net_block.outputs[0]) - nn_outputs[d][0])
            < NEAR_EQUAL
        )


def _test_keras_linear_big(keras_fname, *, reduced_space=False):
    x, y, x_test = get_neural_network_data("131")

    nn = keras.models.load_model(keras_fname, compile=False)
    net = load_keras_sequential(nn)

    m = pyo.ConcreteModel()
    m.neural_net_block = OmltBlock()
    if reduced_space:
        m.neural_net_block.build_formulation(ReducedSpaceNNFormulation(net))
    else:
        m.neural_net_block.build_formulation(FullSpaceNNFormulation(net))

    nn_outputs = nn.predict(x=x_test)
    for d in range(len(x_test)):
        m.neural_net_block.inputs[0].fix(x_test[d])
        status = pyo.SolverFactory("ipopt").solve(m, tee=False)
        pyo.assert_optimal_termination(status)
        assert (
            abs(pyo.value(m.neural_net_block.outputs[0]) - nn_outputs[d][0])
            < VERY_NEAR_EQUAL
        )


@pytest.mark.skipif(not keras_available, reason="Need keras for this test")
def test_keras_linear_131_full(datadir):
    _test_keras_linear_131(datadir.file("keras_linear_131.keras"))
    _test_keras_linear_131(datadir.file("keras_linear_131_sigmoid.keras"))
    _test_keras_linear_131(
        datadir.file("keras_linear_131_sigmoid_output_activation.keras")
    )
    _test_keras_linear_131(
        datadir.file("keras_linear_131_sigmoid_softplus_output_activation.keras")
    )


@pytest.mark.skipif(not keras_available, reason="Need keras for this test")
def test_keras_linear_131_reduced(datadir):
    _test_keras_linear_131(datadir.file("keras_linear_131.keras"), reduced_space=True)
    _test_keras_linear_131(
        datadir.file("keras_linear_131_sigmoid.keras"),
        reduced_space=True,
    )
    _test_keras_linear_131(
        datadir.file("keras_linear_131_sigmoid_output_activation.keras"),
        reduced_space=True,
    )
    _test_keras_linear_131(
        datadir.file("keras_linear_131_sigmoid_softplus_output_activation.keras"),
        reduced_space=True,
    )


@pytest.mark.skipif(not keras_available, reason="Need keras for this test")
def test_keras_linear_131_relu(datadir):
    _test_keras_mip_relu_131(
        datadir.file("keras_linear_131_relu.keras"),
    )
    _test_keras_complementarity_relu_131(
        datadir.file("keras_linear_131_relu.keras"),
    )


@pytest.mark.skipif(not keras_available, reason="Need keras for this test")
def test_keras_linear_big(datadir):
    _test_keras_linear_big(datadir.file("big.keras"), reduced_space=False)


@pytest.mark.skip("Skip - this test is too big for now")
def test_keras_linear_big_reduced_space(datadir):
    _test_keras_linear_big("./models/big.keras", reduced_space=True)


@pytest.mark.skipif(not keras_available, reason="Need keras for this test")
def test_scaling_nn_block(datadir):
    NN = keras.models.load_model(datadir.file("keras_linear_131_relu.keras"))

    model = pyo.ConcreteModel()

    scale_x = (1, 0.5)
    scale_y = (-0.25, 0.125)

    scaler = OffsetScaling(
        offset_inputs=[scale_x[0]],
        factor_inputs=[scale_x[1]],
        offset_outputs=[scale_y[0]],
        factor_outputs=[scale_y[1]],
    )

    scaled_input_bounds = {0: (0, 5)}
    net = load_keras_sequential(
        NN, scaling_object=scaler, scaled_input_bounds=scaled_input_bounds
    )
    formulation = FullSpaceNNFormulation(net)
    model.nn = OmltBlock()
    model.nn.build_formulation(formulation)

    @model.Objective()
    def obj(mdl):
        return 1

    rng = np.random.default_rng()

    for x in rng.normal(1, 0.5, 10):
        model.nn.inputs[0].fix(x)
        pyo.SolverFactory("cbc").solve(model, tee=False)

        x_s = (x - scale_x[0]) / scale_x[1]
        y_s = NN.predict([np.array((x_s,))])
        y = y_s * scale_y[1] + scale_y[0]

        assert y - pyo.value(model.nn.outputs[0]) <= LESS_NEAR_EQUAL
