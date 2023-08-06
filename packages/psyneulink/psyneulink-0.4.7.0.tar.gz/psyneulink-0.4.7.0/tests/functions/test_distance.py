
import psyneulink.components.functions.function as Function
import psyneulink.globals.keywords as kw
import numpy as np
import pytest

SIZE=4
# Some metrics (CROSS_ENTROPY) don't like 0s
test_var = [np.random.rand(SIZE) + Function.EPSILON, np.random.rand(SIZE) + Function.EPSILON]
v1 = test_var[0]
v2 = test_var[1]
norm = len(test_var[0])

test_data = [
    (test_var, kw.DIFFERENCE, False, None, np.sum(np.abs(v1 - v2))),
    (test_var, kw.DIFFERENCE, True,  None, np.sum(np.abs(v1 - v2))/norm),
    (test_var, kw.EUCLIDEAN, False, None, np.linalg.norm(v1 - v2)),
    (test_var, kw.EUCLIDEAN, True,  None, np.linalg.norm(v1 - v2)/norm),
    (test_var, kw.ANGLE, False, "Needs sci-py", 0),
    (test_var, kw.ANGLE, True,  "Needs sci-py", 0/norm),
    (test_var, kw.CORRELATION, False, None, np.correlate(v1, v2)),
    (test_var, kw.CORRELATION, True,  None, np.correlate(v1, v2)/norm),
    (test_var, kw.PEARSON, False, None, np.corrcoef(v1, v2)),
    (test_var, kw.PEARSON, True,  None, np.corrcoef(v1, v2)/norm),
    (test_var, kw.CROSS_ENTROPY, False, None, -np.sum(v1*np.log(v2))),
    (test_var, kw.CROSS_ENTROPY, True,  None, -np.sum(v1*np.log(v2))/norm),
    (test_var, kw.ENERGY, False, None, -np.sum(v1*v2)/2),
    (test_var, kw.ENERGY, True, None, (-np.sum(v1*v2)/2)/norm**2),
]

# use list, naming function produces ugly names
names = [
    "DIFFERENCE",
    "DIFFERENCE NORMALIZED",
    "EUCLIDEAN",
    "EUCLIDEAN NORMALIZED",
    "ANGLE",
    "ANGLE NORMALIZED",
    "CORRELATION",
    "CORRELATION NORMALIZED",
    "PEARSON",
    "PEARSON NORMALIZED",
    "CROSS_ENTROPY",
    "CROSS_ENTROPY NORMALIZED",
    "ENERGY",
    "ENERGY NORMALIZED",
]

@pytest.mark.function
@pytest.mark.distance_function
@pytest.mark.parametrize("variable, metric, normalize, fail, expected", test_data, ids=names)
@pytest.mark.benchmark
def test_basic(variable, metric, normalize, fail, expected, benchmark):
    if fail is not None:
        # This is a rather ugly hack to stop pytest benchmark complains
        benchmark.disabled = True
        benchmark(lambda _:0,0)
        pytest.xfail(fail)
        return
    f = Function.Distance(default_variable=variable, metric=metric, normalize=normalize)
    benchmark.group = "DistanceFunction " + metric + ("-normalized" if normalize else "")
    res = benchmark(f.function, variable)
    assert np.allclose(res, expected)
