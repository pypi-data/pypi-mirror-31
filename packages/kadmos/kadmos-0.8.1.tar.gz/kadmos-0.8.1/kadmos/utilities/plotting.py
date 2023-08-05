import math
import matplotlib.pyplot as plt


class AnnoteFinder(object):
    """Callback for matplotlib to display an annotation when points are clicked on.

    The point which is closest to the click and within
    xtol and ytol is identified.

    Register this function like this:

    scatter(xdata, ydata)
    af = AnnoteFinder(xdata, ydata, annotes)
    connect('button_press_event', af)
    """

    def __init__(self, xdata, ydata, annotes, ax=None, xtol=None, ytol=None):
        self.data = list(zip(xdata, ydata, annotes))
        if xtol is None:
            xtol = ((max(xdata) - min(xdata))/float(len(xdata)))/2
        if ytol is None:
            ytol = ((max(ydata) - min(ydata))/float(len(ydata)))/2
        self.xtol = xtol
        self.ytol = ytol
        if ax is None:
            self.ax = plt.gca()
        else:
            self.ax = ax
        self.drawnAnnotations = {}
        self.links = []

    # noinspection PyMethodMayBeStatic
    def distance(self, x1, x2, y1, y2):
        """Return the distance between two points"""
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def __call__(self, event):
        if event.inaxes:
            click_x = event.xdata
            click_y = event.ydata
            if (self.ax is None) or (self.ax is event.inaxes):
                annotes = []
                # print(event.xdata, event.ydata)
                for x, y, a in self.data:
                    # print(x, y, a)
                    if ((click_x-self.xtol < x < click_x+self.xtol) and
                            (click_y-self.ytol < y < click_y+self.ytol)):
                        annotes.append(
                            (self.distance(x, click_x, y, click_y), x, y, a))
                if annotes:
                    annotes.sort()
                    distance, x, y, annote = annotes[0]
                    self.drawAnnote(event.inaxes, x, y, annote)
                    for l in self.links:
                        l.drawSpecificAnnote(annote)

    def drawAnnote(self, ax, x, y, annote):
        """Draw the annotation on the plot"""
        if (x, y) in self.drawnAnnotations:
            markers = self.drawnAnnotations[(x, y)]
            for m in markers:
                m.set_visible(not m.get_visible())
            self.ax.figure.canvas.draw_idle()
        else:
            t = ax.text(x, y, " - %s" % annote,)
            m = ax.scatter([x], [y], marker='d', c='r', zorder=100)
            self.drawnAnnotations[(x, y)] = (t, m)
            self.ax.figure.canvas.draw_idle()

    def drawSpecificAnnote(self, annote):
        annotes_to_draw = [(x, y, a) for x, y, a in self.data if a == annote]
        for x, y, a in annotes_to_draw:
            self.drawAnnote(self.ax, x, y, a)
