# -*- coding: utf-8 -*-
"""Sample functions for surrogate modeling and sensitivity analysis.

This module contains different examples of multidimensional functions that may
work as sensible examples for real-world models.

"""

# -----------------------------------------------------------------------------
# Authors:      Enrique G. Paredes <egparedes@ifi.uzh.ch>
#               Rafael Ballester-Ripoll <rballester@ifi.uzh.ch>
#
# Copyright:    TT Recipes project (c) 2016-2017
#               VMMLab - University of Zurich
# -----------------------------------------------------------------------------

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import collections
import functools

import numpy as np


def make_unif_axes(n, bounds=(0.0, 1.0), name_tmpl='x{}'):
    assert n > 0
    return tuple([(name_tmpl.format(i + 1), None, bounds, ('unif', None, None))
                  for i in range(n)])


def make_gaussian_axes(n, sigmas, name_tmpl='x{}'):
    assert 0 < n == len(sigmas)
    return tuple([(name_tmpl.format(i + 1), None, None, ('norm', 0.0, sigmas[i]))
                  for i, sigma in enumerate(sigmas)])


def get_linear_mix(d, betas=1.0, sigmas=1.0, name_tmpl='x{}'):
    """Test function used for various numerical estimation methods.

    References:
        - Bertrand Iooss, Clementine Prieur. "Shapley effects for
            sensitivity analysis with dependent inputs: comparisons with
            Sobol’ indices, numerical estimation and applications".

         https://hal.inria.fr/hal-01556303/document

    """
    assert d > 0

    if isinstance(betas, collections.Iterable):
        betas = np.asarray(betas)
        assert len(betas) == d
    else:
        betas *= np.ones(d)

    if isinstance(sigmas, collections.Iterable):
        sigmas = np.asarray(sigmas)
        assert len(sigmas) == d
    else:
        sigmas *= np.ones(d)

    def function(Xs, betas):
        assert Xs.shape[1] == d == len(betas)
        return Xs.dot(betas)

    axes = make_gaussian_axes(d, sigmas, name_tmpl=name_tmpl)

    return functools.partial(function, betas=betas), axes


def get_ishigami(a=7, b=0.1, name_tmpl='x{}'):
    """The Ishigami function of Ishigami & Homma (1990).

     This very well-known function exhibits strong nonlinearity and
     nonmonotonicity. It also has a peculiar dependence on x3, as described
     by Sobol' & Levitan (1999). The values of a and b used by
     Crestaux et al. (2007) and Marrel et al. (2009) are: a = 7 and b = 0.1.
     Sobol' & Levitan (1999) use a = 7 and b = 0.05.

    References:
        - http://www.sfu.ca/~ssurjano/ishigami.html
        - Sobol', I. M., & Levitan, Y. L. (1999). "On the use of variance
            reducing multipliers in Monte Carlo computations of a global
            sensitivity index". Computer Physics Communications, 117(1), 52-61.
        - Ishigami, T., & Homma, T. (1990, December). "An importance quantification
            technique in uncertainty analysis for computer models"
            In Uncertainty Modeling and Analysis, 1990. Proceedings.,
            First International Symposium on (pp. 398-403). IEEE.

    """
    def function(Xs):
        assert Xs.shape[1] == 3
        return np.sin(Xs[:, 0]) + a * np.sin(Xs[:, 1])**2 + b * (Xs[:, 2]**4) * np.sin(Xs[:, 0])

    axes = make_unif_axes(3, bounds=(-np.pi, np.pi), name_tmpl=name_tmpl)

    return function, axes


