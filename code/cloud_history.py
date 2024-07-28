import matplotlib.pyplot as plt

from clusters.configuration import *
from utils.converter import *
from utils.computation import *
from clusters.cluster_analyzer import isolate_clouds
from cloud.cloud import Cloud
from cloud.history_builder import find_predecessors, complete_successors
from animation.animation import *
from cloud.function import *

class CloudHistory:

    def __init__(self, clouds_history):
        self.history = clouds_history
        self.times = []
        self.time_points = None
        self.get_times()
        self.dx = 0
        self.dy = 0
        self.dt = 0

    def get_times(self):
        for clouds in self.history:
            self.times.append(clouds[0].time)

    def plot_graph(self):
        for clouds in self.history:
            for cloud in clouds:
                y = hash_position(cloud.x, cloud.y)
                plt.scatter([-cloud.time], [y], c = [cloud.power])
                for cld in cloud.next:
                    plt.plot([-cloud.time, -cld.time], [y, hash_position(cld.x, cld.y)])
        plt.show()

    def actualize_history(self):
        for cloud in self.history[-1]:
            cloud.actualize_history()

    def compute_x_y(self, idx):
        x, y, p = 0, 0, 0
        for cloud in self.history[idx]:
            x += cloud.x * cloud.power
            y += cloud.y * cloud.power
            p += cloud.power
        return x / p, y / p

    def compute_dx_dy_dt(self):
        x_0, y_0 = self.compute_x_y(0)
        x_1, y_1 = self.compute_x_y(-1)
        self.dx = x_1 - x_0
        self.dy = y_1 - y_0   
        self.dt = self.history[-1][0].time - self.history[0][0].time     

    def extrapolate(self, time_points, option_pos = "linear", option = "linear", k = 3, func = division):
        self.time_points = time_points        
        for cloud in self.history[-1]:
            cloud.extrapolate(time_points, option_pos=option_pos, option=option, k=k, func=func)
        self.compute_dx_dy_dt()

    def draw_map(self, x_a = 80, x_b = -100, y_a = 0, y_b = 1500):
        image = Image.open(map_filepath)
        try:
            picture = np.array(image.getdata()).reshape(image.size[1], image.size[0], 4)
        except:
            picture = np.array(image.getdata()).reshape(image.size[1], image.size[0], 3)            
        x_a, x_b, y_a, y_b = convert_size(image.size[1], image.size[0], x_a, x_b, y_a, y_b)
        picture = picture[x_a:x_b,y_a:y_b]
        plt.imshow(picture)
        self.x_size = picture.shape[0]
        self.y_size = picture.shape[1]

    def validate_points(self, new_points, weights):
        mask = (new_points[:,0] * image_size / scale > 0)
        new_points, weights = new_points[mask], weights[mask]
        mask = (new_points[:,0] * image_size / scale < self.x_size)
        new_points, weights = new_points[mask], weights[mask]
        mask = (new_points[:,1] * image_size / scale > 0)
        new_points, weights = new_points[mask], weights[mask]
        mask = (new_points[:,1] * image_size / scale < self.y_size)
        new_points, weights = new_points[mask], weights[mask]
        return new_points, weights
    
    def generate_mesh_grid(self):
        points = np.zeros((int(self.x_size / vis_coeff) * int(self.y_size / vis_coeff), 2))
        for i in range(int(self.x_size / vis_coeff)):
            for j in range(int(self.y_size / vis_coeff)):
                points[i * int(self.y_size / vis_coeff) + j][0] = i * vis_coeff
                points[i * int(self.y_size / vis_coeff) + j][1] = j * vis_coeff
        return points        

    def classify_point(self, point, i = 0):
        x = int(point[0] / vis_coeff)
        y = int(point[1] / vis_coeff)
        if i == 1: x += 1
        if i == 2: x -= 1
        if i == 3: y += 1
        if i == 4: y -= 1
        return x * int(self.y_size / vis_coeff) + y
    
    def filter_points(self, points, weights):
        mask = (weights > 0)
        return points[mask], weights[mask]
    
    def set_point_weights(self, points_set, weights_set, weights):
        points_set, weights_set = self.validate_points(points_set, weights_set)
        for j, point in enumerate(points_set):
            idx_0 = self.classify_point(point, i=0)
            idx_1 = self.classify_point(point, i=1)
            idx_2 = self.classify_point(point, i=2)
            idx_3 = self.classify_point(point, i=3)
            idx_4 = self.classify_point(point, i=4)
            weights[idx_0] += 0.5 * min(60.0, max(0.0, weights_set[j]))
            weights[idx_1] += 0.125 * min(60.0, max(0.0, weights_set[j]))
            weights[idx_2] += 0.125 * min(60.0, max(0.0, weights_set[j]))
            weights[idx_3] += 0.125 * min(60.0, max(0.0, weights_set[j]))
            weights[idx_4] += 0.125 * min(60.0, max(0.0, weights_set[j]))
        return weights
    
    def draw_circle(self, cloud, t, i):
        theta = np.linspace(0, 2 * np.pi, 150)
        dx = self.dx * (t - self.cloud[-1][0].time) / self.dt
        dy = self.dy * (t - self.cloud[-1][0].time) / self.dt
        x = cloud.x + move_coeff * (cloud.x_future[i] - self.x) + (1 - move_coeff) * dx
        y = cloud.x + move_coeff * (cloud.x_future[i] - self.x) + (1 - move_coeff) * dy
        s = image_size / scale
        a = np.mean(cloud.sizes_future[i]) * np.cos(theta)
        b = np.mean(cloud.sizes_future[i]) * np.sin(theta)
        plt.plot(s * (y + a), s * (x + b))
    
    def visualize_points(self, t, i):
        points, weights = self.generate_mesh_grid(), np.zeros(int(self.x_size / vis_coeff) * int(self.y_size / vis_coeff))
        for cloud in self.history[-1]:
            points_set = cloud.compute_point_set(t, i, self.dx, self.dy, self.dt, c=move_coeff, t_coeff=t_coeff)
            weights_set = cloud.compute_weights(t, i, t_coeff)
            weights = self.set_point_weights(points_set, weights_set, weights)
            if do_draw_cluster_centers:
                self.draw_circle(cloud, t, i)
        points, weights = self.filter_points(points, weights)
        points, weights = self.validate_points(points, weights)
        plt.scatter(points[:,1] * image_size / scale, points[:,0] * image_size / scale, s=np.ones(points.shape[0]), c=weights, cmap="jet")

    def visualize_extrapolation(self, time_points, option_pos = "aproximation", option = "aproximation", k = 3, func = division, x_a = 80, x_b = -100, y_a = 0, y_b = 1500):
        self.extrapolate(time_points, option_pos=option_pos, option=option, k=k, func=func)
        clean_directory("../output/extrapolation")
        for i, t in enumerate(self.time_points):
            plt.title(f"Extrapolation result t={t} minutes")
            self.draw_map(x_a = x_a, x_b = x_b, y_a = y_a, y_b = y_b)
            self.visualize_points(t, i)
            plt.clim(0.0, 60.0)
            plt.colorbar()
            plt.savefig(f"../output/extrapolation/extr-{time_to_titles(t)}.png", dpi = 200)
            plt.clf()
        plt.close()

    def plot_x_extrapolation(self):
        plt.title("X-coord extrapolation plot")
        for cloud in self.history[-1]:
            ts = list(-cloud.history_time)
            ts.extend(self.time_points)
            xs = list(cloud.history_x)
            xs.extend(list(cloud.x_future))
            plt.plot(ts, xs)
        plt.show()

    def plot_y_extrapolation(self):
        plt.title("Y-coord extrapolation plot")
        for cloud in self.history[-1]:
            ts = list(-cloud.history_time)
            ts.extend(self.time_points)
            ys = list(cloud.history_y)
            ys.extend(list(cloud.y_future))
            plt.plot(ts, ys)
        plt.show()

    def plot_power_extrapolation(self):
        plt.title("Power extrapolation plot")
        for cloud in self.history[-1]:
            ts = list(-cloud.history_time)
            ts.extend(self.time_points)
            powers = list(cloud.history_power)
            powers.extend(list(cloud.power_future))
            plt.plot(ts, powers)
        plt.show()

    def plot_size_extrapolation(self):
        plt.title("Size extrapolation plot")
        for cloud in self.history[-1]:
            ts = list(-cloud.history_time)
            ts.extend(self.time_points)
            sizes = list(np.mean(cloud.history_size, axis=1))
            sizes.extend(list(np.mean(cloud.sizes_future, axis=1)))
            plt.plot(ts, sizes)
        plt.show()

    def plot_extrapolation(self, time_points, option_pos = "linear", option = "linear", k = 3, func=division):
        self.extrapolate(time_points, option_pos=option_pos, option=option, k=k, func=func)
        self.plot_x_extrapolation()
        self.plot_y_extrapolation()
        self.plot_power_extrapolation()
        self.plot_size_extrapolation()

    def animate(self, time_points = np.linspace(0, 72, 37), option_pos = "linear", option = "linear", k = 3, func=division, x_a = 80, x_b = -100, y_a = 0, y_b = 1500):
        print("Creating extrapolation ...")
        self.visualize_extrapolation(time_points=time_points, option_pos=option_pos, option=option, k=k, func=func, x_a = x_a, x_b = x_b, y_a = y_a, y_b = y_b)
        print("Creating animation ...")
        animation = Animation("../output/extrapolation")
        animation.animate(animation_path)

