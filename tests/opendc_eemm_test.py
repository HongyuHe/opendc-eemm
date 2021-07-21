import pytest
import pandas as pd
from opendc_eemm.preprocess import aggregate_predictions
from opendc_eemm.visualization import plot_power_draw

@pytest.mark.parametrize('value, expected', [(1, 1)])
def test_test(value, expected):
    assert value == expected

def test_aggregate_predictions():
    with pytest.raises(ValueError):
        aggregate_predictions(pd.DataFrame(), 'max')

def test_plot_power_draw():
    test_dict = {'governor': 'superscaler'}
    with pytest.raises(RuntimeError):
        plot_power_draw(pd.DataFrame([test_dict]), 'powersave', 0)
