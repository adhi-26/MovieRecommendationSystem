import numpy as np
import os
import pkl
from scipy.sparse import csr_matrix
import pandas as pd

def combine_vectors(parameters: list):
    return np.concatenate(parameters, axis=1)

def combine(path = 'pickles/vectors'):
    params = [np.array(pkl.load_pickle(f'{path}/{item}').todense()) for item in os.listdir(path) if 'vectors.pkl' in item]
    metadata = pd.read_csv('MovieData/movie_database.csv', index_col='imdb-id')
    combined_vector = combine_vectors(params)
    combined_series = pd.Series(combined_vector.tolist(), index=data.index.values)
    return combined_series, metadata

if __name__ == '__main__':

    path = 'pickles/vectors'

    # load pickles variables as a list
    params = [np.array(pkl.load_pickle(f'{path}/{item}').todense()) for item in os.listdir(path) if 'vectors.pkl' in item]
    data = pd.read_csv('MovieData/movie_database.csv', index_col='imdb-id')

    #concatenate using numpy concatenate
    combined_vector = combine_vectors(params)

    #   converting to series
    combined_series = pd.Series(combined_vector.tolist(), index=data.index.values)

    #   convert to sparse matrix before pickling
    combined_vector = csr_matrix(combined_vector)

    #   save final feature vector, feature series
    pkl.save_pickle(folder='pickles', filename= 'features_vector', variable = combined_vector)
    pkl.save_pickle(folder='pickles', filename= 'features_series', variable = combined_series)