def find_precessors_successors(clouds, idx):
    if idx > 0 and idx < len(clouds):
        find_predecessors(clouds[idx], clouds[idx - 1])
        complete_successors(clouds[idx - 1], clouds[idx])

def process_file(filepaths, option="mixed"):
    clouds_history = []
    for i, file in enumerate(filepaths):
        clusters = isolate_clouds(file, option=option)
        clouds = []
        time = extract_time(file)
        for cluster in clusters:
            clouds.append(Cloud(cluster, time))
        clouds_history.append(clouds)
        find_precessors_successors(clouds_history, i)
    return clouds_history

def isolate_cloud_history(option_clust = "mixed", option_pos = "linear", option = "linear", k = 3, func="division", x_a = 80, x_b = -100, y_a = 0, y_b = 1500):
    func = string_to_method(func)
    filepaths = list_files(path)
    clouds_history = process_file(filepaths, option=option_clust)
    cloud_history = CloudHistory(clouds_history)
    if do_draw_graph: 
        cloud_history.plot_graph()
    cloud_history.actualize_history()
    if do_plot_extrapolation:
        cloud_history.plot_extrapolation(np.linspace(0, extr_stop, extr_stop // extr_step), option_pos=option_pos, option=option, k=k, func=func)
    cloud_history.animate(option_pos=option_pos, option=option, k=k, func=func, x_a = x_a, x_b = x_b, y_a = y_a, y_b = y_b)
