import numpy as np
import pandas as pd
import os
from tqdm import tqdm

from .preprocess import watt_to_mwh
from .market import extend_spot_prices


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
                        df_im['shortage-price'] - df_da['dayahead-price'],
                        epsilon
                    )
                ) == np.sign(
                    round(
                        df_pred['shortage-predicted'] - df_da['dayahead-price'],
                        epsilon
                    )
                )
            )
        ).value_counts().to_dict()
    )
    perf[False] = perf[False] if False in perf else 0

    return perf[True] / (perf[False] + perf[True]) * 100


def process_traces_for_scheduling(df_trace):
    df = (
        df_trace[df_trace['power-model'] != 'BASE'].drop(
            [
                'duration', 'state', 'vm-count', 'requested-burst',
                'granted-burst', 'interfered-burst', 'cpu-usage', 'cpu-demand',
                'cores'
            ],
            axis=1
        )
        # Average two power models
        .groupby(['governor', 'host-id', 'timestamp']).mean()
        # Aggregate hosts' data
        .groupby(['governor', 'timestamp']).sum().reset_index()
        # Aggregate to ISP (15min)
        .groupby(['governor',
                  pd.Grouper(freq='15min',
                             key='timestamp')]).sum().drop('no-dvfs')
    )
    df['consumption'] = watt_to_mwh(df['power-draw'])
    return df


def schedule(damping, df_pred, df_da, df_trace, save_path=None):
    df_da = extend_spot_prices(df_da, df_pred)
    # Initialize an empty schedule.
    sched = []
    governor = None
    timestamp = None
    total_oc = 0
    prev_overcommission = 0
    oc_counter = 0

    for i, inference in tqdm(df_pred.iterrows(), total=len(df_pred)):
        spot_price = df_da.iloc[i]['dayahead-price']
        # Manually take the mean for performance reasons.
        curr_overcommission = total_oc / (i + 1)

        if curr_overcommission > prev_overcommission:
            # OC level increased
            oc_counter += 1
        else:
            # OC level decreased.
            oc_counter = 0

        prev_overcommission = curr_overcommission

        if inference['shortage-predicted'] <= 0:
            #             if oc_counter >= damping:
            #                 governor = 'ondemand'
            #                 oc_counter = 0
            #             else:
            governor = 'performance'
        else:
            if inference['shortage-predicted'] > spot_price:
                governor = 'powersave'
            else:
                if oc_counter >= damping:
                    governor = 'conservative'
                    oc_counter = 0
                else:
                    governor = 'ondemand'

        record = df_trace.loc[governor].reset_index().iloc[i % len(df_trace)]
        total_oc += record['overcommissioned-burst']
        sched.append(
            {
                'timestamp': inference['interval-start'],
                'governor': governor
            }
        )

    df_sched = pd.DataFrame(sched)
    if save_path and not os.path.exists(save_path):
        os.makedirs(save_path)
        df_sched.to_csv(f"{save_path}/dvfs_schedule.csv", index=False)

    return df_sched


def compute_energy_cost(df_sched, df_price):
    imbalance = df_sched.consumption - df_sched.baseload
    im_cost = 0

    for i, ledger in tqdm(df_price.iterrows(), total=len(df_price)):

        im_consumption = imbalance.iloc[i]

        if im_consumption > 0:
            # Shortage #
            im_cost += (im_consumption * ledger['shortage-price'])  # BRP -> TSO
        elif im_consumption < 0:
            # Surplus #
            im_cost += (
                im_consumption * ledger['spot-price']
            )  # TSO -> BRP (two-price system)
        else:
            # Spot on #
            pass

    total_cost = im_cost + (df_sched.baseload * df_price['spot-price']).sum()
    return total_cost


def get_governor_performance(governor, df_dc, df_price):
    # Extend simulation results.
    repeat = int(np.ceil(len(df_price) / len(df_dc.loc[governor])))
    df_governor = pd.concat(
        [df_dc.loc[governor].reset_index()] * repeat, ignore_index=True
    ).iloc[:len(df_price)]

    return df_governor, {
        'governor': governor,
        'cost': compute_energy_cost(df_governor, df_price),
        'consumption': df_governor.consumption.sum(),
        'overcommission': df_governor['overcommissioned-burst'].sum()
    }


def get_schedule_performance(df_sched, df_price, governor_perf):
    consumption = df_sched.consumption.sum()
    oc = df_sched['overcommissioned-burst'].sum()
    cost = compute_energy_cost(df_sched, df_price)

    return {
        'against':
            governor_perf['governor'],
        'cost %': (cost - governor_perf['cost']) / governor_perf['cost'] * 100,
        'energy %':
            (consumption - governor_perf['consumption']) /
            governor_perf['consumption'] * 100,
        'overcommission %':
            (oc - governor_perf['overcommission']) /
            governor_perf['overcommission'] * 100,
    }
