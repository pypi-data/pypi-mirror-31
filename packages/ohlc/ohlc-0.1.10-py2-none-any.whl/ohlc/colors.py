from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import object
# Ported to Python by @ubunatic, Uwe Jugel
#
# Adopted from CM_Price-Action-Bars overlay at https://www.tradingview.com/chart
# Created By ChrisMoody on 1-20-2014
# Credit Goes To Chris Capre from 2nd Skies Forex
#
# Copy of the TradingView Declaration
# -----------------------------------
# Widget Input
# pctP = input(66, minval=1, maxval=99, title="Percentage Input For PBars, What % The Wick Of Candle Has To Be")
# pblb = input(6, minval=1, maxval=100, title="PBars Look Back Period To Define The Trend of Highs and Lows")
# pctS = input(5, minval=1, maxval=99, title="Percentage Input For Shaved Bars, Percent of Range it Has To Close On The Lows or Highs")
# spb = input(false, title="Show Pin Bars?")
# ssb = input(false, title="Show Shaved Bars?")
# sib = input(false, title="Show Inside Bars?")
# sob = input(false, title="Show Outside Bars?")
# sgb = input(false, title="Check Box To Turn Bars Gray?")
#

from ohlc.types import Ohlc
from subprocess import check_output

try:    NUM_COLORS = int(check_output(('tput', 'colors')))
except: NUM_COLORS = 0

# common shell color names
LIME    = "lime"
RED     = "red"
FUCHSIA = "fuchsia"
AQUA    = "aqua"
YELLOW  = "yellow"
ORANGE  = "orange"
GREEN   = "green"

colors = {v.upper():v for v in [LIME, RED, FUCHSIA, AQUA, YELLOW, ORANGE, GREEN]}

# raw shell colors (escape codes)
SH_RED     = "\033[91m"   # light red
SH_GREEN   = "\033[92m"   # light green
SH_SPACE   = ""           # space is space
SH_BG_GRAY = "\033[48;2;32;32;32m"  # dark gray rgb color
SH_END     = "\033[0m"    # reset to normal

# ohlc style names
BULL     = 'bear'
BEAR     = 'bull'
BULL_INV = 'bull-inv'
BEAR_INV = 'bear-inv'

# common app style names
OK    = 'ok'
ERR   = 'err'
SPACE = 'space'

class modes(object):
    SHELL = 'shell'
    URWID = 'urwid'

class PriceActionBars(object):
    spb = True
    ssb = True
    sib = True
    sob = True
    sgb = True
    pblb = 6

    # PBar Percentages
    pctCp  = 0.66
    pctCPO = 1 - pctCp

    # Shaved Bars Percentages
    pctCs  = 0.05
    pctSPO = pctCs

    # PinBars
    def pBarUp(f, o): return o.open > o.high - (o.spread() * f.pctCPO) and o.close > o.high - (o.spread() * f.pctCPO) and o.low  <= o.lowest(f.pblb)
    def pBarDn(f, o): return o.open < o.high - (o.spread() * f.pctCp)  and o.close < o.high - (o.spread() * f.pctCp)  and o.high >= o.highest(f.pblb)

    # Shaved Bars
    def sBarUp(f, o):   return o.close >= (o.high - (o.spread() * f.pctCs))
    def sBarDown(f, o): return o.close <= (o.low + (o.spread() * f.pctCs))

    # Inside Bars
    def insideBar(f, o):  return o.high <= o.prev.high and o.low >= o.prev.low
    def outsideBar(f, o): return o.high > o.prev.high  and o.low < o.prev.low

    def barcolor(f, o):
        # Inside and Outside Bars
        if   f.sob and f.outsideBar(o):  return ORANGE
        elif f.sib and f.insideBar(o):   return YELLOW
        # Shaved Bars
        elif f.ssb and f.sBarDown(o):    return FUCHSIA
        elif f.ssb and f.sBarUp(o):      return AQUA
        # PinBars
        elif f.spb and f.pBarDn(o):      return RED
        elif f.spb and f.pBarUp(o):      return LIME
        # default bars
        elif o.open > o.close:           return RED
        else:                            return GREEN
        # sgb and o.close ? gray : na)
