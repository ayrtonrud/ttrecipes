#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Authors:      Enrique G. Paredes <egparedes@ifi.uzh.ch>
#               Rafael Ballester-Ripoll <rballester@ifi.uzh.ch>
#
# Copyright:    ttrecipes project (c) 2017
#               VMMLab - University of Zurich
# -----------------------------------------------------------------------------

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import pprint
import random

import numpy as np

import ttrecipes as tr


def main():
    default_bins = 100
    default_order = 2
    default_products = 10
    default_years = 2.0

    parser = argparse.ArgumentParser(
        description="Perform sensitivity analysis of a decay chain of species"
                    " with different decay rates")
    parser.add_argument('--seed', type=int,
                        help="Random seed (default: not set)")
    parser.add_argument('--verbose', action='store_true',
                        help="Verbose mode (default: False)")
    parser.add_argument('-b', '--bins', default=default_bins, type=int,
                        help="Number of samples for each input axis "
                             "(default: {})".format(default_bins))
    parser.add_argument('--order', default=default_order, type=int,
                        help="Maximum order of the collected indices "
                             "(default: {})".format(default_order))
    parser.add_argument('--products', default=default_products, type=int,
                        help='Number of decaying products in the chain '
                             '(default: {})'.format(default_products))
    parser.add_argument('--years', default=default_years, type=float,
                        help='Simulated years of decay time '
                             '(default: {})'.format(default_years))

    print("*TT-recipes* example:", parser.description, "\n")
    args = parser.parse_args()
    if args.verbose:
        pprint.pprint(args)

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    f, axes = tr.models.get_decay_poisson(
        d=args.products, span=args.years, hl_range=(3.0 * (1 / 12.0), 3.0),
        time_step=1.0 / 365.0, name_tmpl='lambda_{:0>2}')
    if args.verbose:
        pprint.pprint(axes)

    print("+ Computing tensor approximations of variance-based sensitivity metrics...")
    results = tr.sensitivity_analysis.var_metrics(
        f, axes, default_bins=args.bins, verbose=args.verbose, eps=1e-4,
        max_order=args.order, cross_kwargs=dict(), print_results=True)


if __name__ == "__main__":
    main()
