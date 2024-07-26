from PIL import Image

import matplotlib.pyplot as plt
import matplotlib.patches as ptc
from sklearn.cluster import DBSCAN

import numpy as np

from math import sqrt

from .cluster import Cluster
from .configuration import *
from .clusterizer import read_image, identify_points, clusterize

def preprocess_points(points):
    points = np.array(points)
    X = points[:,0:2] * scale / image_size
    weights = points[:,2]
    mask = (np.random.uniform(size = weights.shape) < prob * weights / step_3)
    return X[mask], weights[mask]

def isolate_cluster(X, weights, y, idx):
    mask = (y == idx)
    return X[mask], weights[mask]

def analyze_cluster(X):
    x, y = X[:,0].mean(), X[:,1].mean()
    x_std, y_std = X[:,0].std(), X[:,1].std()
    size = sqrt(x_std ** 2 + y_std ** 2)
    return x, y, size

def isolate_clusters(X, y, weights, n_clouds):
    clusters = []
    for i in range(n_clouds):
        cluster, w_cluster = isolate_cluster(X, weights, y, i)
        clusters.append(Cluster(cluster, w_cluster))
    return clusters

def draw_circle(x, y, size):
    theta = np.linspace(0, 2 * np.pi, 150)
    
    a = size * np.cos(theta)
    b = size * np.sin(theta)

    plt.plot(y + a, x + b)

def draw_clusters(picture, clusters):
    plt.imshow(picture)
    for cluster in clusters:
        x, y, size = cluster.x * image_size / scale, cluster.y * image_size / scale, cluster.size * image_size / scale
        draw_circle(x, y, size)
    plt.savefig("../output/clusters.png")
    plt.show()    

def isolate_clouds(filepath, option="mixed"):
    picture = read_image(filepath)
    points_list = identify_points(picture)
    X, weights = preprocess_points(points_list)
    y, n_clouds, X, weights = clusterize(X, weights, option=option)
    clusters = isolate_clusters(X, y, weights, n_clouds)
    if do_draw_clusters:
        draw_clusters(picture, clusters)
    return clusters