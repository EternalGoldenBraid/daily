from daily.models import User, Rating, Tag, rating_as, event_as
from flask import (render_template, redirect, flash,
        url_for, request)
from flask_login import (current_user, login_user,
                    logout_user, login_required)

from daily.data_analysis import bp
from daily import db

#import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from collections import Counter
import numpy as np
import pandas as pd
from numpy.random import default_rng
#from scipy import stats
import os

import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FC
import datetime




@bp.route("/data", methods=["GET", "POST"])
@login_required
def data():
    engine = db.get_engine()

    #return tag_freq(engine)
    return cluster(engine)

def save_plot(fig, name, form=None):

    path = "plots/"
    filename = path+name+"."+form
    plt.savefig("daily/static/"+filename, format=form)
    #plt.savefig(filename)
    return filename
        
@bp.route("/display_plot", methods=["GET", "POST"])
@login_required
def display_plot():
    print("DISPLAY_PLOT ARGS: ", request.args.get("filename"))
    return redirect(
            url_for('static', 
            filename=request.args.get("filename")),
            code=301)

def plot_img(fig):
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

def cluster(engine):

    # Merge ratings, events and tags to get a df of dates with combinations of tags.
    ratings = pd.read_sql('rating',engine,index_col=False)
    ratings = ratings[ratings['user_id'] == current_user.id][['id', 'date','user_id']]
    ratings.columns = ratings.columns.str.replace('id','rating_id')

    tags = pd.read_sql('tag',engine,index_col=False)
    tags.columns = tags.columns.str.replace('id','tag_id')

    events = pd.read_sql('event',engine, index_col=False)
    events.columns = events.columns.str.replace('id','event_id')

    re_m2m = pd.read_sql('rating_events',engine,index_col=False)
    re_m2m=re_m2m[re_m2m['user_id']== current_user.id]
    rating_events = re_m2m \
        .merge(ratings,how='right', on='rating_id') \
        .merge(events,how='left', on='event_id')

    event_tag = pd.read_sql('event_tags',engine, index_col=False)
    event_tag = event_tag[event_tag['user_id']==current_user.id]
    rating_events_tags = rating_events.merge(event_tag,how='left',on='event_id')
    rating_events_tags = rating_events_tags[['date','tag_id']]
    rating_events_tags.fillna(-1,inplace=True)
    rating_events_tags['tag_id']=rating_events_tags['tag_id'].astype(int)

    tag_list = rating_events_tags.groupby('date').agg(list)

    date_tags = list(map(Counter, tag_list['tag_id']))

    data = np.zeros((tag_list.shape[0], tags['tag_id'].shape[0]))
    for row in range(data.shape[0]):
        for col in range(data.shape[1]):
            data[row][col]=date_tags[row][col]
    
    # TODO: Get eigenvectors out
    #data = (data-np.mean(data,axis=0))/np.std(data,axis=0)
    data = (data-np.mean(data,axis=0))
    cov = np.cov(data, rowvar=False)

    #method = "random"
    method = "not random"
    if method != "random":
        e_values, e_vectors = np.linalg.eigh(cov)
    else:
        r, p, q = 20, 5, 5
        u, s, vt = rSVD(data,r,q,p)
        e_values = np.square(s)
        e_vectors = vt.T
    

    # Sort eigenvalues and their eigenvectors in descending order
    e_ind_order = np.flip(e_values.argsort())
    e_values = e_values[e_ind_order]
    # note that we have to re-order the columns, not rows
    e_vectors = e_vectors[:, e_ind_order] 
    # pca
    prin_comp_evd = data @ e_vectors

    """ 3D plot """
    #fig_pca = plt.figure(figsize=(10,10))
    #ax_pca = fig_pca.add_subplot(111, projection='3d')
    #ax[1].scatter(
    #ax_pca.scatter(
        #prin_comp_evd[:, 0], prin_comp_evd[:, 1], prin_comp_evd[:, 2]
        #)


    """ eigen plot """
    fig, ax = plt.subplots(3, figsize=(8,8))
    #ax[1].scatter(
    ax[1].plot(np.cumsum(e_values)/np.sum(e_values))


    """ Eigen tags/days """
    N = 2
    #e_vectors = e_vectors[:,:N]
    
    # Sort the e_vector weighted by it's element values
    e_vec= e_vectors[:,1]
    order = np.flip(e_vec.argsort())
    e_vec = e_vec[order]

    ax[0].plot(np.cumsum(e_vec)/np.sum(e_vec))

    threshold = np.max(cov)*0.9
    cov = cov[cov > threshold]
    print([cov>threshold])

    #fig_cov,ax_cov = plt.subplots(1)
    #ax_cov.imshow(cov)

    idx = np.transpose(np.nonzero(e_vectors))
    #idx = np.transpose(np.nonzero(e_vectors[e_vectors >= 1]))
    
    #print(e_vectors)
    #print(idx.shape)
    #print(idx)
    #print(tags[idx])
    print(tags.shape)

    #eigen_day_idx = eigen_id[0,:]
    #foo = e_vectors[eigen_day_idx]
    #print(foo)

    return plot_img(fig)

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