def get_sobol_g(d, a=6.52, name_tmpl='x{}'):
    """Test function used for various numerical estimation methods.

    The function is integrated over the hypercube [0, 1], ``for i in range(d)``
    For each index ``i``, a lower value of ai indicates a higher importance
    of the input variable ``x_i``.

    Kucherenko et al. (2011) use the values a0 = a1 = 0 and a3 = … = ad = 6.52.
    When used with ai = 6.52, for all i = 1, … d, they classify it as a Type B function,
    meaning that it has dominant low-order terms and a small effective dimension.

    In many cases, for instance in Marrel et al. (2008), there is the constraint
    that ai ≥ 0. They conclude that:

        for ai = 0, xi is very important
        for ai = 1, xi is relatively important
        for ai = 9, xi is non-important
        for ai = 99, xi is non-significant


    References:
        - http://www.sfu.ca/~ssurjano/gfunc.html
        - Kucherenko, S., Feil, B., Shah, N., & Mauntz, W. (2011). "The identification
            of model effective dimensions using global sensitivity analysis"
            Reliability Engineering & System Safety, 96(4), 440-449.
        - Marrel, A., Iooss, B., Laurent, B., & Roustant, O. (2009).
            "Calculations of sobol indices for the gaussian process metamodel"
            Reliability Engineering & System Safety, 94(3), 742-751.
        - Saltelli, A., & Sobol', I. Y. M. (1994). "Sensitivity analysis for
            nonlinear mathematical models: numerical experience"
            Matematicheskoe Modelirovanie, 7(11), 16-28.

    References (a=0 -> davis_rabinowitz_integral):
        - Kucherenko, S., Feil, B., Shah, N., & Mauntz, W. (2011). "The identification
            of model effective dimensions using global sensitivity analysis"
            Reliability Engineering & System Safety, 96(4), 440-449.
        -  Bratley P, Fox B. (1988). "Algorithm 659: Implementing Sobol's
            Quasirandom Sequence Generator". ACM Transactions on
            Mathematical Software. Vol. 14, Number 1, March 1988, pages 88-100
        - Philip J. Davis Philip Rabinowitz (1984). "Methods of Numerical
            Integration, 2nd Edition".  Academic Press

    """
    assert d > 0

    if isinstance(a, collections.Iterable):
        a = np.asarray(a)
        assert len(a) == d
    else:
        a *= np.ones(d)

    def function(Xs, a):
        assert(Xs.shape[1] == d)
        result = np.ones(Xs.shape[0])
        for i in range(Xs.shape[1]):
            result *= (np.abs(4. * Xs[:, i] - 2) + a[i]) / (1. + a[i])
        return result

    axes = make_unif_axes(d, name_tmpl=name_tmpl)

    return functools.partial(function, a=a), axes


def get_prod(d, constant=1, name_tmpl='x{}'):
    """Analytical test function used for sensitivity analysis.

    References:
        - Kucherenko, S., Feil, B., Shah, N., & Mauntz, W. (2011). "The identification
            of model effective dimensions using global sensitivity analysis"
            Reliability Engineering & System Safety, 96(4), 440-449.

    """
    assert d > 0

    def function(Xs, constant):

        Xs = np.asarray(Xs)
        assert(Xs.shape[1] == d)
        return np.prod(np.abs(4 * Xs - 2), axis=1)

    axes = make_unif_axes(d, name_tmpl=name_tmpl)

    return functools.partial(function, constant=constant), axes


def get_decay_poisson(d, span=10.0, hl_range=(3*(1.0/12.0), 3.0),
                      time_step=1.0 / 365, name_tmpl='x{}'):
    """Simulated decay of species with different decay rates

        - Xs: decay_rates in years
        - span(float): simulated time span in years
        - output: fractions of the last specie

    References:
        - Andrea Saltelli, Paola Annoni. "How to avoid a perfunctory sensitivity analysis"
            http://ac.els-cdn.com/S1364815210001180/1-s2.0-S1364815210001180-main.pdf?_tid=96c74b44-365c-11e7-9cc2-00000aab0f27&acdnat=1494515875_1dcbccb878ead778df602acd24051628
        - http://129.173.120.78/~kreplak/wordpress/wp-content/uploads/2010/12/Phyc2150_2016_Lecture10.pdf

    """
    assert d > 0

    def half_life_to_decay_rate(half_lives, year_fraction):
        # decay rates as average number of atom decays per year_fraction
        return 1 - np.exp(- year_fraction * np.log(2) / np.asarray(half_lives))

    def function(Xs, span):
        Xs = np.asarray(Xs)
        if Xs.ndim == 1:
            Xs = np.expand_dims(Xs, axis=0)
        n_products = Xs.shape[1]
        quantities = np.zeros((Xs.shape[0], n_products + 1))
        quantities[:, 0] = 1.0

        # decay rates as average number of atom decays per day
        # rates = 1 - np.exp(- day * math.log(2) / Xs)
        # rates = half_life_to_decay_rate(Xs, 1.0 / 365.0)
        rates = Xs
        n_days = int(span * 365.0)
        for d in range(n_days):
            offsets = quantities[:, :n_products] * rates
            quantities[:, :n_products] -= offsets
            quantities[:, 1:] += offsets

        return quantities[:, -1]

    decay_range = half_life_to_decay_rate(hl_range, time_step)[::-1]
    axes = make_unif_axes(d, bounds=decay_range, name_tmpl=name_tmpl)

    return functools.partial(function, span=span), axes


