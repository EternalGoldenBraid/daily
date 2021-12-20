import json
import os

def save_results(path, results, key='null'):

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
            json.dump(result, file)



