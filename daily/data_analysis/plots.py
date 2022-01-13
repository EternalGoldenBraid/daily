from daily.models import User, Rating, Tag, rating_as, event_as
from flask import Response, redirect, url_for, flash
from flask_login import current_user
from daily.data_analysis.data_models import get_tag_sleep_day_data


#import matplotlib
#matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FC
import networkx as nx

import math
import numpy as np
import pandas as pd
from numpy.random import default_rng
#from scipy import stats

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
import joblib
import json
from collections import Counter
from itertools import combinations
import os
import io


import datetime

from daily.data_analysis.helpers import save_results



def save_plot(fig, name, form=None):
    path = "plots/"
    filename = path+name+"."+form
    plt.savefig("daily/static/"+filename, format=form)
    #plt.savefig(filename)
    return filename
        
def plot_img(fig):
    # BytesIO write stream to RAM.
    output = io.BytesIO()
    FC(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_subplots(ax, labels:np.array):
    """ Add rotated labels up and down """
    ax.set_xticks(range(labels.shape[0]))
    ax.set_xticklabels(labels, rotation=45,fontsize=10)
    ax.tick_params(axis='x', bottom=True, top=True,
            labelbottom=True, labeltop=True)
    
    # Set everyother tick top and bot
    ticks_bot = [tick.label1 for tick in ax.xaxis.get_major_ticks()]
    for idx, tick in enumerate(ticks_bot):
        if idx % 2 == 0: tick.set_visible(False)
    plt.setp(ticks_bot,ha='right')

    ticks_top = [tick.label2 for tick in ax.xaxis.get_major_ticks()]
    for idx, tick in enumerate(ticks_top):
        if idx % 2 == 1: tick.set_visible(False)
    plt.setp(ticks_top, ha='left' )

    ax.grid(True)
    plt.tight_layout()

def tag_freq(engine):
    """ Return a runnig average of tag frequencies for
        the past week, month and all time.

    TODO: Add user_id checks
        - requires user_id columns in events and tags.
    """

    ### Data analysis
    tags = pd.read_sql('tag',engine, index_col=False)
    tags.columns = tags.columns.str.replace('id','tag_id')

    events = pd.read_sql('event',engine, index_col=False)
    events.columns = events.columns.str.replace('id','event_id')

    # Add tags associated with events to events.
    event_tag = pd.read_sql('event_tags',engine, index_col=False)
    match = pd.merge(event_tag,events,how='right', on='event_id')
    events_tags_joined = pd.merge(match, tags, how='right', on='tag_id')

    # Pick tags corresponding to weekly, monthly and all time freq.
    min_date = events['rating_date'].min()
    max_date = events['rating_date'].max()
    # All time
    tags_name_all = events_tags_joined.groupby('tag_name').count()['tag_id']
    #tags_name_all = tags_name_all[tags_name_all > 20]
    tags_name_all = tags_name_all.sort_values(ascending=False)
    tags_name_all = tags_name_all[:20]
    labels_all = tags_name_all.index

    # Monthly 
    month = events_tags_joined[events_tags_joined['rating_date'] > max_date - datetime.timedelta(30)]
    tags_name_monthly = month.groupby('tag_name').count()['tag_id']
    tags_name_monthly = tags_name_monthly.sort_values(ascending=False)
    tags_name_monthly= tags_name_monthly[:20]
    labels_monthly = tags_name_monthly.index

    # Weekly 
    week = events_tags_joined[events_tags_joined['rating_date'] > max_date - datetime.timedelta(7)]
    tags_name_weekly = week.groupby('tag_name').count()['tag_id']
    tags_name_weekly = tags_name_weekly.sort_values(ascending=False)
    tags_name_weekly= tags_name_weekly[:20]
    labels_weekly = tags_name_weekly.index

    # Plot
    fig, ax = plt.subplots(1,3, figsize=(20,10), dpi=300)
    ax[0].stem(tags_name_all)
    create_subplots(ax=ax[0], labels=labels_all)

    ax[1].stem(tags_name_monthly)
    create_subplots(ax=ax[1], labels=labels_monthly)

    ax[2].stem(tags_name_weekly)
    create_subplots(ax=ax[2], labels=labels_weekly)
    name = 'tag_freq'
    
    return plot_img(fig)

def get_tag_sleep_day_data(engine):
    """
    Return data to be used in naive bayes model.
    priors_tags: counts for all tags.
    priors_rating_sleep: counts for each sleep rating label.
    priors_rating_day: counts for each day rating label.
    posteriors_sleep: tags that occur given each sleep rating label.
    posteriors_day: tags that occur given each day rating label.
    """

    RATING_DAY_MAX = 2
    RATING_DAY_MIN = -2 
    RATING_SLEEP_MAX = 2
    RATING_SLEEP_MIN = -2 

    user_id_ = get_user_id_()

    ratings = pd.read_sql('rating',engine,index_col=False)
    columns_ratings = ['id', 'date', 'user_id','rating_sleep', 'rating_day']
    ratings = ratings[ratings['user_id'] == user_id_][columns_ratings]
    ratings.columns = ratings.columns.str.replace('id','rating_id')
    ratings['rating_sleep'] = ratings['rating_sleep'].clip(RATING_SLEEP_MAX, RATING_SLEEP_MIN)
    ratings['rating_day'] = ratings['rating_day'].clip(RATING_DAY_MAX, RATING_DAY_MIN)


    # TODO: Add support to filter by user_id!
    re_m2m = pd.read_sql('rating_events',engine,index_col=False)
    et_m2m = pd.read_sql('event_tags',engine, index_col=False)
    if ( 'user_id' in re_m2m.columns and 'user_id' in et_m2m.columns ):
        re_m2m=re_m2m[re_m2m['user_id']== user_id_]
        et_m2m=et_m2m[et_m2m['user_id']== user_id_]

    ###### Build a priori distributions for ratings and tags

    ### Get tag frequencies.
    # Merge many-2-many tables: rating_id - event_id and event_id - tag_id
    # to produce rating_id - tag_id data rt_m2m.
    rt_m2m = re_m2m.merge(et_m2m,how='inner', on='event_id')
    rt_m2m = rt_m2m[['rating_id', 'tag_id']]
    rating_ids_tag_ids = ratings.merge(rt_m2m, how='inner', on='rating_id')
    data = rating_ids_tag_ids.groupby('rating_id').agg(list)

    # Separete label columns 
    tags = pd.read_sql('tag',engine,index_col='id')
    tags.index.name = 'tag_id'
    rating_id_tags = rating_ids_tag_ids[['rating_id', 'tag_id']] \
                        .merge(tags,how='inner', left_on='tag_id', right_index=True) \
                        .groupby('rating_id').agg(list)['tag_name']
    #rating_id_tags = rating_ids_tag_ids[['rating_id', 'tag_id']].groupby('rating_id').agg(list)
    label_columns = ['rating_id', 'rating_sleep', 'rating_day']
    labels = (rating_ids_tag_ids[label_columns].drop_duplicates().set_index('rating_id'))
    #print(rating_id_tags)
    #print(labels)
    # An extra merge just to make order is preserved.
    # TODO: Think of a better solution to ensure order is preserved. 
    # Or is it guaranteed to be preserved by drop_duplicates? I think so but not sure.

    return rating_id_tags, labels

from daily.data_analysis.data_models import get_kmodes_data
def make_tag_network(engine, G, fig):

    # Fetch 2D array of tag frequencies and attributes (last 3 cols).
    data, nodes = get_kmodes_data(engine, timespan=90, freq_threshold=4)
    attributes = data[:,-3:]
    data = data[:,:-3]

    #seed = 911
    #seed = 11
    #rng = default_rng(seed)
    rng = default_rng()
    rng.shuffle(data)
    data = data[:]
    
    #print(nodes.shape)

    A = np.zeros((data.shape[1], data.shape[1]))

    nz_args = np.argwhere(data)
    nz_args = list(map(np.argwhere, data))

    print("#####")
    print("data")
    print(data)
    print("NZ_ARGS: ")

    # Complexity an issue here for large N? O(K(N^2)
    # TODO: Note that A will be triangular so the full loop cycle is redundant.
    for entry in nz_args:
        for row in entry:
            row = row[0]
            for col in entry:
                col = col[0]
                if row != col:
                    A[row][col] += 1

    A_pd = pd.DataFrame(A, index=nodes,columns=nodes).astype(int)

    print("Adjacency matrix: ")
    print(A)
    #G.add_nodes_from(nodes)
    G = nx.from_pandas_adjacency(A_pd, create_using = nx.MultiGraph())

    weights = nx.get_edge_attributes(G,'weight').values()
    w = list(weights)
    a = 10
    sigm = lambda x: 1/1+np.exp(-a*x)
    w = list(map(sigm,w))
    print("weights")
    #print(w)
    #print(weights)

    pos = nx.spring_layout(G, k=0.5, iterations=10)
    #pos = nx.circular_layout(G)
    #pos = nx.shell_layout(G)
    #pos = nx.bipartite_layout(G, nodes)
    #pos = nx.kamada_kawai_layout(G)
    #pos = nx.spectral_layout(G)
    #pos = nx.spiral_layout(G, scale=0.1, center=None, 
    #        dim=2, resolution=0.35, equidistant=False) # Nice one

    # Create a gridspec for adding subplots of different sizes
    axgrid = fig.add_gridspec(5, 4)
    ax0 = fig.add_subplot(axgrid[0:3, :])
    nx.draw_networkx(G,pos=pos, ax=ax0,
            alpha=0.7, node_size=3000,
            #width=list(weights),
            width=w,
            edge_color = 'r',
            connectionstyle="arc3,rad=0.4")
    ax0.set_title(nx.info(G))
    ax0.set_axis_off()

    ### DEGREE PLOTS
    # Unpack degree info (dict) from G to desc sorted lists of degree values and labels.
    degree_sequence = sorted(G.degree, key=lambda tple: tple[1], reverse=True)
    degree_labels, degrees = list(map(list, list(zip(*degree_sequence))))

    ax1 = fig.add_subplot(axgrid[3:, :2])
    ax1.plot(degrees, "b-", marker="o")
    ax1.set_title("Degree Rank Plot")
    ax1.set_ylabel("Degree")
    ax1.set_xlabel("Rank")
    create_subplots(ax1, np.array(degree_labels))
    ax1.grid(axis='x')


    ax2 = fig.add_subplot(axgrid[3:, 2:])
    ax2.bar(*np.unique(degrees, return_counts=True))
    ax2.set_title("Degree histogram")
    ax2.set_xlabel("Degree")
    ax2.set_ylabel("# of Nodes")

    output = io.BytesIO() # file-like object for the image
    fig.tight_layout()
    #plt.savefig(output, aspect='auto') # save the image to the stream
    plt.savefig(output) # save the image to the stream
    output.seek(0) # writing moved the cursor to the end of the file, reset
    plt.clf() # clear pyplot
    return Response(output, mimetype='image/png')

    #G.add_edges_from(edges, weight=2)

def create_graph(G, fig, clusters, frequencies):

    print("Frequency")
    print(frequencies)

    count = 0
    for c in clusters: count += len(c)
    color_map = np.empty(count)

    labels = {}

    color_idx = -1
    for cluster_idx, cluster in enumerate(clusters):
        # Create cluster
        color_idx += 1

        # TODO: Circumvent this magic number. 
        # Purpose: Ignore non-string labels. i.e. ratings and meditation.
        cluster = cluster[:-3]
        cluster_frequencies = frequencies[cluster_idx][:-3]
        G.add_nodes_from(cluster)

        edges = []
        fully_connect_cluster(G, cluster, color ='r', weight=10)
        
    pos = nx.spring_layout(G, k=.5, iterations=20)
    #pos = nx.circular_layout(G)
    nx.draw(G, pos, with_labels=True,
            alpha=0.7, node_size=3000)

    #nx.draw(G, pos, 
    #        edge_color=colors, width=50*list(weights),
    #        alpha=0.7,node_size=3000*nodes[:,1], labels=label_map)

    #print(color_map)
            #alpha=0.7, node_size=1000, node_color=color_map)

    output = io.BytesIO() # file-like object for the image
    plt.savefig(output) # save the image to the stream
    output.seek(0) # writing moved the cursor to the end of the file, reset
    plt.clf() # clear pyplot
    return Response(output, mimetype='image/png')

def fully_connect_cluster(G, nodes, color='r', weight=10):
    """ Fully connect node cluster.
    first column is node labels.
    """
    edges = []
    for idx, node in enumerate(nodes):
        for adj_node in nodes: 

            # Skip self loops
            if node == adj_node: continue
            edges.append((node, adj_node))
        
    G.add_edges_from(edges, color=color, weight=weight)


def create_graph_v2(G, fig, clusters, frequencies):

    #frequencies = frequencies[1:3]
    #clusters = clusters[1:3]
    c_ =0
    for f in frequencies: c_+=len(f)
    print("Freq count: ", c_)

    node_count = 0
    for c in clusters: node_count += len(c[:-3])


    # Nodes with columns: Node id, Frequency, Cluster_idx, #TODO: numerical attributes...
    nodes = np.empty((node_count, 3), dtype=int)
    labels = np.empty(node_count, dtype=object)
    label_map = {}

    node_idx = 0
    start=0
    for cluster_idx, c in enumerate(clusters): 
        cluster = c[:-3]

        for in_cluster_idx, node in enumerate(cluster):

            # Add label and frequencies.
            nodes[node_idx,0] = node_idx
            nodes[node_idx,1] = frequencies[cluster_idx][in_cluster_idx]
            labels[node_idx] = node
            label_map[node_idx] = node
            node_idx += 1

        # Add cluster id.
        nodes[start:node_idx,2] = cluster_idx
        start = node_idx

    print("FREQUENCIES")
    #print(frequencies)
    #[cluster_idx][in_cluster_idx]
    print("NODES")
    print(nodes)
    print(nodes.shape)
    print("LABELS")
    #print(labels)
    print(labels.shape)


    G.add_nodes_from(nodes[:,0])

    low, high = nodes[0,2], nodes[-1,2]+1
    norm = mpl.colors.Normalize(vmin=low, vmax=high, clip=True)
    mapper = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.coolwarm)
    #mapper = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.summer)
    
    # Fully connect groups.
    nodes = nodes[nodes[:, 2].argsort()]
    grouped = np.split(nodes[:,0], np.unique(nodes[:, 2], return_index=True)[1][1:])
    for cluster_idx, cluster in enumerate(grouped):
        fully_connect_cluster(G=G, nodes=cluster, 
                color=mapper.to_rgba(cluster_idx), weight=20)

    #nx.draw(G, pos, 
    #        alpha=0.7, node_size=1000)

    edges = []

    labels_unique = np.unique(labels)
    for label in labels_unique:
        doubles = (np.nonzero(label==labels))
        comb = (list(combinations(*doubles,2)))
        for edge in comb: edges.append(edge)

    G.add_edges_from(edges, color=mapper.to_rgba(cluster_idx+1), weight=2)

    colors = nx.get_edge_attributes(G,'color').values()
    weights = nx.get_edge_attributes(G,'weight').values()


    #pos = nx.spring_layout(G, k=.2, iterations=20)
    pos = nx.circular_layout(G)
    nx.draw(G, pos, 
            edge_color=colors, width=50*list(weights),
            alpha=0.7,node_size=3000*nodes[:,1], labels=label_map)

    #nx.draw(G, pos, edge_color=colors, width=list(weights))
    #plt.show()
    #nx.draw(G)

    #print(color_map)
            #alpha=0.7, node_size=1000, node_color=color_map)

    output = io.BytesIO() # file-like object for the image
    plt.savefig(output) # save the image to the stream
    output.seek(0) # writing moved the cursor to the end of the file, reset
    plt.clf() # clear pyplot
    return Response(output, mimetype='image/png')


