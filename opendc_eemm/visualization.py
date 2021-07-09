import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
import datetime
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
import itertools
from itertools import cycle
from statannot import add_stat_annotation
from matplotlib.patches import *
import matplotlib.dates as mdates
from datetime import timedelta

import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib import rc
import matplotlib.font_manager

plt.style.use('default')
sns.set_style("whitegrid", {'grid.linestyle': '--'})

from .preprocess import *


def set_hatches(ax, cycle):
    hatches = itertools.cycle(
        ['/', '\\', 'x', '-', '.', '//', '+', '*', 'o', 'O']
    )
    for i, bar in enumerate(ax.patches):
        if i % cycle == 0:
            hatch = next(hatches)
        bar.set_hatch(hatch)


def show_values_on_bars(
    axs,
    h_v="v",
    pad=0.4,
    append='',
):
    def _show_on_single_plot(ax):
        if h_v == "v":
            ''' Vertical plot '''
            for p in ax.patches:
                _x = p.get_x() + p.get_width() / 2
                _y = p.get_y() + p.get_height() + float(pad)
                value = float(p.get_height())
                ax.text(_x, _y, f"{value:.3f}{append}", ha="center")
        elif h_v == "h":
            ''' Horizontal plot '''
            for p in ax.patches:
                _x = p.get_x() + p.get_width() + float(pad)
                _y = p.get_y() + p.get_height() / 1.5
                value = float(p.get_width())
                ax.text(_x, _y, f"{value:.3f}{append}", ha="left")

    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _show_on_single_plot(ax)
    else:
        _show_on_single_plot(axs)


def set_sns_legend(ax, new_loc='best', title=None, **kws):
    old_legend = ax.legend_
    handles = old_legend.legendHandles
    labels = [t.get_text() for t in old_legend.get_texts()]
    title = old_legend.get_title().get_text() if title is None else title
    ax.legend(handles, labels, loc=new_loc, title=title, **kws)


def plot_power_draw(df, governor, core_freq):
    governors = set(df.governor)
    if governor not in governors:
        raise RuntimeError(f"{governor=} must be in {governors}")

    df = prepare_traces_for_plot(df, core_freq)
    hue_order = ['SQRT', 'LINEAR']
    ax = sns.lineplot(
        data=df[(df.governor == governor) & (df['power-model'] != 'BASE')],
        hue_order=hue_order,
        x="timestamp",
        y='power-draw',
        hue='power-model',
        style='power-model',
        ci=90,
        n_boot=1500
    )

    date_form = DateFormatter("%d %b")
    ax.xaxis.set_major_formatter(date_form)
    ax.set_title(f"Governor: {governor}")
    ax.legend(title='Power Model', fontsize=10, loc='best')
    ax.set(ylabel='Instant Power Draw [Watt]', xlabel=None)
    plt.xticks(rotation=30)
    plt.show()


def plot_overcommission(df, core_freq):
    df = prepare_traces_for_plot(df, core_freq)

    ax = sns.lineplot(
        data=df,
        x="timestamp",
        y='overcommissioned-burst',
        hue='governor',
        style='governor',
        ci=90,
        n_boot=1500
    )

    date_form = DateFormatter("%d\ %b")
    ax.xaxis.set_major_formatter(date_form)
    ax.set(xlabel=None, ylabel='Overcommissioned CPU Cycle')
    ax.legend(title='Governor', fontsize=10, loc='best')
    sns.despine(left=True)
    plt.xticks(rotation=30)
    plt.show()


def plot_market_costs(df):
    ax = sns.barplot(
        data=df,
        y='load',
        x='price',
        hue='market',
        palette='pastel',
        estimator=np.mean,
        ec='k',
        errwidth=2,
        capsize=0.1,
        errcolor='k'
    )
    ax.set(ylabel='Load Type', xlabel='Energy Cost [€]')
    ax.legend(title='Market')
    sns.despine(left=True)
    set_hatches(ax, 3)
    show_values_on_bars(ax, 'h', 100, ' €')
    plt.show()


def plot_purchase_comparison(df_costs):
    da_base = df_costs[(df_costs.load == 'baseload') &
                       (df_costs.market == 'day-ahead')]['price'].mean()
    im_peak = df_costs[(df_costs.load == 'peakload') &
                       (df_costs.market == 'imbalance')]['price'].mean()
    da_im = da_base + im_peak

    da_full = df_costs[(df_costs.load == 'fullload') &
                       (df_costs.market == 'day-ahead')]['price'].mean()
    od_full = df_costs[(df_costs.load == 'fullload') &
                       (df_costs.market == 'on-demand')]['price'].mean()

    odda_reduction = (od_full - da_full) / od_full * 100
    oddaim_reduction = (od_full - da_im) / od_full * 100
    daim_reduction = (da_full - da_im) / da_full * 100

    od_cat = 'On-Demand (full load)'
    da_cat = 'Day-Aead (full load)'
    da_im_cat = 'Day-Aead (base load)\n+ Balancing (peak load)'

    x = [od_cat, da_cat, da_im_cat]
    y = [od_full, da_full, da_im]

    order = x
    ax = sns.barplot(
        x=x, y=y, order=order, palette='deep', ec='k', lw=2, fill=True
    )
    ax.set_ylabel('Energy Cost [€]')

    set_hatches(ax, 1)

    show_values_on_bars(ax, 'v', 100, ' €')

    add_stat_annotation(
        ax,
        x=x,
        y=y,
        order=order,
        box_pairs=[(da_cat, da_im_cat), (od_cat, da_cat), (od_cat, da_im_cat)],
        text_annot_custom=[
            f"{abs(daim_reduction): 0.1f}\%", f"{odda_reduction: 0.1f}\%",
            f"{oddaim_reduction: 0.1f}\%"
        ],
        pvalues=[0, 0, 0],
        perform_stat_test=False,
        line_offset_to_box=0.08,
        text_offset=0.08,
        text_format='full',
        loc='inside',
        verbose=0
    )
    sns.despine(left=True)
    plt.show()
