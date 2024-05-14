import numpy as np
import numpy.polynomial.polynomial as poly

def ransac(x_arr, y_arr, threshold=1e-4, deg=1):
    if len(x_arr) == 0:
        return None 
    
    num_iter = 50
    max_inliers = []

    for _ in range(num_iter):
        chosen_indexes = np.random.choice(len(x_arr), size=deg + 1)
        coefs = poly.polyfit([x_arr[idx] for idx in chosen_indexes], [y_arr[idx] for idx in chosen_indexes], deg)

        curr_inliers = []
        for idx in range(len(x_arr)):
            if np.square(y_arr[idx] - poly.polyval(x_arr[idx], coefs)) <= threshold:
                curr_inliers.append(idx)

        if len(curr_inliers) > len(max_inliers):
            max_inliers = curr_inliers

    x_vals = np.array([x_arr[idx] for idx in max_inliers])
    y_vals = np.array([y_arr[idx] for idx in max_inliers])
    return poly.polyfit(x_vals, y_vals, deg)

def estimate(x_arr, y_arr):
    return ransac(x_arr, y_arr)