def time_series(engine):
    rng = default_rng()
    # Sleep ratings
    s= pd.read_sql('rating',engine, index_col=False)
    s['date'] = pd.to_datetime(s['date']).dt.date
    s_date = s
    s_date = s_date.set_index(s_date['date'])
    idx = pd.date_range(min(s['date']), max(s['date']), freq='D')
    s_date.index = pd.DatetimeIndex(s_date.index)
    s_date = s_date.reindex(idx)
    s_date = s_date.set_index(s_date['date'])
    s_date = s_date[:3]
    idx = pd.date_range(min(s_date['date']), max(s_date['date']), freq='D')
    fig, ax = plt.subplots(2, figsize=(8,8))
    fig.autofmt_xdate()
    ax[0].scatter(range(209),s_date['rating_sleep'],s=5)
    ax.plot(s_date['rating_sleep'],c='g')
    ax.plot('date',data=s_date['rating_sleep'])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    ax.set_xticks(np.arange(s_date['date'].size))
    ax.set_xticklabels(s_date['date'])
    ax.xaxis.set_major_locator(mdates.YearLocator(1, month=1, day=1))
    plt.xticks(rotation=30)

def get_user_id_():
    # Allow demoers to view plots generated from my data.
    if current_user.is_anonymous or current_user.id == 2:
        # TODO: Change this to query by my username.
        user_id = 1
    else:
        user_id = current_user.id
        #user_id_= current_user.get_id()

    return user_id

