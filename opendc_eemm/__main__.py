"""Console script for opendc_eemm."""
from pprint import pprint
import pandas as pd
import argparse
import logging
import sys

from .__init__ import __version__
from .preprocess import *
from .market import *
from .visualization import *
from .decision import *
'''
Example commands:

trace:
    * opendc-eemm -t ./example/traces.parque --pue 1.58 trace -s power --g performance
    * opendc-eemm -t ./example/traces.parque --pue 1.58 trace -s oc

market:
    * opendc-eemm -t ./example/traces.parque market -s load -o 80.4 -d ./example/market/dayahead_2020.csv -i ./example/market/balancing_2020.csv
    * opendc-eemm -t ./example/traces.parque market -s strategy -o 80.4 -d ./example/market/dayahead_2020.csv -i ./example/market/balancing_2020.csv

decision:
    * opendc-eemm -t ./example/traces.parque decision -o score -f 12 -a first -d ./example/market/dayahead_2020.csv -i ./example/market/balancing_2020.csv -p ./example/fake_pred_sigma50.csv
    * opendc-eemm -t ./example/traces.parque decision -o schedule -f 12 -a first -d ./example/market/dayahead_2020.csv -i ./example/market/balancing_2020.csv -p ./example/fake_pred_sigma50.csv -s ./output
'''


def dispatch(args, df_trace):

    if args.cmd == 'trace':
        logging.info('Visualizing results.')
        if args.show == 'power':
            plot_power_draw(df_trace, args.governor, core_freq=args.frequency)
        elif args.show == 'oc':
            plot_overcommission(df_trace, core_freq=args.frequency)
    else:
        df_da = preprocess_dayahead(pd.read_csv(args.dayahead_prices))
        df_im = preprocess_imbalance(pd.read_csv(args.imbalance_prices))

        if args.cmd == 'market':
            df_costs = garner_costs(args.od_price, df_trace, df_da, df_im)
            logging.info('Visualizing results.')

            if args.show == 'load':
                plot_market_costs(df_costs)
            elif args.show == 'strategy':
                plot_purchase_comparison(df_costs)

        elif args.cmd == 'decision':
            df_pred = aggregate_predictions(
                pd.read_csv(args.predictions), args.aggregate
            )

            if args.option == 'score':
                score = compute_agreement_score(df_pred, df_da, df_im)
                logging.info(
                    f"The AA score of the predictions is {score: 0.3f}%."
                )
            elif args.option == 'schedule':
                logging.info('DVFS scheduler invoked.')
                df_power = process_traces_for_scheduling(df_trace)
                df_sched = schedule(
                    args.factor, df_pred, df_da, df_power, args.save_to
                )
                pprint(df_sched)

                if args.save_to:
                    logging.info(
                        f"`dvfs_schedule.csv` has been saved to {args.save_to}"
                    )
    return 0


def main():
    """Console script for opendc_eemm."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='(%(asctime)s) OpenDC EEMM - [%(levelname)s] %(message)s'
    )

    parser = argparse.ArgumentParser(
        add_help=False,
        description="CLI of OpenDC Extension for Energy Modelling & Managament."
    )
    subparsers = parser.add_subparsers(
        dest='cmd', description='Available commands.'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s ' + __version__,
        help="Show version number of the package and exit."
    )
    parser.add_argument(
        '-h',
        '--help',
        action='help',
        default=argparse.SUPPRESS,
        help='Show the help messages and exit.'
    )
    parser.add_argument(
        '-t',
        '--trace',
        required=True,
        metavar='path',
        help='Path to simulation results (expecting a Parque file).'
    )
    parser.add_argument(
        '--pue',
        default=1.58,
        type=float,
        metavar='float',
        help='PUE value of the simulatied datacenter.'
    )

    trace_parser = subparsers.add_parser(
        'trace', help='Visualize simulation results.'
    )
    trace_parser.add_argument(
        '-s',
        '--show',
        required=True,
        choices=['power', 'over-commission'],
        metavar="['power', 'oc']",
        help=
        "Choose 'power' to show power draw; choose 'oc' to show over-commissioned."
    )
    trace_parser.add_argument(
        '-f',
        '--frequency',
        type=float,
        default=2670,
        metavar='float',
        help='Frequency of simulated machines.'
    )
    trace_parser.add_argument(
        '-g', '--governor', metavar='value', help='Governor to visualize.'
    )

    market_parser = subparsers.add_parser(
        'market', help='Compare costs in different markets.'
    )
    market_parser.add_argument(
        '-s',
        '--show',
        required=True,
        choices=['load', 'strategy'],
        metavar="['load', 'strategy']"
    )
    market_parser.add_argument(
        '-o',
        '--od_price',
        required=True,
        type=float,
        metavar='float',
        help='On-demand energy price.'
    )
    market_parser.add_argument(
        '-d',
        '--dayahead_prices',
        required=True,
        metavar='path',
        help='Path to day-ahead energy prices (expecting a CSV file).'
    )
    market_parser.add_argument(
        '-i',
        '--imbalance_prices',
        required=True,
        metavar='path',
        help='Path to imbalance energy prices (expecting a CSV file).'
    )

    schedule_parser = subparsers.add_parser(
        'decision', help='Optimize fine-grained decision-making.'
    )
    schedule_parser.add_argument(
        '-o',
        '--option',
        required=True,
        choices=['score', 'schedule'],
        metavar="['score', 'schedule']",
        help=
        "Choose 'score' to compute the agreement accuracy (AA) sore of the predictions; choose 'schedule' for DVFS scheduling."
    )
    schedule_parser.add_argument(
        '-f',
        '--factor',
        type=float,
        metavar='float',
        help='Damping factor of the DVFS scheduler.'
    )
    schedule_parser.add_argument(
        '-d',
        '--dayahead_prices',
        required=True,
        metavar='path',
        help='Path to day-ahead energy prices (expecting a CSV file).'
    )
    schedule_parser.add_argument(
        '-i',
        '--imbalance_prices',
        required=True,
        metavar='path',
        help='Path to imbalance energy prices (expecting a CSV file).'
    )
    schedule_parser.add_argument(
        '-p',
        '--predictions',
        required=True,
        metavar='path',
        help='Machine learning predictions (expecting a CSV file).'
    )
    schedule_parser.add_argument(
        '-a',
        '--aggregate',
        required=True,
        choices=['first', 'last', 'mean'],
        metavar="['first', 'last', 'mean']",
        help="Aggregation method for machine learning predictions."
    )
    schedule_parser.add_argument(
        '-s',
        '--save_to',
        default=None,
        metavar='path',
        help='Destination path of the DVFS schedule.'
    )

    args = parser.parse_args()

    print()
    logging.info('Starting.')
    logging.info('Preprocessing traces.')
    data_trace = pd.read_parquet(args.trace)
    df_trace = preprocess_traces(data_trace, pue=args.pue, map_governor=True)

    return dispatch(args, df_trace)


if __name__ == "__main__":
    sys.exit(main())