def get_borehole():
    """Example of analytical model with non-uniform variables

    References:
        - http://www.sfu.ca/~ssurjano/borehole.html
        - https://tel.archives-ouvertes.fr/tel-01143694/document (p. 84)

    """
    def function(Xs):
        rw = Xs[:, 0]
        r = Xs[:, 1]
        Tu = Xs[:, 2]
        Hu = Xs[:, 3]
        Tl = Xs[:, 4]
        Hl = Xs[:, 5]
        L = Xs[:, 6]
        Kw = Xs[:, 7]

        frac1 = 2 * np.pi * Tu * (Hu - Hl)
        frac2a = 2 * L * Tu / (np.log(r / rw) * (rw**2) * Kw)
        frac2b = Tu / Tl
        frac2 = np.log(r / rw) * (1 + frac2a + frac2b)

        return frac1 / frac2

    axes = (('r_w', None, (0.05, 0.15), ('norm', 0.10, 0.0161812)),
            ('r', None, (100, 50000), ('lognorm', 7.71, 1.0056)),
            ('T_u', None, (63070, 115600), ('unif', None, None)),
            ('H_u', None, (990, 1110), ('unif', None, None)),
            ('T_l', None, (63.1, 116), ('unif', None, None)),
            ('H_l', None, (700, 820), ('unif', None, None)),
            ('L', None, (1120, 1680), ('unif', None, None)),
            ('K_w', None, (9855, 12045), ('unif', None, None)))

    return function, axes


def get_piston():
    """Piston simulation routine.

    References:
        - http://www.sfu.ca/~ssurjano/piston.html

    """
    def function(Xs):
        M = Xs[:, 0]
        S = Xs[:, 1]
        V0 = Xs[:, 2]
        k = Xs[:, 3]
        P0 = Xs[:, 4]
        Ta = Xs[:, 5]
        T0 = Xs[:, 6]

        Aterm1 = P0 * S
        Aterm2 = 19.62 * M
        Aterm3 = -k * V0 / S
        A = Aterm1 + Aterm2 + Aterm3

        Vfact1 = S / (2 * k)
        Vfact2 = np.sqrt(A**2 + 4 * k * (P0 * V0 / T0) * Ta)
        V = Vfact1 * (Vfact2 - A)

        fact1 = M
        fact2 = k + (S**2) * (P0 * V0 / T0) * (Ta / (V**2))

        C = 2 * np.pi * np.sqrt(fact1 / fact2)
        return C

    axes = (('M', None, (30, 60), ('unif', None, None)),
            ('S', None, (0.005, 0.020), ('unif', None, None)),
            ('V_0', None, (0.002, 0.010), ('unif', None, None)),
            ('k', None, (1000, 5000), ('unif', None, None)),
            ('P_0', None, (90000, 110000), ('unif', None, None)),
            ('T_a', None, (290, 296), ('unif', 290, 296)),
            ('T_$', None, (340, 360), ('unif', None, None)))

    return function, axes


def get_dike(output='cost'):
    """Analytical model with many non-uniform variables.

    References:
        - http://statweb.stanford.edu/~owen/pubtalks/siamUQ.pdf, page 30

    """
    assert output in ('H', 'overflow', 'cost')

    def function(Xs, output):
        Q = Xs[:, 0]
        Ks = Xs[:, 1]
        Zv = Xs[:, 2]
        Zm = Xs[:, 3]
        Hd = Xs[:, 4]
        Cb = Xs[:, 5]
        L = Xs[:, 6]
        B = Xs[:, 7]

        H = (Q / (B * Ks * np.sqrt((Zm - Zv) / L))) ** (3. / 5)
        S = Zv + H - Hd - Cb

        if output == 'H':
            return H
        elif output == 'overflow':
            return S
        elif output == 'cost':
            return (S > 0) + (S <= 0) * (0.2 + 0.8 * (1 - np.exp(-1000/S**4))) + 0.05*np.minimum(Hd, 8)
        else:
            assert ValueError('Invalid output specification')

    axes = (('Q', None, (500.0, 3000.0), ('gumbel', 1013.0, 558.0)),
            ('K_s', None, (15.0, None), ('norm', 30.0, 8.0)),
            ('Z_v', None, (49.0, 51.0), ('isotriang', None, None)),
            ('Z_m', None, (54.0, 56.0), ('isotriang', None, None)),
            ('H_d', None, (7.0, 9.0), ('unif', None, None)),
            ('C_b', None, (55.0, 56.0), ('isotriang', None, None)),
            ('L', None, (4990.0, 5010.0), ('isotriang', None, None)),
            ('B', None, (295.0, 305.0), ('isotriang', None, None)))

    return functools.partial(function, output=output), axes