def get_rating_events_tags(engine, columns):
    # Return a complete view to ratings, events and tags.

    user_id_ = get_user_id_()
    # Merge ratings, events and tags to get a df of dates with combinations of tags.
    
    # Read ratings for user
    ratings = pd.read_sql('rating',engine,index_col=False)
    columns_ratings = ['id', 'date', 'user_id','rating_sleep', 'rating_day']
    #ratings = ratings[ratings['user_id'] == user_id_][['id', 'date','user_id',]]
    ratings = ratings[ratings['user_id'] == user_id_][columns_ratings]
    ratings.columns = ratings.columns.str.replace('id','rating_id')

    # Read all tags.
    # TODO: Inefficient, fetch only for user, or lazy=dynamic.
    tags = pd.read_sql('tag',engine,index_col=False)
    tags.columns = tags.columns.str.replace('id','tag_id')

    # Read all events.
    # TODO: Inefficient, fetch only for user, or lazy=dynamic.
    events = pd.read_sql('event',engine, index_col=False)
    events.columns = events.columns.str.replace('id','event_id')

    # Read all rating event associations.
    # TODO: Which first join is sensible here? Inner or right?
    re_m2m = pd.read_sql('rating_events',engine,index_col=False)
    # TODO: Inefficient, fetch only for user, or lazy=dynamic.
    #re_m2m=re_m2m[re_m2m['user_id']== user_id_]
    rating_events = re_m2m \
        .merge(ratings,how='inner', on='rating_id') \
        .merge(events,how='left', on='event_id')

    # Read all event tag associations.
    # Not all events have tags, thus merge innner vs. left
    # dictates whether null tags are included.
    event_tag = pd.read_sql('event_tags',engine, index_col=False)
    # TODO: Inefficient, fetch only for user, or lazy=dynamic.
    #event_tag = event_tag[event_tag['user_id']==user_id_]
    rating_events_tags = rating_events.merge(event_tag,how='inner',on='event_id')

    # Clean
    rating_events_tags.fillna(-1,inplace=True)

    return rating_events_tags[columns]

