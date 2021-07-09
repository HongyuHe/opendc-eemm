from itertools import cycle
import pandas as pd
import numpy as np

from .preprocess import aggregate_consumption

extend_spot_prices = (
    lambda df_da, df_pred: pd.concat(
        [df_da] * (len(df_pred) // len(df_da)), ignore_index=True
    ).sort_values(by='interval-start').reset_index(drop=True)
)


def compute_agreement_score(df_pred, df_da, df_im):
    epsilon = 10
    df_da = extend_spot_prices(df_da, df_pred)
    perf = (
        (
            (
                np.sign(df_im['shortage-price'])
                == np.sign(df_pred['shortage-predicted'])
            ) & (
                np.sign(
                    round(
                        df_im['shortage-price'] - df_da['spot-price'], epsilon
                    )
                ) == np.sign(
                    round(
                        df_pred['shortage-predicted'] - df_da['spot-price'],
                        epsilon
                    )
                )
            )
        ).value_counts().to_dict()
    )

    perf[False] = perf[False] if False in perf else 0

    return perf[True] / (perf[False] + perf[True]) * 100


def garner_costs(od_price, df_trace, df_da, df_im):
    df_linear = aggregate_consumption(
        df_trace, power_model='LINEAR', freq='15min', preprocess=True
    )
    df_sqrt = aggregate_consumption(
        df_trace, power_model='SQRT', freq='15min', preprocess=True
    )
    df_base = aggregate_consumption(
        df_trace, power_model='BASE', freq='15min', preprocess=True
    )

    im_cost = {
        'baseload-LINEAR':
            (df_base.consumption * df_im['shortage-price']).sum(),
        'baseload-SQRT': (df_base.consumption * df_im['shortage-price']).sum(),
        'peakload-LINEAR':
            (
                (df_linear.consumption - df_base.consumption) *
                df_im['shortage-price']
            ).sum(),
        'peakload-SQRT':
            (
                (df_sqrt.consumption - df_base.consumption) *
                df_im['shortage-price']
            ).sum(),
        'fullload-LINEAR':
            (df_linear.consumption * df_im['shortage-price']).sum(),
        'fullload-SQRT': (df_sqrt.consumption * df_im['shortage-price']).sum(),
    }
    df_im_costs = pd.DataFrame(im_cost.items(), columns=['load', 'price'])
    df_im_costs['market'] = 'imbalance'
    df_im_costs['model'] = ''

    for i, row in df_im_costs.iterrows():
        tmp = row['load']
        df_im_costs.at[i, 'load'] = tmp.split('-')[0]
        df_im_costs.at[i, 'model'] = tmp.split('-')[1]

    df_base_da = aggregate_consumption(df_base, '1h')
    df_linear_da = aggregate_consumption(df_linear, '1h')
    df_sqrt_da = aggregate_consumption(df_sqrt, '1h')

    da_costs = {
        'baseload-LINEAR':
            (df_base_da.consumption * df_da['dayahead-price']).sum(),
        'baseload-SQRT':
            (df_base_da.consumption * df_da['dayahead-price']).sum(),
        'peakload-LINEAR':
            (
                (df_linear_da.consumption - df_base_da.consumption) *
                df_da['dayahead-price']
            ).sum(),
        'peakload-SQRT':
            (
                (df_sqrt_da.consumption - df_base_da.consumption) *
                df_da['dayahead-price']
            ).sum(),
        'fullload-LINEAR':
            (df_linear_da.consumption * df_da['dayahead-price']).sum(),
        'fullload-SQRT':
            (df_sqrt_da.consumption * df_da['dayahead-price']).sum(),
    }
    df_da_costs = pd.DataFrame(da_costs.items(), columns=['load', 'price'])
    df_da_costs['market'] = 'day-ahead'
    df_da_costs['model'] = ''

    for i, row in df_da_costs.iterrows():
        tmp = row['load']
        df_da_costs.at[i, 'load'] = tmp.split('-')[0]
        df_da_costs.at[i, 'model'] = tmp.split('-')[1]
    df_da_costs

    od_costs = {
        'baseload-LINEAR': (df_base.consumption * od_price).sum(),
        'baseload-SQRT': (df_base.consumption * od_price).sum(),
        'peakload-LINEAR':
            ((df_linear.consumption - df_base.consumption) * od_price).sum(),
        'peakload-SQRT':
            ((df_sqrt.consumption - df_base.consumption) * od_price).sum(),
        'fullload-LINEAR': (df_linear.consumption * od_price).sum(),
        'fullload-SQRT': (df_sqrt.consumption * od_price).sum(),
    }

    df_od_costs = pd.DataFrame(od_costs.items(), columns=['load', 'price'])
    df_od_costs['market'] = 'on-demand'
    df_od_costs['model'] = ''

    for i, row in df_od_costs.iterrows():
        tmp = row['load']
        df_od_costs.at[i, 'load'] = tmp.split('-')[0]
        df_od_costs.at[i, 'model'] = tmp.split('-')[1]

    return pd.concat([df_da_costs, df_im_costs, df_od_costs])


def compute_imbalance_cost(
    df_daload, df_fullload, df_price, is_one_price=False
):
    df_imload = df_daload.copy()
    df_imload['consumption'] = df_fullload.consumption - df_daload.consumption
    schedule = cycle(df_imload.consumption)
    im_cost = 0

    not_consider_state = True  # Shortcircuit state conditions.

    for _, isp in df_price.iterrows():
        im_consumption = next(schedule)

        if not_consider_state or isp.state >= 0:
            ''' Under production (Upwards or No regulation) '''
            if im_consumption > 0:
                # Shortage #
                im_cost += (
                    im_consumption * isp['shortage-price']
                )  # BRP -> TSO
            elif im_consumption < 0:
                # Surplus #
                #               # TSO -> BRP (one-price/two-price system)
                sell = (im_consumption * isp['surplus-price']) if is_one_price \
                        else (im_consumption * isp['spot-price']) # Two-price system
                im_cost += sell
            else:
                # Spot on #
                pass

        else:
            ''' Over production (Downwards regulation) '''
            if im_consumption > 0:
                # Shortage #
                #                 im_cost -= (im_consumption * isp['shortage-price']) # TSO -> BRP (one-price)
                im_cost -= (
                    im_consumption * isp['spot-price']
                )  # TSO -> BRP (two-price)
            elif im_consumption < 0:
                # Surplus #
                im_cost -= (im_consumption * isp['surplus-price'])  # BRP -> TSO
            else:
                # Spot on #
                pass

    return im_cost
