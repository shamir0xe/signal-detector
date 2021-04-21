import matplotlib.pyplot as plt
import numpy as np

class ShowGeometryPlot:
    @staticmethod
    def do(*args):
        sz = len(args)
        for i in range(sz):
            data = args[i]
            plt.subplot(sz, 1, i + 1)
            plt.plot(np.array([point.x for point in data]), np.array([point.y for point in data]), 'o-')
        plt.show()
        plt.pause(0.001)
