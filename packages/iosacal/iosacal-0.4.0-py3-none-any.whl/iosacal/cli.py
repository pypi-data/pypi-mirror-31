#! /usr/bin/env python
# -*- coding: utf-8 -*-
# filename: cli.py
# Copyright 2018 Stefano Costa <steko@iosa.it>
#
# This file is part of IOSACal, the IOSA Radiocarbon Calibration Library.

# IOSACal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# IOSACal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with IOSACal.  If not, see <http://www.gnu.org/licenses/>.

import sys
import pkg_resources

from optparse import OptionParser, OptionGroup

from iosacal import core, plot, text


usage = "usage: %prog -d DATE -s SIGMA --id ID [other options] ..."

parser = OptionParser(usage = usage)
parser.add_option("-d", "--date",
                action="append",
                type="int",
                dest="date",
                help="non calibrated radiocarbon BP date for sample",
                metavar="DATE")
parser.add_option("-s", "--sigma",
                action="append",
                type="int",
                dest="sigma",
                help="standard deviation for date",
                metavar="SIGMA")
parser.add_option("--id",
                  action="append",
                  type="str",
                  dest="id",
                  metavar="ID",
                  help="sample identification")
parser.add_option("-p", "--plot",
                  default=False,
                  dest="plot",
                  action="store_true",
                  help="output results to graphic plot")
parser.add_option("-c", "--curve",
                  default="intcal13",
                  type="str",
                  dest="curve",
                  help="calibration curve to be used [default: %default]")
parser.add_option("-o", "--oxcal",
                  action="store_true",
                  dest="oxcal",
                  default=False,
                  help="draw plots more OxCal-like looking [default: %default]")
parser.add_option("-n", "--name",
                  default="iosacal",
                  type="str",
                  dest="name",
                  help="name of output image [default: %default]")
group0 = OptionGroup(parser, 'Single and multiple plots',
                    'Use these two options when more than 1 sample is supplied'
                    'to determine which output is generated.')
group0.add_option("-1", "--single",
                action="store_true",
                default=True,
                dest="single",
                help="generate single plots for each sample")
group0.add_option("--no-single",
                action="store_false",
                dest="single",
                help="don't generate single plots for each sample")
group0.add_option("-m", "--stacked",
                action="store_true",
                default=False,
                dest="stacked",
                help="generate stacked plot with all samples")
parser.add_option_group(group0)
group = OptionGroup(parser, 'BP or BC/AD output',
                    'Use these two mutually exclusive options to choose which '
                    ' type of dates you like as output.')
parser.set_defaults(BP='bp')
group.add_option("--bp",
                action="store_const",
                dest="BP",
                const='bp',
                help="express date in Calibrated BP Age (default action)")
group.add_option("--ad",
                action="store_const",
                dest="BP",
                const='ad',
                help="express date in Calibrated BC/AD Calendar Age")
group.add_option("--ce",
                action="store_const",
                dest="BP",
                const='ce',
                help="express date in Calibrated BCE/CE Calendar Age")
parser.add_option_group(group)

(options, args) = parser.parse_args()
if not (options.date and options.sigma):
    parser.error('Please provide date and standard deviation')
if len(options.date) != len(options.sigma):
    parser.error('Mismatch in number of dates and standard deviation values')
if options.id is None:
    options.id = ['Determination #{}'.format(n) for n in range(len(options.date))]
if len(options.id) != len(options.date):
    parser.error('Mismatch in number of dates and ID values')


def main():
    """Main program procedure.

    By default produces text output to stdout for each sample."""

    # resource_string actually returns bytes
    curve_filename = pkg_resources.resource_filename("iosacal", "data/%s.14c" % options.curve)
    curve = core.CalibrationCurve(curve_filename)
    calibrated_ages = []
    for d, s, id in zip(options.date, options.sigma, options.id):
        rs = core.R(d, s, id)
        ca = rs.calibrate(curve)
        calibrated_ages.append(ca)
        if options.plot and options.single is True:
            outputname = '{}_{:d}_{:d}.pdf'.format(id, d, s)
            plot.single_plot(ca, oxcal=options.oxcal, output=outputname, BP=options.BP)
        else:
            sys.stdout.write(text.single_text(ca, options.BP))
    if options.plot and options.stacked is True:
        plot.stacked_plot(
                        calibrated_ages,
                        oxcal=options.oxcal,
                        name=options.name,
                        output='{}.pdf'.format(options.name)
                        )

if __name__ == '__main__':
    main()