def polar(engine):
    """

    Resource: https://towardsdatascience.com/polar-heatmaps-in-python-with-matplotlib-d2a09610bc55
    """

    RATING_DAY_MAX = 2
    RATING_DAY_MIN = -2 
    RATING_SLEEP_MAX = 2
    RATING_SLEEP_MIN = -2 

    user_id_ = get_user_id_()

    ratings = pd.read_sql('rating',engine,index_col=False)
    columns_ratings = ['id', 'date', 'user_id','rating_sleep', 'rating_day']
    ratings = ratings[ratings['user_id'] == user_id_][columns_ratings]
    ratings.columns = ratings.columns.str.replace('id','rating_id')
    ratings['rating_sleep'] = ratings['rating_sleep'].clip(RATING_SLEEP_MAX, RATING_SLEEP_MIN)
    ratings['rating_day'] = ratings['rating_day'].clip(RATING_DAY_MAX, RATING_DAY_MIN)

    # Plot
    theta = range(ratings.shape[0])
    r = ratings['rating_sleep']
    r_2 = ratings['rating_day']
    #m = ratings['meditation']

    labels = ['rating_sleep', 'rating_day']

    fig, ax = plt.subplots(2,3, figsize=(20,10), dpi=300,
                        subplot_kw={'projection': 'polar'})
    ax = ax.flatten()
    ax[0].plot(theta, r, 'ro')
    ax[0].set_title(labels[0])
    #ax[0].legend()

    ax[1].plot(theta, r_2, 'bx')
    ax[1].set_title(labels[1])

    ax[2].plot(theta, r, 'ro')
    ax[2].plot(theta, r_2, 'bx')
    ax[2].set_title('Sleep and Day ratings')
    fig.legend(labels)

    for axis in ax:
        axis.set_yticks([-2, -1, 0, 1, 2])

    return plot_img(fig)

