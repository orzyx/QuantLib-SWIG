
# Copyright (C) 2004 StatPro Italia srl
#
# This file is part of QuantLib, a free-software/open-source library
# for financial quantitative analysts and developers - http://quantlib.org/
#
# QuantLib is free software: you can redistribute it and/or modify it under the
# terms of the QuantLib license.  You should have received a copy of the
# license along with this program; if not, please email quantlib-dev@lists.sf.net
# The license is also available online at http://quantlib.org/html/license.html
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the license for more details.

from QuantLib import *

swaptionVols = [ # maturity,          length,             volatility
                 (Period(1, 'Year'),  Period(1,'Years'),  0.1810),
                 (Period(1, 'Year'),  Period(3,'Years'),  0.1590),
                 (Period(1, 'Year'),  Period(5,'Years'),  0.1400),
                 (Period(1, 'Year'),  Period(10,'Years'), 0.1220),
                 (Period(2, 'Years'), Period(5, 'Years'), 0.1290),
                 (Period(2, 'Years'), Period(7, 'Years'), 0.1230),
                 (Period(3, 'Years'), Period(5, 'Years'), 0.1201),
                 (Period(4, 'Years'), Period(4, 'Years'), 0.1189),
                 (Period(4, 'Years'), Period(5, 'Years'), 0.1146),
                 (Period(5, 'Years'), Period(3, 'Years'), 0.1183),
                 (Period(5, 'Years'), Period(5, 'Years'), 0.1108),
                 (Period(7, 'Years'), Period(2, 'Years'), 0.1110),
                 (Period(7, 'Years'), Period(5, 'Years'), 0.1040),
                 (Period(10,'Years'), Period(1, 'Year'),  0.1109),
                 (Period(10,'Years'), Period(5, 'Year'),  0.0977) ]

def formatVol(v, digits = 2):
    format = '%%.%df %%%%' % digits
    return format % (v * 100)

def formatPrice(p, digits = 2):
    format = '%%.%df %%%%' % digits
    return format % p

def calibrate(model, helpers, l, name):

    format = '%12s |%12s |%12s |%12s |%12s'
    header = format % ('maturity','length','volatility','implied','error')
    rule = '-' * len(header)
    dblrule = '=' * len(header)

    print
    print dblrule
    print name
    print rule

    method = Simplex(l, 1.0e-9);
    method.setEndCriteria(EndCriteria(1000, 1.0e-7));
    model.calibrate(helpers, method);

    print 'Parameters: %s' % model.params()
    print rule

    print header
    print rule

    totalError = 0.0
    for swaption, helper in zip(swaptionVols, helpers):
        maturity, length, vol = swaption
        NPV = helper.modelValue()
        implied = helper.impliedVolatility(NPV, 1.0e-4, 1000, 0.05, 0.50)
        error = implied - vol
        totalError += abs(error)
        print format % (maturity, length,
                        formatVol(vol,4), formatVol(implied,4),
                        formatVol(error,4))
    averageError = totalError/len(helpers)

    print rule
    format = '%%%ds' % len(header)
    print format % ('Average error: ' + formatVol(averageError,4))
    print dblrule

todaysDate = Date(15,2,2002)
Settings.instance().evaluationDate = todaysDate
calendar = TARGET()
settlementDate = Date(19,2,2002);

settlementDays = 2
dayCounter = Thirty360()
depositHelpers = [ DepositRateHelper(QuoteHandle(SimpleQuote(rate)),
                                     n, unit, settlementDays,
                                     calendar, 'mf', dayCounter)
                   for n, unit, rate in [(1, 'week',   0.03295),
                                         (1, 'month',  0.0331),
                                         (3, 'months', 0.0329),
                                         (6, 'months', 0.0333),
                                         (9, 'months', 0.0341),
                                         (1, 'year',   0.0353)] ]

fixedLegFrequency = 1
fixedLegAdjustment = 'unadjusted'
fixedLegDayCounter = Thirty360()
floatingLegFrequency = 2
floatingLegAdjustment = 'modifiedfollowing'
swapHelpers = [ SwapRateHelper(QuoteHandle(SimpleQuote(rate)),
                               n, unit, settlementDays, calendar,
                               fixedLegFrequency, fixedLegAdjustment,
                               fixedLegDayCounter, floatingLegFrequency,
                               floatingLegAdjustment)
                for n, unit, rate in [(2,  'years', 0.04875),
                                      (3,  'years', 0.0438),
                                      (5,  'years', 0.0474325),
                                      (10, 'years', 0.051825),
                                      (20, 'years', 0.0545125)] ]

