import numpy as np

class Cluster:

    def __init__(self, points, weights):
        self.points = points
        self.weights = weights
        self.size_array = []
        self.get_power()
        self.get_center()
        self.get_size()
        self.get_size_array()
        
    def get_power(self):
        self.power = np.sum(self.weights)

    def get_center(self):
        self.x = np.sum(self.points[:,0] * self.weights) / self.power
        self.y = np.sum(self.points[:,1] * self.weights) / self.power

    def get_size(self):
        self.size = np.sqrt(np.mean((self.points[:,0] - self.x) ** 2 + (self.points[:,1] - self.y) ** 2))

    def get_angles(self):
        self.angles = np.arctan((self.points[:,1] - self.y) / (self.points[:,0] - self.x))
        correction = np.zeros(self.angles.shape)
        correction[self.points[:,1] < self.y] = np.pi
        self.angles += correction

    def get_direction_points(self, idx, number):
        mask = (self.angles > np.pi * idx / number)
        points_in_angle = self.points[mask]
        size_angle = np.sqrt(np.mean((points_in_angle[:,0] - self.x) ** 2 + (points_in_angle[:,1] - self.y) ** 2))
        return size_angle

    def get_size_array(self, number = 8):
        self.get_angles()
        for idx in range(number):
            self.size_array.append(self.get_direction_points(idx, number))