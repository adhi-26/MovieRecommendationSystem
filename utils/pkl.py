import pickle

def save_pickle(folder: str, filename: str, variable):
    with open(f'{folder}/{filename}.pkl', 'wb') as f:
        pickle.dump(variable, f)

def load_pickle(path: str):
    with open(path, 'rb') as f:
        variable = pickle.load(f)
    return variable