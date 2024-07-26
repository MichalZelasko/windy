import numpy as np
from math import sqrt
import json

# path = "../resources/pictures"

yellow_camera = np.array((255, 227, 161))
grey_camera = np.array((211, 211, 211))
green_camera = np.array((144, 238, 144))

f = open("../conf/conf.json")
data = json.load(f)

screenshoot = data["screenshoot"]
filepaths = data["filepaths"]
picture_setting = data["picture_setting"]
cluster = data["cluster"]
colormap = data["colormap"]
sampling = data["sampling"]
visualization = data["visualization"]
extrapolation_dict = data["extrapolation"]

do_screenshot = screenshoot["do_screenshot"]
url = screenshoot["url"]
url_map = screenshoot["url_map"]
delay_1 = screenshoot["delay_1"]
delay_2 = screenshoot["delay_2"]
screenshot_number = screenshoot["screenshot_number"]
screenshot_time = screenshoot["screenshot_time"]
do_convert = screenshoot["do_convert"]

path = filepaths["path"]
resource = filepaths["resource"]
map_filepath = filepaths["map"]
animation_path = filepaths["animation"]

grey_difference = picture_setting["grey_difference"]
image_size = picture_setting["image_size"]
x_a = picture_setting["x_a"]
x_b = picture_setting["x_b"]
y_a = picture_setting["y_a"]
y_b = picture_setting["y_b"]

eps_coeff = cluster["eps_coeff"]
mixed_coeff = cluster["mixed_coeff"]
clusterize_depth = cluster["clusterize_depth"]
kmeans_first = cluster["kmeans_first"]
n_clusters = cluster["n_clusters"]
option_clust = cluster["option_clust"]

step_1 = colormap["step_1"]
step_2 = colormap["step_2"]
step_3 = colormap["step_3"]
half_way = colormap["half_way"]

prob = sampling["prob"]
scale = sampling["scale"]

n = 0.99 / prob

do_draw_clusters = visualization["do_draw_clusters"]
do_draw_elbow_graph = visualization["do_draw_elbow_graph"]
do_draw_graph = visualization["do_draw_graph"]
do_draw_cluster_centers = visualization["do_draw_cluster_centers"]
vis_coeff = visualization["vis_coeff"]
t_coeff = visualization["t_coeff"]

option_pos = extrapolation_dict["option_pos"]
option = extrapolation_dict["option"]
k = extrapolation_dict["k"]
func = extrapolation_dict["func"]
move_coeff = extrapolation_dict["move_coeff"]