termStructure = YieldTermStructureHandle()
termStructure.linkTo(PiecewiseFlatForward(settlementDate,
                                          depositHelpers+swapHelpers))


# define the ATM/OTM/ITM swaps

payFixed = 1
fixingDays = 2
swapStart = settlementDate.plusYears(1)
index = Euribor(6, 'months', termStructure)
swapLength = 5
swapEnd = swapStart.plusYears(swapLength)

fixedSchedule = Schedule(calendar, swapStart, swapEnd,
                         fixedLegFrequency, fixedLegAdjustment)
floatingSchedule = Schedule(calendar, swapStart, swapEnd,
                            floatingLegFrequency, floatingLegAdjustment)

atmRate = SimpleSwap(payFixed, 100.0,
                     fixedSchedule, 0.0, fixedLegDayCounter,
                     floatingSchedule, index, fixingDays, 0.0,
                     termStructure).fairRate()

atmSwap = SimpleSwap(payFixed, 100.0,
                     fixedSchedule, atmRate, fixedLegDayCounter,
                     floatingSchedule, index, fixingDays, 0.0,
                     termStructure)
otmSwap = SimpleSwap(payFixed, 100.0,
                     fixedSchedule, atmRate*1.2, fixedLegDayCounter,
                     floatingSchedule, index, fixingDays, 0.0,
                     termStructure)
itmSwap = SimpleSwap(payFixed, 100.0,
                     fixedSchedule, atmRate*0.8, fixedLegDayCounter,
                     floatingSchedule, index, fixingDays, 0.0,
                     termStructure)

helpers = [ SwaptionHelper(maturity, length,
                           QuoteHandle(SimpleQuote(vol)),
                           index, termStructure)
            for maturity, length, vol in swaptionVols ]

times = {}
for h in helpers:
    for t in h.times():
        times[t] = 1
times = times.keys()
times.sort()

grid = TimeGrid(times)

HW = HullWhite(termStructure)
HW2 = HullWhite(termStructure)
BK = BlackKarasinski(termStructure)

print "Calibrating..."

for h in helpers:
    h.setPricingEngine(JamshidianSwaptionEngine(HW))
calibrate(HW, helpers, 0.05, "Hull-White (analytic formulae)")

for h in helpers:
    h.setPricingEngine(TreeSwaptionEngine(HW2,grid))
calibrate(HW2, helpers, 0.05, "Hull-White (numerical calibration)")

for h in helpers:
    h.setPricingEngine(TreeSwaptionEngine(BK,grid))
calibrate(BK, helpers, 0.05, "Black-Karasinski (numerical calibration)")


# price Bermudan swaptions on defined swaps

schedule = Schedule(calendar, swapStart, swapEnd, 1, 'mf')
bermudanDates = [ d for d in schedule ]
exercise = BermudanExercise(bermudanDates[:-1])

format = '%17s |%17s |%17s |%17s'
header = format % ('model', 'in-the-money', 'at-the-money', 'out-of-the-money')
rule = '-' * len(header)
dblrule = '=' * len(header)

print
print dblrule
print 'Pricing Bermudan swaptions...'
print rule
print header
print rule

atmSwaption = Swaption(atmSwap, exercise, termStructure,
                       TreeSwaptionEngine(HW, 100))
otmSwaption = Swaption(otmSwap, exercise, termStructure,
                       TreeSwaptionEngine(HW, 100))
itmSwaption = Swaption(itmSwap, exercise, termStructure,
                       TreeSwaptionEngine(HW, 100))

print format % ('HW analytic', formatPrice(itmSwaption.NPV()),
                formatPrice(atmSwaption.NPV()), formatPrice(otmSwaption.NPV()))

atmSwaption.setPricingEngine(TreeSwaptionEngine(HW2, 100))
otmSwaption.setPricingEngine(TreeSwaptionEngine(HW2, 100))
itmSwaption.setPricingEngine(TreeSwaptionEngine(HW2, 100))

print format % ('HW numerical', formatPrice(itmSwaption.NPV()),
                formatPrice(atmSwaption.NPV()), formatPrice(otmSwaption.NPV()))

atmSwaption.setPricingEngine(TreeSwaptionEngine(BK, 100))
otmSwaption.setPricingEngine(TreeSwaptionEngine(BK, 100))
itmSwaption.setPricingEngine(TreeSwaptionEngine(BK, 100))

print format % ('BK numerical', formatPrice(itmSwaption.NPV()),
                formatPrice(atmSwaption.NPV()), formatPrice(otmSwaption.NPV()))

print dblrule
