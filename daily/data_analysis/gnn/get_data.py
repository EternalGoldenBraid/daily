import pandas as pd
import numpy as np
from collections import Counter
import pickle
import os

def get_user_id_():
    # Allow demoers to view plots generated from my data.
    if current_user.is_anonymous or current_user.id == 2:
        # TODO: Change this to query by my username.
        user_id = 1
    else:
        user_id = current_user.id
        #user_id_= current_user.get_id()

    return user_id

def get_event_tag_data(engine, timespan=0, freq_threshold=2):
    # Allows demoers to view plots generated from my data.
    user_id_ = 1

    # Merge ratings, events and tags to get a df of dates with combinations of tags.
    
    # Read ratings for user
    #ratings = pd.read_sql('rating',engine,index_col='id')

    if timespan != 0:
        #query = f'SELECT * FROM rating WHERE user_id={user_id_} and date > CURRENT_DATE()-{timespan}'
        query = f'SELECT * FROM rating WHERE user_id={user_id_} ORDER BY date desc LIMIT {timespan}'

    else: 
        query = f'SELECT * FROM rating WHERE user_id={user_id_}'
    ratings = pd.read_sql(query, engine,index_col='id')
    ratings['rating_id'] = ratings.index

    # Read all tags.
    # TODO: Inefficient, fetch only for user, or set lazy=true?.
    # TODO: Add manual sql query.
    tags = pd.read_sql('tag',engine,index_col='id')
    #tags.columns = tags.columns.str.replace('id','tag_id')

    # Read all rating event associations.
    # TODO: Add manual sql query.
    # TODO: Inefficient, fetch only for user, or lazy=dynamic.
    #query = f'SELECT * FROM rating_events WHERE rating_id={ratings.index}'
    #re_m2m = pd.read_sql(query,engine,index_col=False)
    re_m2m = pd.read_sql('rating_events',engine,index_col=False)
    re_m2m = re_m2m[re_m2m['rating_id'].isin(ratings.index)]

    # Read all event tag associations.
    # Not all events have tags, thus merge innner vs. left
    # dictates whether null tags are included.
    # TODO: Inefficient, fetch only for user, or lazy=dynamic.
    et_m2m = pd.read_sql('event_tags',engine, index_col=False)
    et_m2m = re_m2m \
            .merge(et_m2m,how='inner',on='event_id')[['event_id', 'tag_id']]

    # Clean data. Remove rows there tag_id doesn't occur >= n times
    et_m2m = et_m2m[et_m2m.groupby('tag_id')['tag_id'] \
            .transform('count').ge(freq_threshold)]

    data = re_m2m \
            .merge(et_m2m,how='inner',on='event_id')[['event_id', 'tag_id','rating_id']]

    # Reduce redundant rating_id entries
    data = (data.groupby('event_id').agg(list))
    data['rating_id'] = data['rating_id'].apply(lambda x: x[0])
    data = data.merge(ratings,how='inner',on='rating_id')

    tag_list = et_m2m.groupby('event_id').agg(list)
    all_tags = np.concatenate([np.array(i) for i in tag_list['tag_id'].values])
    tag_id_columns = np.unique(all_tags)
    tag_names = tags.loc[tag_id_columns]['tag_name']

    features = ['meditation', 'rating_sleep', 'rating_day', 'cw', 'screen']
    event_features = data[features]
    event_features['event_id'] = event_features.index.values
    edges = []

    # Connect nodes u and v if edge exists.
    idx = 0
    f = np.zeros((len(all_tags),event_features.shape[1]+1)).astype(int)

    # First create NxF matrix, N number of nodes F+1 number of features.
    for event_idx, event in enumerate(data['tag_id']):
        for u in event:
            f[idx,0] = u
            f[idx,1:] = event_features.iloc[event_idx].values
            idx += 1

    # Associate each node of an edge with its corresponding index wrt. 
    # feature matrix 
    for event_idx, event in enumerate(data['tag_id']):
        event_id = event_features['event_id'].iloc[event_idx]
        for u in event:
            locations = np.array(*np.where(u==f[:,0]))
            is_same_event = np.array(f[np.where(u==f[:,0])][:,-1] == event_id)
            u_idx = locations[is_same_event].squeeze()
            for v in event:
                if u == v: continue
                locations = np.array(*np.where(v==f[:,0]))
                is_same_event = np.array(f[np.where(v==f[:,0])][:,-1] == event_id)
                v_idx = locations[is_same_event].squeeze()
                edges.append(np.array([u_idx, v_idx]))
    print(f"Edges within events {len(edges)}.")
    


    # Add edges connecting event graphs across days and events.
    print(f)
    nodes = f[:,0]
    cross_edges = []
    print(nodes)
    processed = []
    for u_idx, node in enumerate(nodes):
        v_idxs = np.array(*np.where(node==nodes))
        for v_idx in v_idxs:
            # Skip self loop and same event nodes.
            if v_idx == u_idx or f[u_idx,-1] == f[v_idx,-1]: continue
            cross_edges.append(np.array([u_idx,v_idx]))

    print(f"Edges cross events {len(cross_edges)}.")

    # Drop the event_id 
    f = (np.delete(f,-1,1))
    edges = np.array(edges)
    cross_edges = np.array(cross_edges)

    print(f"Saving data, features dim {f.shape}, edges dim {len(edges)}.")
    features = pd.DataFrame(f, columns = np.concatenate((['tag_id'], features)))

    PIK = "event_tag_graph.dat"
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(THIS_FOLDER, PIK)
    with open(path, "wb") as f:
        pickle.dump([features, edges, cross_edges], f)

    print("Data packed")
    return data, tag_names
