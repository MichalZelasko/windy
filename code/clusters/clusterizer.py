from PIL import Image

import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN, KMeans

import numpy as np

from .configuration import *

def read_image(filepath):
    image = Image.open(filepath)
    try:
        picture = np.array(image.getdata()).reshape(image.size[1], image.size[0], 4)
    except:
        picture = np.array(image.getdata()).reshape(image.size[1], image.size[0], 3)
    return picture[:,:,:3]

def check_if_backgroud(pixel):
    return np.abs(pixel[0] - pixel[1]) < grey_difference and \
           np.abs(pixel[0] - pixel[2]) < grey_difference and \
           np.abs(pixel[1] - pixel[2]) < grey_difference

def verify_pixel(pixel):
    return np.array_equal(pixel, yellow_camera) or \
           np.array_equal(pixel, grey_camera)   or \
           np.array_equal(pixel, green_camera)  or \
           check_if_backgroud(pixel)

def verify_if_not_line(picture, i, j):
    return picture[i - 1][j - 1] + picture[i - 1][j] + picture[i - 1][j + 1] + \
           picture[i][j - 1]     + picture[i][j]     + picture[i][j + 1]     + \
           picture[i + 1][j - 1] + picture[i + 1][j] + picture[i + 1][j + 1] < 3

def remove_lines(picture):
    mask = np.zeros((picture.shape[0], picture.shape[1]))
    for i in range(1, picture.shape[0] - 1):
        for j in range(1, picture.shape[1] - 1):
            if picture[i][j] == 0 and verify_if_not_line(picture, i, j):
                mask[i][j] = 1
    return mask

def interpret_pixel(pixel):
    idx = pixel.argmax()
    retval = 0
    if idx == 2:
        retval = step_1 - half_way * pixel[0] / pixel[2]
    elif idx == 1:
        retval = step_1 + (step_2 - step_1) * pixel[0] / (pixel[0] + pixel[2])
    else:
        retval = step_2 + half_way * pixel[2] / pixel[0]
    return retval    

def interpret_points(mask, picture):
    points_list = []
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            if mask[i][j]:
                value = interpret_pixel(picture[i][j])
                if value >= 0:
                    points_list.append((i, j, value))
    return points_list                

def identify_points(picture):
    mask = np.apply_along_axis(verify_pixel, 2, picture)
    mask = remove_lines(mask * 1)
    points_list = interpret_points(mask, picture)
    return points_list

def check_color(color):
    title = str(interpret_pixel(color))
    arr = np.zeros((32, 32, 3))
    arr[:,:,0] = color[0] / 255
    arr[:,:,1] = color[1] / 255
    arr[:,:,2] = color[2] / 255
    plt.imshow(arr)
    plt.title(title)
    plt.show()

def check_colors():
    colors = np.array([(126, 122, 145),
                    (117, 111, 147),
                    (103, 94, 150),
                    (99, 90, 144),
                    (103, 95, 149),
                    (18, 139, 141),
                    (88, 203, 89),
                    (198, 67, 77),
                    (161, 17, 107)])
    x = []
    y_red = []
    y_green = []
    y_blue = []
    for i, color in enumerate(colors):
        m = color.mean()
        x.append(i)
        y_red.append(color[0] / m)
        y_green.append(color[1] / m)
        y_blue.append(color[2] / m)
        check_color(color)
    plt.plot(x, y_red, color = "red")
    plt.plot(x, y_green, color = "green")
    plt.plot(x, y_blue, color = "blue")
    plt.show()

def clusterize_dbscan(X):
    cls = DBSCAN(eps_coeff * n * scale / image_size).fit(X)
    return cls.labels_

def elbow_method(X, start = 1, stop = 50, step = 4):
    scores, xs = [], []
    for n_clusters in range(start, stop, step):
        cls = KMeans(n_clusters).fit(X)
        scores.append(cls.score(X))
        xs.append(n_clusters)
    if do_draw_elbow_graph:
        plt.plot(xs, scores)
        plt.show()
    for i in range(1, len(scores) - 1):
        if 2 / (1 / scores[i - 1] + 1 / scores[i + 1]) < scores[i]:
            return start + step * i
    return stop

def clusterize_kmeans(X, start = 1, stop = 50, step = 4):
    n_clusters = elbow_method(X, start, stop, step)
    cls = KMeans(n_clusters).fit(X)
    return cls.labels_

def compute_center(X, y, weights):
    m = y.max()
    centers = []
    for i in range(m):
        mask = (y == i)
        w = weights[mask]
        w_sum = np.sum(w)
        cluster = X[mask]
        centers.append([np.sum(cluster[:,0] * w) / w_sum, np.sum(cluster[:,1] * w) / w_sum, w_sum])
    centers = sorted(centers, key=lambda x: x[2], reverse=True)
    return np.array(centers)[:,:2]

def clusterize_mixed(X, weights):
    cls = DBSCAN(eps_coeff * n * scale / image_size).fit(X)
    y = cls.labels_
    centers = compute_center(X, y, weights)
    n_clusters = int(min(y.max(), (y.max() + 1) / mixed_coeff))
    cls = KMeans(n_clusters, init = centers[:n_clusters], max_iter = 1000).fit(X)
    return cls.labels_

def clusterize_hierarchical(X, weights, depth = 3, kmeans_first = False, n_clusters = 2, offset = 0, print_offset = ""):
    if depth == 0:
        return np.zeros(X.shape[0]) + offset, X, weights
    if kmeans_first:
        cls = KMeans(int(n_clusters), max_iter = 300).fit(X)
        y = cls.labels_
    else:
        cls = DBSCAN((2 * depth) * eps_coeff * n * scale / image_size).fit(X)
        y = cls.labels_
        if y.max() < 0: 
            y = np.zeros(y.shape).astype(int)
    y_new, X_new, w_new = clusterize_hierarchical(X[y == 0], weights[y == 0], depth=depth - 1, kmeans_first=(not kmeans_first), n_clusters=n_clusters, offset = offset, print_offset=print_offset+"  ")
    for i in range(1, y.max() + 1):
        y_part, X_part, w_part = clusterize_hierarchical(X[y == i], weights[y == i], depth=depth - 1, kmeans_first=(not kmeans_first), n_clusters=n_clusters, offset = y_new.max() + 1, print_offset=print_offset+"  ")
        y_new = np.concatenate((y_new, y_part))
        X_new = np.concatenate((X_new, X_part))
        w_new = np.concatenate((w_new, w_part))
    return y_new, X_new, w_new

def clusterize(X, weights, option = "Hierarchical"):
    if option.lower() == "DBSCAN".lower():
        y = clusterize_dbscan(X)
    elif option.lower() == "KMEANS".lower():
        y = clusterize_kmeans(X, start=elbow_start, stop=elbow_stop, step=elbow_step)
    elif option.lower() == "Hierarchical".lower():
        y, X, weights = clusterize_hierarchical(X, weights, depth=clusterize_depth, kmeans_first=kmeans_first, n_clusters=n_clusters)
    else:
        y = clusterize_mixed(X, weights)
    y = y.astype(int)
    return y, y.max() + 1, X, weights
