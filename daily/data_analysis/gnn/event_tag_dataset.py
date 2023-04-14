import torch
import pandas as pd
#from torch_geometric.data import InMemoryDataset
from sklearn.model_selection import train_test_split
#import torch_geometric.transforms as T

# custom dataset
#class EventTagDataset(InMemoryDataset):
class EventTagDataset():
        def __init__(self, transform=None):
            super(EventTagDataset, self).__init__('.', transform, None, None)
            pass

            #data = Data(edge_index=edge_index)

            #data.num_nodes = G.number_of_nodes()

            ## embedding 
            #data.x = torch.from_numpy(embeddings).type(torch.float32)
            #
            ## labels
            #y = torch.from_numpy(labels).type(torch.long)
            #data.y = y.clone().detach()
            #
            #data.num_classes = 2
            ## splitting the data into train, validation and test
            #X_train, X_test, y_train, y_test = train_test_split(pd.Series(G.nodes()), 
            #pd.Series(labels),
            #test_size=0.30, 
            #random_state=42)
            #
            #n_nodes = G.number_of_nodes()
            #
            ## create train and test masks for data
            #train_mask = torch.zeros(n_nodes, dtype=torch.bool)
            #test_mask = torch.zeros(n_nodes, dtype=torch.bool)
            #train_mask[X_train.index] = True
            #test_mask[X_test.index] = True
            #data['train_mask'] = train_mask
            #data['test_mask'] = test_mask
            #self.data, self.slices = self.collate([data])

        def _download(self):
            return

        def _process(self):
            pass
            return

        def __repr__(self):
            pass
            return '{}()'.format(self.__class__.__name__)

dataset = EventTagDataset()
data = dataset[0]
