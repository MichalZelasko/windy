from math import factorial
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.interpolate import interp1d, CubicSpline, make_interp_spline, BarycentricInterpolator
from scipy.optimize import curve_fit
from .function import *

def extrapolate_position(time, position_history, time_points, option = "linear", func = square):
    option = option.lower()     
    if option in ["slinear", "quadratic", "cubic"]:
        print(f"{option} interpolation - position extrapolation.")
        model = interp1d(time, position_history, kind=option, fill_value='extrapolate')
    elif option == "noncubic":
        print(f"Noncubic interpolation - position extrapolation.")
        model = make_interp_spline(time, position_history, k = 2)
    elif option == "cubicspline":
        print(f"Cubicspline interpolation - position extrapolation.")
        model = CubicSpline(time, position_history, bc_type='natural', extrapolate=True)    
    elif option == "polynomial":
        print(f"Polynomial interpolation - position extrapolation.")
        model = BarycentricInterpolator(time, position_history)
    elif option == "aproximation":
        print(f"Aproximation {str(square)} - position extrapolation.")
        popt, _ = curve_fit(func, time, position_history)
        model = lambda x: func(x, *popt)
    else:
        print(f"Linear regression - position extrapolation.")
        model = LinearRegression().fit(time.reshape(-1, 1), position_history)
        return model.predict(time_points.reshape(-1, 1))
    return model(time_points)

def calculate_derivatives(x, y, k): 
    derivatives = np.zeros((k, k))
    for i in range(k):
        derivatives[0][i] = (y[i + 1] - y[i]) / (x[i + 1] - x[i])
    for i in range(1, k):
        for j in range(k - i):
            derivatives[i][j] = (derivatives[i - 1][j + 1] - derivatives[i - 1][j]) / (x[j + 1] - x[j])
    return derivatives

def extrapolate_taylor(time, history, time_points, k = 3):
    derivatives = calculate_derivatives(history, time, k)
    prediction = np.zeros(len(time_points))
    for i, t in enumerate(time_points):
        prediction[i] = prediction[0] + history[0]
        for j in range(k):
            prediction[i] += (derivatives[j][0] * (t - time[0]) ** 2) / (factorial(j))
    return prediction

def extrapolate_size(time, size_array, time_points, option = "linear", func = square):
    option = option.lower() 
    size_array = np.nan_to_num(size_array, nan = 0)         
    if option == "linear":
        print(f"Linear regression - size extrapolation.")
        model = LinearRegression().fit(time.reshape(-1, 1), size_array)
        return model.predict(time_points.reshape(-1, 1))
    elif option == "noncubic":
        print(f"Noncubic interpolation - size extrapolation.")
        model = make_interp_spline(time, size_array, k=2)
    elif option == "cubicspline":
        print(f"Cubicspline interpolation - size extrapolation.")
        model = CubicSpline(time, size_array, bc_type='natural', extrapolate=True)    
    elif option == "polynomial":
        print(f"Polynomial interpolation - size extrapolation.")
        model = BarycentricInterpolator(time, size_array)
    elif option == "aproximation":
        print(f"Aproximation {str(square)} - size extrapolation.")
        popt, _ = curve_fit(func, time, size_array)
        model = lambda x: func(x, *popt)
    else:
        print("Taylor extrapolation - size extrapolation.")
        return extrapolate_taylor(time, size_array, time_points, k=3)
    return model(time_points)