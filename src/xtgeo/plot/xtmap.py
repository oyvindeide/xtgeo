"""Module for map plots of surfaces, using matplotlib."""

from __future__ import print_function, division, absolute_import

import matplotlib.pyplot as plt
import matplotlib.patches as mplp
from matplotlib import ticker
import numpy as np
import numpy.ma as ma
import six

from xtgeo.common import XTGeoDialog
from xtgeo.plot.baseplot import BasePlot

xtg = XTGeoDialog()
logger = xtg.functionlogger(__name__)


class Map(BasePlot):
    """Class for plotting a map, using matplotlib."""

    def __init__(self):
        """The __init__ (constructor) method for a Map object."""

        super(Map, self).__init__()

        clsname = "{}.{}".format(type(self).__module__, type(self).__name__)
        logger.info(clsname)

        self._wells = None
        self._surface = None
        self._tight = False

        self._pagesize = 'A4'
        self._wfence = None
        self._showok = True  # to indicate if plot is OK to show
        self._legendtitle = "Map"

    # =========================================================================
    # Properties
    # =========================================================================
    @property
    def pagesize(self):
        """ Returns page size."""
        return self._pagesize

    # =========================================================================
    # Functions methods (public)
    # =========================================================================

    def canvas(self, title=None, subtitle=None, infotext=None,
               figscaling=1.0):
        """Prepare the canvas to plot on, with title and subtitle.

        Args:
            title (str, optional): Title of plot.
            subtitle (str, optional): Sub title of plot.
            infotext (str, optional): Text to be written as info string.
            figscaling (str, optional): Figure scaling, default is 1.0


        """
        # self._fig, (ax1, ax2) = plt.subplots(2, figsize=(11.69, 8.27))
        self._fig, self._ax = plt.subplots(figsize=(11.69 * figscaling,
                                                    8.27 * figscaling))
        if title is not None:
            plt.title(title, fontsize=18)
        if subtitle is not None:
            self._ax.set_title(subtitle, size=14)
        if infotext is not None:
            self._fig.text(0.01, 0.02, infotext, ha='left', va='center',
                           fontsize=8)

    def plot_surface(self, surf, minvalue=None, maxvalue=None,
                     contourlevels=None, xlabelrotation=None,
                     colormap=None, logarithmic=False):
        """Input a surface and plot it."""

        # need a deep copy to avoid changes in the original surf

        usesurf = surf.copy()
        if (abs(surf.rotation) > 0.001):
            usesurf.unrotate()

        xi, yi, zi = usesurf.get_xyz_values()

        zimask = ma.getmaskarray(zi).copy()  # yes need a copy!

        legendticks = None
        if minvalue is not None and maxvalue is not None:
            minv = float(minvalue)
            maxv = float(maxvalue)

            step = (maxv - minv) / 10.0
            legendticks = []
            for i in range(10 + 1):
                llabel = float('{0:9.4f}'.format(minv + step * i))
                legendticks.append(llabel)

            zi.unshare_mask()
            zi[zi < minv] = minv
            zi[zi > maxv] = maxv

            # need to restore the mask:
            zi.mask = zimask

            # note use surf.min, not usesurf.min here ...
            notetxt = ('Note: map values are truncated from [' +
                       str(surf.values.min()) + ', ' +
                       str(surf.values.max()) + '] ' +
                       'to interval [' +
                       str(minvalue) + ', ' + str(maxvalue) + ']')

            self._fig.text(0.99, 0.02, notetxt, ha='right', va='center',
                           fontsize=8)

        logger.info('Legendticks: {}'.format(legendticks))

        if minvalue is None:
            minvalue = usesurf.values.min()

        if maxvalue is None:
            maxvalue = usesurf.values.max()

        if colormap is not None:
            self.colormap = colormap
        else:
            self.colormap = 'rainbow'

        levels = np.linspace(minvalue, maxvalue, self.contourlevels)
        logger.debug('Number of contour levels: {}'.format(levels))

        plt.setp(self._ax.xaxis.get_majorticklabels(), rotation=xlabelrotation)

        # zi = ma.masked_where(zimask, zi)
        # zi = ma.masked_greater(zi, _cxtgeo.UNDEF_LIMIT)

        if ma.std(zi) > 1e-07:
            uselevels = levels
        else:
            uselevels = 1

        try:
            if logarithmic is False:
                locator = None
                ticks = legendticks
                im = self._ax.contourf(xi, yi, zi, uselevels, locator=locator,
                                       cmap=self.colormap)

            else:
                logger.info('use LogLocator')
                locator = ticker.LogLocator()
                ticks = None
                uselevels = None
                im = self._ax.contourf(xi, yi, zi, locator=locator,
                                       cmap=self.colormap)

            self._fig.colorbar(im, ticks=ticks)
        except ValueError as err:
            logger.warning('Could not make plot: {}'.format(err))

        plt.gca().set_aspect('equal', adjustable='box')

    def plot_faults(self, fpoly, idname='POLY_ID', color='k', edgecolor='k',
                    alpha=0.7, linewidth=0.8):
        """Plot the faults

        Args:
            fpoly (object): A XTGeo Polygons object
            idname (str): Name of column which has the faults ID
            color (c): Fill color model c according to Matplotlib_
            edgecolor (c): Edge color according to Matplotlib_
            alpha (float): Degree of opacity
            linewidth (float): Line width

        .. _Matplotlib: http://matplotlib.org/api/colors_api.html
        """

        aff = fpoly.dataframe.groupby(idname)

        for name, group in aff:

            # make a dataframe sorted on faults (groupname)
            myfault = aff.get_group(name)

            # make a list [(X,Y) ...]; note PY3 need the
            # list before the zip!
            if six.PY3:
                af = list(zip(myfault['X_UTME'].values,
                              myfault['Y_UTMN'].values))
            else:
                # make a numpy (X,Y) list from pandas series
                af = myfault[['X_UTME', 'Y_UTMN']].values

            p = mplp.Polygon(af, alpha=0.7, color=color, ec=edgecolor,
                             lw=linewidth)

            if p.get_closed():
                self._ax.add_artist(p)
            else:
                print("A polygon is not closed...")

    def plot_points(self, points):
        """Plot a points set on the map.

        This can be be useful e.g. for plotting the underlying point set
        that makes a gridded map.

        Args:
            points (Points): A XTGeo Points object X Y VALUE

        """

        # This function is "in prep"

        dataframe = points.dataframe

        self._ax.scatter(dataframe['X_UTME'].values,
                         dataframe['Y_UTMN'].values, marker='x')

        #print(dataframe)


    def show(self):
        """Call to matplotlib.pyplot show().

        Returns:
            True of plotting is done; otherwise False
        """
        if self._tight:
            self._fig.tight_layout()

        if self._showok:
            logger.info('Calling plt show method...')
            plt.show()
            return True
        else:
            logger.warning("Nothing to plot (well outside Z range?)")
            return False

    def savefig(self, filename, fformat='png'):
        """Call to matplotlib.pyplot savefig().

        Returns:
            True of plotting is done; otherwise False
        """
        if self._tight:
            self._fig.tight_layout()

        if self._showok:
            plt.savefig(filename, format=fformat)
            plt.close(self._fig)
            return True
        else:
            logger.warning("Nothing to plot (well outside Z range?)")
            return False