from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
def polar_heat_map(engine, label, heat, ax, timespan=0, cycle=4):
    """

    Resource: https://towardsdatascience.com/polar-heatmaps-in-python-with-matplotlib-d2a09610bc55
    TODO: ADD dates/seasons as ticks on outer rim.
    """

    RATING_MAX = 2
    RATING_MIN = -2 

    user_id_ = get_user_id_()

    ratings = pd.read_sql('rating',engine,index_col=False)
    if timespan != 0:
        max_date = ratings['date'].max()
        #ratings = ratings[ratings['date'] > max_date - datetime.timedelta(timespan)]
        ratings = ratings.iloc[-timespan:]
    columns_ratings = ['id', 'date', 'user_id', label, heat]
    ratings = ratings[ratings['user_id'] == user_id_][columns_ratings]
    ratings.columns = ratings.columns.str.replace('id','rating_id')
    ratings[label] = ratings[label].clip(RATING_MAX, RATING_MIN)

    # Plot
    ratings = ratings[[label,heat]]
    ratings.dropna()

    theta = np.arange(0,360,360/(ratings.shape[0]))
    theta = theta[::-1]
    r = ratings[label]; r += r.abs().max()+1
    temperature = ratings[heat]
    avg_temp = []
    patches = []

    columns = ['r', 'heat', 'theta']
    df = pd.DataFrame(list(zip(r,temperature,theta)),
            columns=columns)

    #pr = df[['r', 'theta','heat']]
    #pr['r'] = pr['r']-3
    #print(pr)

    ntheta  =int(df.shape[0]/cycle); dtheta = 360/ntheta;
    nradius = r.max() - r.min()+1; dradius = max(r)/nradius;
    
    # Create wedges starting from outer radius.
    for nr in range(nradius, 0, -1):
        start_r = (nr-1)*dradius
        end_r = nr*dradius

        for nt in range(0,ntheta):
            start_t = nt*dtheta
            end_t = (nt+1)*dtheta

            stripped = df[(df['r']>start_r) & (df['r']<=end_r) &
                            (df['theta']>=start_t) & (df['theta']<end_t)]
            
            avg_temp.append(stripped['heat'].mean())
            wedge = mpatches.Wedge(0,end_r, start_t, end_t)
            patches.append(wedge)

    # Color generator https://coolors.co/c97b84-a85751-7d2e68-251351-040926
    #colors = ['#000052','#0c44ac','#faf0ca','#ed0101','#970005'] 
    #colors = ["#04151f","#183a37","#efd6ac","#c44900","#432534"]
    colors = ["#c97b84","#a85751","#7d2e68","#251351","#040926"]
    cm = LinearSegmentedColormap.from_list('custom', colors,N=10)
    cm.set_bad(color='white')

    # Assign patch colors
    #avg_temp = np.array(avg_temp)
    #print(avg_temp)
    #avg_temp = avg_temp[~np.isnan(avg_temp)]
    #print(avg_temp)
    #print(np.array(avg_temp).max())
    #print(np.array(avg_temp).min())
    collection = PatchCollection(patches, linewidth=0.0,
            edgecolor=['#000000' for x in avg_temp],
            facecolor=cm([( x )/( temperature.abs().max() ) for x in avg_temp]))


    #ax.set_title(f"{label} from {ratings[label].min()} to {ratings[label].max()}")
    ax.set_title(f"{label} from {RATING_MIN} to {RATING_MAX}" \
            f" for past {timespan} days with {cycle} cycle(s)." \
            f" Temperature from {heat}.")
    ax.add_collection(collection)

    return ax

