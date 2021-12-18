from daily.models import User, Rating, Tag, rating_as, event_as
from flask import Response
from flask_login import current_user

#import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from collections import Counter
import numpy as np
import pandas as pd
from numpy.random import default_rng
#from scipy import stats

import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FC
import datetime



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

def create_subplots(ax, labels):
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

def cluster(engine):

    # Allow demoers to view plots generated from my data.
    if current_user.is_anonymous or current_user.id == 2:
        # TODO: Change this to query by my username.
        user_id_ = 1
    else:
        user_id_ = current_user.id
        #user_id_ = current_user.get_id()

    # Merge ratings, events and tags to get a df of dates with combinations of tags.
    
    # Read ratings for user
    ratings = pd.read_sql('rating',engine,index_col=False)
    ratings = ratings[ratings['user_id'] == user_id_][['id', 'date','user_id']]
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
    rating_events_tags = rating_events_tags[['date','tag_id']]

    # Clean
    rating_events_tags.fillna(-1,inplace=True)
    rating_events_tags['tag_id']=rating_events_tags['tag_id'].astype(int)

    tag_list = rating_events_tags.groupby('date').agg(list)

    #print(tag_list[100:105])
    #print(tag_list[99:100].index)
    print("TESTING")
    for i in range(1,4):
        foo = tag_list[i-1:i].iloc[0]
        foo=np.array(foo)
        print(foo)
        print("length: ", len(foo))
        print("")

    

    # Produce dictionary for each rating/date where
    # key is tag_id and value it's count in that rating/date.
    date_tags = list(map(Counter, tag_list['tag_id']))
    dates = rating_events_tags['date']

    data = np.zeros((tag_list.shape[0], tags['tag_id'].shape[0]))
    # TODO: More optimal way than for loop
    for row in range(data.shape[0]):
        for col in range(data.shape[1]):
            data[row][col]=date_tags[row][col]
    
    # TODO: Get eigenvectors out
    mean = np.mean(data,axis=0)
    data = (data-mean)
    #data = (data-mean)/np.std(data,axis=0)

    # Data rows are tags, columns are days.
    # Element x_ij is the expression level of the i_th
    # tag on the j_th day.
    data = data.T
    cov = np.dot(data,data.T)

    #method = "random"
    method = "not random"
    if method != "random":
        e_values, e_vectors = np.linalg.eigh(cov)

        # Sort eigenvalues and their eigenvectors in descending order
        e_ind_order = np.flip(e_values.argsort())
        e_values = e_values[e_ind_order]
        # note that we have to re-order the columns, not rows
        e_vectors = e_vectors[:, e_ind_order] 
    else:
        r, p, q = 20, 5, 5
        u, s, vt = rSVD(data,r,q,p)
        e_values = np.square(s)
        e_vectors = vt.T
    

    # pca
    #prin_comp_evd = data @ e_vectors

    """ 3D plot """
    #fig_pca = plt.figure(figsize=(10,10))
    #ax_pca = fig_pca.add_subplot(111, projection='3d')
    #ax[1].scatter(
    #ax_pca.scatter(
        #prin_comp_evd[:, 0], prin_comp_evd[:, 1], prin_comp_evd[:, 2]
        #)


    """ eigen plot """
    fig, ax = plt.subplots(2,2, figsize=(8,8))
    print(ax.shape)
    ax[0][0].plot(e_values)
    ax[0][0].set_title("Eigenvalues")

    k = 200
    ax[1][0].plot(e_values[:k])
    ax[1][0].set_title(f"Eigenvalues for first {k} tags.")

    sum_eig = np.sum(e_values)
    cum_sum = np.cumsum(e_values/sum_eig)
    r = 0.7
    ax[0][1].plot(cum_sum)
    ax[0][1].set_title(f"Cumulative sum, capture {r*100}%")
    ax[0][1].axhline(r, color='r')


    cum_sum_r = cum_sum[cum_sum > r]
    total = data.shape[0]
    r_count = len(cum_sum_r)
    ax[1][1].plot(cum_sum_r)
    ax[1][1].set_title(
            f"{r_count}/{total} = {r_count/total*100:.1f}%  tags required.")

    # Find tags corresponding to eigenvectors.
    #for vector in e_vectors:

    print("")
    print("FIND")

    # TODO: How does an eigenvector's entry correspond to TAGID??
    tag_id = np.flatnonzero(e_vectors[0])
    print(tag_id)
    print(type(tag_id))
    t = tags[tags['tag_id']==tag_id[0]]
    print(t)
    #for idx in range(4):
        #indices = (e_vectors[idx].nonzero())
        #for i in indices:


    #print(e_vectors[0][e_vectors[0] != 0])
    #idx = (np.argmax(e_vectors[0]))
    #print(idx)
    #tag_id = ((e_vectors[0][idx]))
    #print(tag_id)
    #print(tags[tags['tag_id']==tag_id])
    return plot_img(fig)

