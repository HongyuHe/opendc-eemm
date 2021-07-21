import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
import itertools
from itertools import cycle

watt_to_mwh = lambda x: np.float128(x * 5 * 60 * 2.7777777777778e-10)


def preprocess_dayahead(df):
    df['interval-start'] = pd.to_datetime(
        df['MTU (CET)'].apply(lambda cell: cell.split('-')[0].strip()),
        format='%d.%m.%Y %H:%M'
    )
    df = df.drop([
        'MTU (CET)', 'BZN|NL'
    ], axis=1).set_index('interval-start').reset_index()  # Reorder columns.
    df.columns = ['interval-start', 'dayahead-price']
    return df


# Default frequency == one ISP (15min).
def aggregate_predictions(df, agg, freq='15min'):
    if agg not in ['first', 'last', 'mean']:
        raise ValueError(f"{agg=} is not one of ['first', 'last', 'mean'].")

    df.columns = df.columns.str.replace('_', '-')
    df['interval-start'] = pd.to_datetime(df['interval-start'])

    return df.groupby([pd.Grouper(freq=freq,
                                  key='interval-start')]).agg(agg).reset_index()


def preprocess_imbalance(df_im):
    df = pd.DataFrame()
    df['shortage-price'] = df_im.Consume
    df['surplus-price'] = df_im.Feed
    return df


def preprocess_traces(df, pue, map_governor=False):
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.columns = df.columns.str.replace('_', '-')
    df['power-model'] = df['power-model'].apply(lambda s: s.replace('_', '-'))
    # Use PUE to compute the power draw of the whole datacenter
    df['power-draw'] = df['power-draw'] * pue
    if map_governor:
        df['governor'] = df['governor'].map({ # Map model names here.
            'ConservativeScalingGovernor[threshold=0.8,stepSize=-1.0]': 'conservative',
            'OnDemandScalingGovernor[threshold=0.8]': 'ondemand',
            'PerformanceScalingGovernor': 'performance',
            'PowerSaveScalingGovernor': 'powersave',
            'null': 'no-dvfs',
        })
    return df


def prepare_traces_for_plot(df, core_freq):
    usage_to_percent = lambda x: x['cpu-usage'] / (core_freq * x.cores) * 100
    demand_to_percent = lambda x: x['cpu-demand'] / (core_freq * x.cores) * 100

    df = df.groupby(
        [
            'governor', 'power-model', 'host-id',
            pd.Grouper(freq='1d', key='timestamp')
        ]
    ).mean().reset_index(level=['timestamp', 'host-id'])
    df['cpu-usage'] = df.apply(usage_to_percent, axis=1)
    df['cpu-demand'] = df.apply(demand_to_percent, axis=1)
    return df.reset_index()


def aggregate_consumption(
    df_raw, freq, kind='', power_model=None, preprocess=False
):
    df = pd.DataFrame()
    df_raw = df_raw[df_raw['power-model'] == power_model
                   ] if power_model else df_raw
    df['timestamp'] = pd.to_datetime(df_raw['timestamp'], unit='ms')

    if (preprocess):
        # Only keep the power draw for now.
        df_raw.columns = df_raw.columns.str.replace('_', '-')
        df['consumption'] = df_raw['power-draw']
        # * The original traces is of 5min-granularity.
        # * Jouls => MWh (1 J = 2.7777777777778 * 10^-10 MWh).
        df['consumption'] = watt_to_mwh(df.consumption)
    else:
        df['consumption'] = df_raw.consumption

    df = df.groupby([pd.Grouper(freq=freq, key='timestamp')]
                   ).sum().reset_index(level=['timestamp'])
    df['kind'] = f"{kind} {freq}"
    return df
