import os
import time
from matplotlib import pyplot as plt


if __name__ == '__main__':
    start = time.time()

    graph_path = "retraining_graph.png"
    if os.path.exists(graph_path):
        os.remove(graph_path)

    data_points = open("retraining.txt", "r").readlines()
    data_X = list(map(lambda x: int(x.split()[0]), data_points))
    data_Y = list(map(lambda y: float(y.split()[1]), data_points))
    plt.plot(data_X, data_Y)

    plt.title("Retraining Performance")
    plt.xlabel("Number of trainings")
    plt.ylabel("Files transcribed")
    plt.savefig(graph_path, dpi=120)
