#! /usr/bin/python
# -*- coding: utf-8 -*-

import Gnuplot
from numpy import *

x = arange(256) * pi / 128
y1 = sin(x)
y2 = cos(x)
y3 = [1, 2, 3, 4, 5]

size = arange(105, 945, 105)
#size = [105, 210, 315, 420, 525, 630, 735, 840, 945]
pre  = ([48.54, 58.33, 61.07, 64.80, 59.76, 65.20, 64.78, 66.00, 65.08])
rec  = [40.73, 53.63, 59.68, 64.92, 60.48, 65.73, 64.11, 66.13, 65.73]

gp = Gnuplot.Gnuplot()

gp('set terminal postscript eps')
gp('set output "test.eps"')

gp('set multiplot layout 3, 2') # 縦、横
gp('set style data lines')

# PLOT ONLY Y
#gp.plot(y)
#gp.hardcopy('gpsample1.eps', eps=True, color=True, fontsize=24)


d1 = Gnuplot.Data(x, y1, title='sin(x)')
d2 = Gnuplot.Data(x, y2, title='cos(x)')

gp.plot(d1, xlabel='x', ylabel='y')

gp.plot(d2)

gp.plot(d1, d2,
        xrange='[0:6.3]',
        yrange='[-1.2:1.2]',
        title='This is title',
        xlabel='x-label',
        ylabel='y-label')

gp.plot(y3, yrange='[*:*]')

d3 = Gnuplot.Data(size, pre, title='precision')
#d4 = Gnuplot.Data(size, rec, title='recall')
gp.plot(pre)