from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
def polar_nice(engine):
    """
    Resource: https://towardsdatascience.com/polar-heatmaps-in-python-with-matplotlib-d2a09610bc55
    """


    labels = ['rating_sleep', 'rating_day']

    fig, ax = plt.subplots(2,2, figsize=(20,10), dpi=200,
                        edgecolor='w', facecolor='w')

    ax = ax.flatten()
    #polar_heat_map(engine=engine, label=labels[0], heat='meditation',
    polar_heat_map(engine=engine, label=labels[0], heat='meditation',
                    timespan=7, ax=ax[0], cycle=1)

    #polar_heat_map(engine=engine, label=labels[0], heat=labels[0],
    #TODO: Above gives error at line 356. figure out why!
    polar_heat_map(engine=engine, label=labels[0], heat='meditation',
                    timespan=30, ax=ax[1], cycle=1)

    polar_heat_map(engine=engine, label=labels[0], heat='meditation',
                    timespan=4*30, ax=ax[2], cycle=1)
    polar_heat_map(engine=engine, label=labels[0], heat='meditation',
                    timespan=3*4*30, ax=ax[3], cycle=1)

    for axis in ax:
        axis.set_xlim(-5,5); axis.set_ylim(-5,5)
        axis.axis('off') ;axis.axis('equal')
    plt.tight_layout()
    return plot_img(fig)
