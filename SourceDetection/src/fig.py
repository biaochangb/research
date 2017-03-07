# coding=utf-8
"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/9.
"""

import matplotlib.pyplot as plt
import numpy as np


class Fig:
    """drawing figs according to the experiment results."""
    colors = {'RC': '#00008f', 'DC': '#0070ff', 'JC': '#00dfff', 'RI': '#bfff40', 'DI': '#ffcf00',
              'DMP': '#ff6000', 'GSBA-JC': '#ef0000', 'BFSA-RC': '#800000', 'GSBA-U': '#696969', 'GSBA-RC': '#bfff40',
              'GSBA-DC': '#ffcf00', 'GSBA-RI': '#bfff40', 'GSBA-DMP': '#ff6000'}
    markers = {'RC': '.', 'DC': '*', 'JC': 'o', 'RI': 'p', 'DI': '+',
               'DMP': 'x', 'GSBA-JC': 's', 'BFSA-RC': '^', 'GSBA-U': '>', 'GSBA-RC': '.', 'GSBA-DC': '*',
               'GSBA-RI': 'p', 'GSBA-DMP': 'x'}
    # hatchs = {'GSBA-RC':'','GSBA-DC','GSBA-JC'}
    debug = False

    def bars(self, x, y, legend, xlabel, ylabel, title='', path=None):
        n = len(legend)
        width = 0.4  # the width of the bars
        index = np.arange(len(x))
        fig, ax = plt.subplots(figsize=(11, 8))
        for i in np.arange(0, n):
            if legend[i].startswith('GSBA'):
                ax.bar(index + i * width * 2 / n + 0.1, y[i], width * 2 / n,
                       label=legend[i], color=self.colors[legend[i]], hatch='')
            else:
                ax.bar(index + i * width * 2 / n + 0.1, y[i], width * 2 / n, label=legend[i], color=self.colors[legend[i]])
        plt.xlabel(xlabel, fontsize=30)
        plt.ylabel(ylabel, fontsize=30)
        # plt.title('Scores by group and Category')

        plt.xticks(index + width + 0.1, x, fontsize=28)
        plt.yticks(fontsize=28)  # change the num axis size
        # plt.xlim(0, 50)  # The ceil
        y_min = np.min(y)
        y_max = np.max(y)
        plt.ylim(0.8 * y_min, 1.25 * y_max)  # The ceil
        plt.legend(loc=1, ncol=n / 2, mode="expand", borderaxespad=0., fontsize=26)
        plt.tight_layout()
        if path is not None:
            fig.savefig(path)
        if self.debug:
            plt.show()

    def lines(self, x, y, legend, xlabel, ylabel, title='', path=None):
        n = len(legend)
        width = 3
        fig, ax = plt.subplots(figsize=(16, 8))
        for i in np.arange(0, n):
            print y[i]
            ax.plot(x, y[i], '-D', label=legend[i], color=self.colors[legend[i]], linewidth=width,
                    markersize=10, marker=self.markers[legend[i]], markeredgewidth=2)
        plt.xlabel(xlabel, fontsize=26)
        plt.ylabel(ylabel, fontsize=26)
        # plt.title('Scores by group and Category')

        plt.xticks(fontsize=24)
        plt.yticks(fontsize=24)  # change the num axis size
        # plt.xlim(0, 50)  # The ceil
        y_min = np.min(y)
        y_max = np.max(y)
        x_max = np.max(x)
        x_min = np.min(x)
        plt.xlim(x_min - 0.2, x_max + 0.2)
        plt.ylim(y_min - 0.2, 1.1 * y_max)  # The ceil
        plt.legend(loc=1, ncol=n, mode="expand", borderaxespad=0., fontsize=24)
        plt.tight_layout()
        if path is not None:
            fig.savefig(path)

    def test(self, base_path):
        x = np.arange(5, 11, 1)
        methods = ['GSBA-U', 'GSBA-RC', 'GSBA-DC', 'GSBA-JC', 'GSBA-RI', 'GSBA-DMP']
        m = 6
        xlable = 'The number of observed infected nodes, N'
        y = [[0.51, 0.48, 0.54, 0.43, 0.4, 0.44],
             [0.67, 0.49, 0.55, 0.5, 0.4, 0.45],
             [0.57, 0.46, 0.51, 0.45, 0.38, 0.48],
             [0.58, 0.47, 0.51, 0.43, 0.4, 0.47],
             [0.57, 0.45, 0.53, 0.45, 0.38, 0.47],
             [0.66, 0.59, 0.66, 0.62, 0.51, 0.61]]
        ylabel = 'Detection Rate'
        path = base_path + 'test.pdf'
        self.bars(x, y[0:m], methods[0:m], xlable, ylabel, path=path)

    def effect_of_different_priors(self, base_path):
        x = np.arange(20, 46, 5)
        methods = ['RC', 'DC', 'JC', 'GSBA-RC', 'GSBA-DC', 'GSBA-JC']
        m = len(methods)
        xlable = 'The number of observed infected nodes, N'
        y = [[0.092086622, 0.075288403, 0.069216758, 0.063145112, 0.047763611, 0.043108682],
             [0.087634082, 0.069823922, 0.060716454, 0.052823315, 0.044930176, 0.042096742],
             [0.113337381, 0.087634082, 0.075490791, 0.07124064, 0.062133171, 0.049989881],
             [0.156243675, 0.126087836, 0.114754098, 0.107468124, 0.087634082, 0.081562437],
             [0.17911354, 0.148755313, 0.132564258, 0.118801862, 0.101801255, 0.094312892],
             [0.182756527, 0.150779194, 0.133171423, 0.119409027, 0.102003643, 0.093300951], ]
        ylabel = 'Detection Rate'
        path = base_path + 'power-grid-prior-full-rate.pdf'
        self.bars(x, y[0:m], methods[0:m], xlable, ylabel, path=path)

        y = [[1.859542603, 2.085205424, 2.253187614, 2.37259664, 2.522363894, 2.649868448],
             [1.865614248, 2.082169601, 2.252985226, 2.370977535, 2.505768063, 2.611009917],
             [1.878567092, 2.082169601, 2.263711799, 2.388990083, 2.520340012, 2.654523376],
             [1.57842542, 1.793159279, 1.939688322, 2.077109897, 2.247723133, 2.346893341],
             [1.659380692, 1.864197531, 2.03339405, 2.160089051, 2.359036632, 2.439587128],
             [1.652499494, 1.866828577, 2.030965392, 2.158065169, 2.360858126, 2.44161101], ]
        ylabel = 'Detection Error'
        path = base_path + 'power-grid-prior-full-error.pdf'
        self.bars(x, y[0:m], methods[0:m], xlable, ylabel, path=path)

        y = [[0.437543007, 0.43623558, 0.439141874, 0.431555209, 0.434036632, 0.434774787],
             [0.42157458, 0.41896782, 0.42340282, 0.417411166, 0.418594414, 0.416177562],
             [0.408490184, 0.402558187, 0.402158807, 0.395877064, 0.393336369, 0.392444175],
             [0.306274034, 0.301420765, 0.301369493, 0.294463238, 0.294960534, 0.292608334],
             [0.267364906, 0.2608136, 0.25804493, 0.251001821, 0.250875329, 0.246765162],
             [0.264480874, 0.258708763, 0.256068272, 0.249197675, 0.248709775, 0.245330455], ]
        ylabel = 'Detection Ranking'
        path = base_path + 'power-grid-prior-full-ranking.pdf'
        self.bars(x, y[0:m], methods[0:m], xlable, ylabel, path=path)

        x = np.arange(5, 11, 1)
        y = [[0.33, 0.304, 0.27, 0.256, 0.212, 0.182],
             [0.332, 0.302, 0.266, 0.244, 0.22, 0.18],
             [0.324, 0.33, 0.286, 0.304, 0.312, 0.292],
             [0.584, 0.546, 0.514, 0.508, 0.488, 0.426],
             [0.568, 0.496, 0.498, 0.442, 0.45, 0.404],
             [0.572, 0.5, 0.514, 0.468, 0.468, 0.408], ]
        ylabel = 'Detection Rate'
        path = base_path + 'scale-free-prior-full-rate.pdf'
        self.bars(x, y[0:m], methods[0:m], xlable, ylabel, path=path)

        y = [[0.71, 0.76, 0.802, 0.882, 0.918, 1.032],
             [0.706, 0.77, 0.806, 0.912, 0.902, 1.016],
             [0.74, 0.744, 0.792, 0.83, 0.84, 0.914],
             [0.458, 0.518, 0.542, 0.584, 0.616, 0.696],
             [0.532, 0.63, 0.684, 0.784, 0.762, 0.864],
             [0.514, 0.632, 0.656, 0.742, 0.74, 0.87], ]
        ylabel = 'Detection Error'
        path = base_path + 'scale-free-prior-full-error.pdf'
        self.bars(x, y[0:m], methods[0:m], xlable, ylabel, path=path)

        y = [[0.4648, 0.427, 0.408857143, 0.38525, 0.362, 0.3656],
             [0.4464, 0.406333333, 0.400857143, 0.38825, 0.372, 0.3814],
             [0.4528, 0.405666667, 0.388285714, 0.37275, 0.348444444, 0.3522],
             [0.316, 0.282, 0.261428571, 0.245, 0.219555556, 0.2232],
             [0.3224, 0.298333333, 0.273714286, 0.26325, 0.236222222, 0.24],
             [0.3204, 0.297333333, 0.271428571, 0.25825, 0.233111111, 0.2356], ]
        ylabel = 'Detection Ranking'
        path = base_path + 'scale-free-prior-full-ranking.pdf'
        self.bars(x, y[0:m], methods[0:m], xlable, ylabel, path=path)


if __name__ == '__main__':
    base_path = '../data/fig/'
    fig = Fig()
    fig.debug = False
    if fig.debug:
        fig.test(base_path)
    fig.effect_of_different_priors(base_path)
