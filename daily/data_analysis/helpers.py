import json
import os, io
import pandas as pd
import numpy as np
from flask import Response

from matplotlib.backends.backend_agg import FigureCanvasAgg as FC

def save_results(path, results, key='null'):
    """ Save data to json """

    if not (path and results and key): 
        raise ValueError('Insuficcient parameters for save_results')
        return

    if os.path.exists(path):
        with open(path, 'r+') as file_in:
            data = json.load(file_in)
        data[key] = results
        with open(path, 'w') as file_out:
            json.dump(data, file_out)
    else:
        with open(path, 'w') as file:
            result = { key : results }
            print(result)
            json.dump(result, file)

def L2(x, y):

    dist = np.sqrt(np.sum(np.dot(x-y, x-y)))

    return dist

def update_nearests(data, centers):
    n_vectors = data.shape[0]
    vec_dim = data.shape[1]-1

    for tag_idx, tag_vector in enumerate(data[:,:vec_dim]):

        comp = lambda center: L2(tag_vector, center)
        #nearests[tag_idx] = np.argmin(list(map(comp,centers)))
        tag_vector[-1] = np.argmin(list(map(comp,centers)))

def kmeans(data, k=3):

    max_ = data.max()
    min_ = data.min()
    vec_dim = data.shape[1]
    n_vectors = data.shape[0]

    centers = np.random.randint(min_,max_,(k, vec_dim))
    #print("Random centers: ", centers)
    #print("Data: ")
    print(data)

    nearest = np.zeros((n_vectors,1))
    data = np.hstack((data, nearest))
    for tag_idx, tag_vector in enumerate(data[:,:vec_dim]):

        comp = lambda center: L2(tag_vector, center)
        nearest[tag_idx] = np.argmin(list(map(comp,centers)))

    data[:,-1] = nearest.flatten()

    #print("nearest")
    #print(nearest)
    mean = lambda vectors: np.mean(vectors)

    eps = 0
    while eps < 5000:
        eps += 1

        for k_th in range(k):
            truth_table = (data[:,-1] == k_th)

            if truth_table.sum() == 0: continue
            centers[k_th] = np.mean(data[truth_table.T,:-1],axis=0)

        update_nearests(data, centers)

        #for tag_vector in data:
        #    dist = tag_vector[:-1]-centers[int(tag_vector[-1])]
        #    print("Pre: ", loss)
        #    loss += np.dot(dist,dist)
        #    print("Post:, ", loss)

    print("centers")
    print(centers)

def plot_img(fig):
    # BytesIO write stream to RAM.
    output = io.BytesIO()
    FC(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')
