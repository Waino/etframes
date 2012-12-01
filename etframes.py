"""
This module implements two graph types described in Edward Tufte's
"Visual Display of Quantitative Information".

Original author: Adam Hupp <adam@hupp.org>
Author of this fork: Stig-Arne Gronroos <stig.gronroos@gmail.com>
License: Distributed under the PSF license, http://www.python.org/psf/license/

"""
import matplotlib.pylab
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

from matplotlib.collections import LineCollection
from matplotlib.artist import Artist
from matplotlib.ticker import FixedLocator

__all__ = ["add_range_frame", "add_dot_dash_plot"]


def cleanframe_and_ticks(axes):
    """Removes frame around plot contents and removes redundant ticks"""

    # Turn off the default frame
    axes.set_frame_on(False)

    # Only show ticks on bottom and left frame
    axes.get_xaxis().tick_bottom()
    axes.get_yaxis().tick_left()


def interval_as_array(interval):
    """Backwards compatibility with pre-numpy intervals."""

    if callable(interval):
        tmp = interval()
        return np.array(tmp.get_bounds())
    else:
        return np.asarray(interval)


class RangeFrameArtist(Artist):
    """"Draws range frames on a graph"""

    def __init__(self, color, linewidth, xbounds, ybounds):
        """
        color: str indicating color of line
        linewidth: width of line to draw
        xbounds, ybounds: tuple (min,max) of data on x and y axis
        """
        Artist.__init__(self)
        self.color = color
        self.linewidth = linewidth
        self.xbounds = xbounds
        self.ybounds = ybounds

    def draw(self, renderer, *args, **kwargs):
        if not self.get_visible(): return

        rf = self.make_range_frame()
        for obj in rf:
            obj.draw(renderer)

    def make_range_frame(self):
        """ Constructs the component lines of the range frame """
        xtrans = transforms.blended_transform_factory(
            self.axes.transData, self.axes.transAxes
        )
        intervalx = interval_as_array(self.axes.dataLim.intervalx)

        ytrans = transforms.blended_transform_factory(
            self.axes.transAxes, self.axes.transData
        )
        intervaly = interval_as_array(self.axes.dataLim.intervaly)

        xline = LineCollection(
            segments=[[(intervalx[0], 0), (intervalx[1], 0)]],
            linewidths=[self.linewidth],
            colors=[self.color],
            transform=xtrans,
            zorder=10
        )
        yline = LineCollection(
            segments=[[(0, intervaly[0]), (0, intervaly[1])]],
            linewidths=[self.linewidth],
            colors=[self.color],
            transform=ytrans,
            zorder=10
        )

        return [xline, yline]


class BarChartArtist(Artist):
    """ Axis drawing artist for the simplified bar chart """
    def __init__(self, color=None, linewidth=None):
        """
        color: color to use for bottom line
        linewidth: width of bottom line
        """
        Artist.__init__(self)
        if color is None:
            color = (.5, .5, .5)
        if linewidth is None:
            linewidth = 3
        self.color = color
        self.linewidth = linewidth

    def draw(self, renderer, *args, **kwargs):
        if not self.get_visible(): return

        self.xminf, self.xmaxf = interval_as_array(self.axes.dataLim.intervalx)

        bottom = self.make_bottom_line()
        bottom.draw(renderer)

        self.clean_ticks()

    def make_bottom_line(self):
        """
        Makes a line at the bottom.
        FIXME: for some reason there is a single pixel glitch.
        """
        trans = transforms.blended_transform_factory(
            self.axes.transData, self.axes.transAxes
        )

        range_lines = LineCollection(
            segments=[[(self.xminf, 0), (self.xmaxf, 0)]],
            linewidths=[self.linewidth],
            colors=[self.color],
            transform=trans,
            zorder=0
        )
        return range_lines

    def clean_ticks(self):
        """ For this chart, we don't want ticks on either side, only labels """
        for tick in (
            self.axes.xaxis.get_major_ticks()
            + self.axes.xaxis.get_minor_ticks()
        ):
            tick.tick1On = False

        for tick in (
            self.axes.yaxis.get_major_ticks()
            + self.axes.yaxis.get_minor_ticks()
        ):
            tick.tick1On = False


def add_range_frame(
    axes=None, color="k", linewidth=1.0, xbounds=None, ybounds=None
):
    """
    Adds a range frame to a matplotlib graph.  The range frame is
    described in Tufte's "The Visual Display of Quantitative
    Information" p. 130.

    The range frame is an unobtrusive way of marking the minimum and
    maxiumum values on a scatterplot or other graph.

    axes: the matplotlib axes to apply a range frame to.  If None or
    unspecified, use the current axes

    color: string specification of the color. default is 'k', (black)

    linewidth: width of lines in range frame

    xbounds, ybounds: tuple (min,max) on x and y axes

    """

# Implementation detail: you might expect that the range of values is
# available via axes.dataLim.  Unfortunitely this range seems to
# extend .2 past the real min and max.

    if axes is None:
        axes = matplotlib.pylab.gca()

    axes.add_artist(RangeFrameArtist(
        color=color,
        linewidth=linewidth,
        xbounds=xbounds,
        ybounds=ybounds
    ))

    cleanframe_and_ticks(axes)


def add_dot_dash_plot(axes=None, xs=None, ys=None):
    """
    Add a dot-dash-plot to a matplotlib graph, as described on p. 133
    of Tufte's "The Visual Display of Quantitative Information".

    axes: axes to apply the dash-dot-plot to.  If None or unspecified,
    use the current axes.

    xs: a list of values along the x-axis to plot
    yx: a list of values along the y-axis to plot

    """

    if axes is None:
        axes = matplotlib.pylab.gca()

    if xs is not None:
        axes.xaxis.set_minor_locator(FixedLocator(xs))

    if ys is not None:
        axes.yaxis.set_minor_locator(FixedLocator(ys))

    cleanframe_and_ticks(axes)


def bar_chart(
    data, yticks, color=None, papercolor=None, linewidth=3, barwidth=.5
):
    """
    Plots a vector of values in a bar chart, as described on p. 128
    of Tufte's "The Visual Display of Quantitative Information".

    data: A vector of numerical values.
          Multiple data series are not supported.
    yticks: Positions of y-axis ticks and white grid lines.
            The user must explicitly set these, as it strongly affects the
            readability of the chart.

    Optional keyword arguments:
    color: color to use for the bars. Default: gray.
    papercolor: color of paper. Necessary for the white grid to work.
                Default: white.
    linewidth: width of white grid and bottom line.
    barwidth: width of the bars, as proportion [0,1]. Default: 0.5.
    """
    data = np.asarray(data)
    assert len(data.shape) == 1, 'This bar chart is only designed for univariate data'

    if color is None:
        color = (.5, .5, .5)
    if papercolor is None:
        papercolor = (1, 1, 1)

    plt.bar(
        range(len(data)), data,
        width=barwidth, align='center', color=color, edgecolor=color
    )
    axes = matplotlib.pylab.gca()
    cleanframe_and_ticks(axes)
    axes.set_xlim(-barwidth, len(data) - 1 + barwidth)
    axes.set_yticks(yticks)
    axes.add_artist(BarChartArtist())
    for tick in axes.xaxis.get_major_ticks() + axes.xaxis.get_minor_ticks():
        tick.tick1On = False
    for y in axes.yaxis.get_majorticklocs():
        if y == 0: continue
        plt.axhline(y, color=papercolor, linewidth=3)