def get_fire_spread(wind_factor=1.0):
    """Returns the rate of spread and the reaction intensity of fire

    Args:
        :param delta: fuel depth
        :param sigma: fuel particle area-to-volume ratio
        :param h: fuel particle low heat content
        :param rho: ovendry particle density
        :param ml: moisture content of the live fuel
        :param md: moisture content of the dead fuel
        :param S: fuel particle total mineral content
        :param U: wind speed at midflame height
        :param tanphi: slope
        :param P: dead fuel loading vs. total loading

    Notes:
        Provided by: Eunhye Song <eunhyesong2016@u.northwestern.edu>

    References:
        - E. Song, B.L. Nelson, and J. Staum, 2016, Shapley effects for global
            sensitivity analysis: Theory and computation, SIAM/ASA Journal of
            Uncertainty Quantification, 4, 1060–1083.

    """
    def function(Xs):
        w0 = 1 / (1 + np.exp((15 - Xs[:, 0]) / 2)) / 4.8824
        # w0 = 0.95/(1+2.43*exp((15-X[1])*0.33))**(1/2.26) /4.8824
        delta = Xs[:, 0] / 30.48
        sigma = Xs[:, 1] * 30.48
        h = Xs[:, 2] * 0.4536 / 0.25
        rho = Xs[:, 3] / 0.48824
        ml = Xs[:, 4]
        md = Xs[:, 5]
        S = Xs[:, 6]
        U = Xs[:, 7] / 0.018288
        tanphi = Xs[:, 8]
        P = Xs[:, 9]

        rmax = sigma**1.5 / (495 + 0.0594 * sigma**1.5)
        bop = 3.348 * sigma**(-0.8189)
        # A =1/(4.774*sigma**(0.1) - 7.27)
        A = 133 * sigma**(-0.7913)
        thestar = (301.4 - 305.87 * (ml - md) + 2260 * md) / (2260 * ml)
        theta = np.minimum(1, np.maximum(thestar, 0))
        muM = np.exp(-7.3 * P * md - (7.3 * theta + 2.13) * (1 - P) * ml)

        # muM = exp(-2*(P*md + (1-P)*ml))

        # muM = min(max(0,1-2.59*(md/ml)+5.11*(md/ml)**2 - 3.52*(md/ml)**3),1)
        muS = np.minimum(0.174 * S**(-0.19), 1)
        C = 7.47 * np.exp(-0.133 * sigma**0.55)
        B = 0.02526 * sigma**0.54
        E = 0.715 * np.exp(-3.59 * 10**(-4) * sigma)
        # wn = w0/(1+S)
        wn = w0 * (1 - S)
        rhob = w0 / delta
        eps = np.exp(-138 / sigma)
        Qig = (401.41 + md * 2565.87) * 0.4536 / 1.060
        # Qig = 250 + 1116*md
        beta = rhob / rho
        r = rmax * (beta / bop)**A * np.exp(A * (1 - beta / bop))
        xi = ((192 + 0.2595 * sigma)**(-1) * np.exp((0.792 + 0.681 * sigma**0.5) * (beta + 0.1)))
        phiW = C * U**B * (beta / bop)**(-E)
        phiS = 5.275 * beta**(-0.3) * tanphi**2

        # Reaction intensity
        IR = r * wn * h * muM * muS
        # Rate of spread
        R = IR * xi * (1 + phiW + phiS) / (rhob * eps * Qig)

        # c(R*30.48/60)
        results = R * 30.48 / 60
        assert not np.any(np.isnan(results))

        return results

    axes = (('delta', None, None, ('lognorm', 2.19, 0.517)),
            ('sigma', None, (3.0 / 0.6, None), ('lognorm', 3.31, 0.294)),
            ('h', None, None, ('lognorm', 8.48, 0.063)),
            ('rho_p', None, None, ('lognorm', -0.592, 0.219)),
            ('m_l', None, (0.0, None), ('norm', 1.18, 0.377)),
            ('m_d', None, None, ('norm', 0.19, 0.047)),
            ('S_T', None, (0.0, None), ('norm', 0.049, 0.011)),
            ('U', None, None, ('lognorm', 1.0174, 0.5569, wind_factor)),
            ('tan_phi', None, (0.0, None), ('norm', 0.38, 0.186)),
            ('P', None, (None, 1.0), ('lognorm', -2.19, 0.64)))

    return function, axes
