import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.interpolate import CubicSpline, make_interp_spline, BarycentricInterpolator
from scipy.optimize import curve_fit
from .function import *

from .extrapolate import *

class Cloud:

    def __init__(self, cluster, time):
        self.x = cluster.x
        self.y = cluster.y
        self.size_array = np.array(cluster.size_array)
        self.power = cluster.power
        self.weights = cluster.weights
        self.points = cluster.points
        self.time = time
        self.next = []
        self.previous = []
        self.history_time = None
        self.history_x = None
        self.history_y = None
        self.history_size = None
        self.history_power = None
        self.time_points = None
        self.x_future = None
        self.y_future = None
        self.power_future = None
        self.sizes_future = None

    def add_next(self, next_cloud, recursion = False):
        self.next.append(next_cloud)
        if not recursion:
            next_cloud.add_previous(self, recursion = True)

    def add_previous(self, previous_cloud, recursion = False):
        self.previous.append(previous_cloud)
        if not recursion:
            previous_cloud.add_next(self, recursion = True)

    def has_next(self):
        return len(self.next) > 0

    def actualize_history(self):
        n = len(self.previous)
        if n < 1:
            self.history_x = np.array([])
            self.history_y = np.array([])
            self.history_size = self.size_array.reshape(1, -1)
            self.history_power = np.array([])
            self.history_time = np.array([])
        else:
            for prev in self.previous:
                prev.actualize_history()
            self.history_x = np.zeros(self.previous[0].history_x.shape)
            self.history_y = np.zeros(self.previous[0].history_y.shape)
            self.history_size = np.zeros(self.previous[0].history_size.shape)
            self.history_power = np.zeros(self.previous[0].history_power.shape)
            self.history_time = self.previous[0].history_time
            w_sum, one_distance_sum = 0, 0
            for prev in self.previous:
                one_distance = 1 / np.sqrt((self.x - prev.x) ** 2 + (self.y - prev.y) ** 2)
                w_sum += (prev.power / len(prev.next)) * one_distance
                one_distance_sum += one_distance
                self.history_x += prev.history_x * (prev.power / len(prev.next)) * one_distance
                self.history_y += prev.history_y * (prev.power / len(prev.next)) * one_distance
                self.history_size += prev.history_size * (prev.power / len(prev.next)) * one_distance
                self.history_power += prev.history_power / len(prev.next)
            self.history_x /= w_sum
            self.history_y /= w_sum
            self.history_size /= w_sum
            self.history_size = np.append(self.history_size, self.size_array.reshape((1, -1)), axis = 0)
        self.history_x = np.append(self.history_x, [self.x])
        self.history_y = np.append(self.history_y, [self.y])
        self.history_power = np.append(self.history_power, [self.power])
        self.history_time = np.append(self.history_time, [self.time])

    def extrapolate_x(self, time_points, option = "linear", func = square):
        return extrapolate_position(-self.history_time, self.history_x, time_points, option, func)

    def extrapolate_y(self, time_points, option = "linear", func = square):
        return extrapolate_position(-self.history_time, self.history_y, time_points, option, func)

    def extrapolate_power(self, time_points, option = "linear", k = 3, func = square):
        time_history, power_history = -self.history_time, self.history_power
        option = option.lower()          
        if option == "linear":
            print(f"Linear regression - power extrapolation.")
            model = LinearRegression().fit(time_history.reshape(-1, 1), power_history)
            return model.predict(time_points.reshape(-1, 1))
        elif option == "noncubic":
            print(f"Noncubic interpolation - power extrapolation.")
            model = make_interp_spline(time_history, power_history, k=2)
        elif option == "cubicspline":
            print(f"Cubicspline interpolation - power extrapolation.")
            model = CubicSpline(time_history, power_history, bc_type='natural', extrapolate=True)    
        elif option == "polynomial":
            print(f"Polynomial interpolation - power extrapolation.")
            model = BarycentricInterpolator(time_history, power_history)
        elif option == "aproximation":
            print(f"Aproximation {str(square)} - power extrapolation.")
            popt, _ = curve_fit(func, time_history, power_history)
            model = lambda x: func(x, *popt)
        else:
            print("Taylor extrapolation - power extrapolation.")
            return extrapolate_taylor(time_history, power_history, time_points, k=k)
        return model(time_points)

    def extrapolate_size_array(self, time_points, option = "linear", func = square):
        time_history, size_history = -self.history_time, self.history_size
        predicted_sizes = np.zeros((len(time_points), size_history.shape[1]))
        for i in range(size_history.shape[1]):
            size_array = size_history[:,i]
            size_predicted = extrapolate_size(time_history, size_array, time_points, option, func)
            predicted_sizes[:,i] = size_predicted
        return predicted_sizes

    def extrapolate(self, time_points, option_pos = "linear", option = "linear", k = 3, func = division):
        if self.history_x is None or self.history_y is None or \
        self.history_size is None or self.history_power is None:
            self.actualize_history()
        time_points = np.array(time_points)
        self.time_points = time_points
        self.x_future = self.extrapolate_x(time_points, option_pos, func)
        self.y_future = self.extrapolate_y(time_points, option_pos, func)
        self.power_future = self.extrapolate_power(time_points, option, k, func)
        self.sizes_future = self.extrapolate_size_array(time_points, option, func)

    def extrapolate_size_change(self, alpha, time, idx, t_coeff = 0.0):
        n = self.size_array.shape[0]
        angle = 2 * np.pi / n
        part = round(alpha / angle)
        w = alpha / angle - part + 0.5
        size_1, size_2 = self.size_array[part - 1], self.size_array[part]        
        size = size_1 * w + size_2 * (1 - w)
        
        size_future_1, size_future_2 = self.sizes_future[idx][part - 1], self.sizes_future[idx][part]
        size_future = size_future_1 * w + size_future_2 * (1 - w)
        c = (100.0 - t_coeff * time) / 100.0
        return np.sqrt(np.sqrt(max(0.0, c * self.power_future[idx] / self.power))) * size_future / size

    def compute_point_set(self, time, idx, dx, dy, dt, c = 0.5, t_coeff = 0.0):
        new_points = np.zeros((self.points.shape[0], 2))
        dx, dy = dx * (time - self.time) / dt, dy * (time - self.time) / dt
        for i, point in enumerate(self.points):
            v_x, v_y = point[0] - self.x, point[1] - self.y
            alpha = np.arctan(v_y / v_x)
            if v_y > 0: alpha += np.pi
            size_coeff = self.extrapolate_size_change(alpha, time, idx, t_coeff=t_coeff)
            new_points[i][0] = self.x + c * (self.x_future[idx] - self.x) + (1 - c) * dx + v_x * size_coeff
            new_points[i][1] = self.y + c * (self.y_future[idx] - self.y) + (1 - c) * dy + v_y * size_coeff
        return new_points
    
    def compute_weights(self, time, idx, t_coeff = 0.0):
        future_size = np.mean(self.sizes_future[idx])
        actual_size = np.mean(self.size_array)
        c = (100.0 - t_coeff * time) / 100.0
        p = self.power_future[idx]
        if p < 1.0: p = np.exp(p - 1)
        weights = self.weights * np.sqrt(max(0.0, c * p / self.power))
        weights = np.where(weights > 60.0, 60.0, weights)
        weights = np.where(weights < 0.0, 0.0, weights)
        weights = weights * ((actual_size ** 2) / (future_size ** 2))        
        return weights
            