def bayes(engine):
    # Lesson 1:
    # Do naive bayes on tags. I.e. tag occurences are i.i.d.

    RATING_DAY_MAX = 2
    RATING_DAY_MIN = -2 
    RATING_SLEEP_MAX = 2
    RATING_SLEEP_MIN = -2 

    user_id_ = get_user_id_()

    # Fetch data
    #columns = ['rating_id', 'rating_sleep', 'rating_day', 'tag_id']
    #data = get_rating_events_tags(engine, columns)

    ratings = pd.read_sql('rating',engine,index_col=False)
    columns_ratings = ['id', 'date', 'user_id','rating_sleep', 'rating_day']
    ratings = ratings[ratings['user_id'] == user_id_][columns_ratings]
    ratings.columns = ratings.columns.str.replace('id','rating_id')
    ratings['rating_sleep'] = ratings['rating_sleep'].clip(RATING_SLEEP_MAX, RATING_SLEEP_MIN)
    ratings['rating_day'] = ratings['rating_day'].clip(RATING_DAY_MAX, RATING_DAY_MIN)

    # Split to training and testing data.
    ratings_tets = ratings.iloc[-10:]
    ratings = ratings[:-10]

    # TODO: Add support to filter by user_id!
    re_m2m = pd.read_sql('rating_events',engine,index_col=False)
    et_m2m = pd.read_sql('event_tags',engine, index_col=False)
    if ( 'user_id' in re_m2m.columns and 'user_id' in et_m2m.columns ):
        re_m2m=re_m2m[re_m2m['user_id']== user_id_]
        et_m2m=et_m2m[et_m2m['user_id']== user_id_]

    tags = pd.read_sql('tag',engine,index_col=False)
    tags.columns = tags.columns.str.replace('id','tag_id')

    events = pd.read_sql('event',engine, index_col=False)
    events.columns = events.columns.str.replace('id','event_id')

    # Build a priori distributions for ratings and tags

    ### Get tag frequencies.
    # Merge many-2-many tables: rating_id - event_id and event_id - tag_id
    # to produce rating_id - tag_id data rt_m2m.
    rt_m2m = re_m2m.merge(et_m2m,how='inner', on='event_id')
    rt_m2m = rt_m2m[['rating_id', 'tag_id']]

    ## DEBUG
    print("TEST")
    #print(rt_m2m[-20:])
    #print((re_m2m.merge(et_m2m,how='inner', on='event_id')).size)
    #print((re_m2m.merge(et_m2m,how='left', on='event_id')).size)
    #print((re_m2m.merge(et_m2m,how='right', on='event_id')).size)
    ## END DEBUG

    tag_prior = rt_m2m.groupby('tag_id').count()

    # Get rating frequencies.
    ratings_tags = ratings.merge(rt_m2m, how='inner', on='rating_id')
    prior_rating_day = ratings_tags[['tag_id', 'rating_day']]
    prior_rating_day = prior_rating_day.groupby('rating_day').count()['tag_id']

    prior_rating_sleep = ratings_tags[['tag_id', 'rating_sleep']]
    prior_rating_sleep = prior_rating_sleep.groupby('rating_sleep').count()['tag_id']

    # Calculate a posteriori distributions for tags given ratings.
    #print(prior_rating_day)
    print("CHECK1")
    #print(prior_rating_sleep)
    #print(tag_prior)

    #print(rt_m2m[-5:])
    #print(ratings_tags[-5:])

    # Posterior for sleep_rating
    rating_sleep_tags = ratings_tags[['rating_sleep', 'tag_id']]
    # TODO: Potentially very slow grouping?
    # See https://medium.com/@aivinsolatorio/optimizing-pandas-groupby-50x-using-numpy-to-speedup-an-agent-based-model-a-story-of-8b0d25614915
    rating_sleep_group = rating_sleep_tags.groupby('rating_sleep').agg(list)

    # Scale indices from -2 to 2 --> 0 to 4.
    indices = rating_sleep_group.index+rating_sleep_group.index.max()
    if indices[0] != 0: 
        # Indices are expected to be between 0 and some positive integer.
        return redirect(url_for('data_analysis.index')), 500

    posteriors = [np.array(list_[0]) for list_ in rating_sleep_group.values]

    # Posterior for day_rating
        


def rSVD(X,r,q,p):
    """
    r: Target rank
    q: Power iterations
    p: Oversampling factor for accuracy gain
    """
    #X=X.T # Variables to rows
    # Step 1: Sample column space of X with P matrix
    X_columns = X.shape[1]
    P = np.random.rand(X_columns,r+p)
    # Tall and skinny, will represent the column space well
    #due to the random matrix sampling the data matrix
    Z = X @ P

    # Power iterations take care of pushing down the singular values,
    # such that r can be kept low.
    for k in range(q):
        Z = X @ (X.T @ Z)
   
        # Fetch an orthonormal basis for the column space of X
        Q , R = np.linalg.qr(Z,mode='reduced')
   
        # Project X to the orthornormal basis. X into Q.
        Y = Q.T @ X
        # SVD for the projection. S and VT are the same as for SVD of X.
        UY, S, VT = np.linalg.svd(Y, full_matrices=False)
        U = Q @ UY
    return U, S, VT

