from daily.models import User, Rating, Tag, rating_as, event_as
from flask import (render_template, redirect, flash,
        url_for, request)
from flask_login import (current_user, login_user,
                    logout_user, login_required)

from daily.data_analysis import bp
from daily import db

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from collections import Counter
import numpy as np
import pandas as pd
from numpy.random import default_rng
#from scipy import stats
import os





@bp.route("/data", methods=["GET", "POST"])
@login_required
def data():
    engine = db.get_engine()

    filenames = []
    filenames.append(tag_freq(engine))
    return render_template("data_analysis/data.html",filenames=filenames)

def save_plot(fig, name, type="img", form=None):

    if type=="html":
        #html = mpld3.fig_to_html(
        #        fig1, d3_url=None, mpld3_url=None, no_extras=False,
        #        template_type='general', figid=None, use_http=False))
        html = mpld3.fig_to_html(fig)
        file = open(f"daily/templates/data_analysis/{name}.html","w")
        file.write(html)
        file.close()
        return name
    elif type=="img":
        path = "plots/"
        filename = path+name+"."+form
        plt.savefig("daily/static/"+filename, format=form)
        #plt.savefig(filename)
        return filename
        
@bp.route("/display_plot", methods=["GET", "POST"])
@login_required
#def display_plot(filename):
def display_plot():
    #print("DISPLAY_PLOT ARGS: ", filename)
    #print(help(request.args))
    print("DISPLAY_PLOT ARGS: ", request.args.get("filename"))
    return redirect(
            url_for('static', 
            filename=request.args.get("filename")),
            code=301)

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


def tag_freq(engine):
    tags = pd.read_sql('tag',engine, index_col=False)
    tags.columns = tags.columns.str.replace('id','tag.id')

    event_tag = pd.read_sql('event_tags',engine, index_col=False)

    events = pd.read_sql('event',engine, index_col=False)
    events.columns = events.columns.str.replace('id','event.id')

    # Add tags associated with events to events.
    match = pd.merge(event_tag,events,how='right', on='event.id')
    match = pd.merge(match, tags, how='right', on='tag.id')
    tags_name = match.groupby('tag_name').count()['tag.id']

    tags_name = tags_name[tags_name > 20]
    tags_name = tags_name.sort_values(ascending=False)

    labels = tags_name.index
    
    # Plot
    fig, ax = plt.subplots(1, figsize=(20,10), dpi=300)
    ax.stem(tags_name)

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

    #ax.grid(True)
    plt.tight_layout()
    name = 'tag_freq'
    name = save_plot(fig,name=name,type="img",form='png')

    return name


def kmeans(engine, data, k:int = 5):

    k = k

def cluster(engine):
    """ TAGS """
    tags = pd.read_sql('tag',engine, index_col=False)
    tags.columns = tags.columns.str.replace('id','tag.id')

    event_tag = pd.read_sql('event_tags',engine, index_col=False)

    events = pd.read_sql('event',engine, index_col=False)
    events.columns = events.columns.str.replace('id','event.id')

    # Add tags associated with events to events.
    match = pd.merge(event_tag,events,how='right', on='event.id')
    #match = pd.merge(event_tag,events,how='left', on='event.id')

    # Include tag names
    #match = pd.merge(match,tags,on='tag.id')
    #tags_name = match.groupby('rating_date')['tag_name'].apply(list)

    #tags_id = match.groupby('rating_date')['tag.id'].agg(list) # Series
    tags_id = match.groupby('rating_date').agg(list) # Series

    days = (max(tags_id.index) - min(tags_id.index))
    days = days.days
    data = np.zeros((days,max(tags['tag.id'])))
    for row, day in enumerate(tags_id.index):
        print(row)
        print(day)
        input()
        a = Counter(tags_id[day])
        input()
        for col in a.keys():
            data[row][col]=a[col]
    
    #data = (data-np.mean(data,axis=0))/np.std(data,axis=0)
    data = (data-np.mean(data,axis=0))
    cov = np.cov(data, rowvar=False)

    method = "random"
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

    #plt.show()
    #print (mpld3.fig_to_html(fig1, d3_url=None, mpld3_url=None, no_extras=False, template_type='general', figid=None, use_http=False))
    #html = mpld3.fig_to_html(fig)
    #file = open("daily/templates/data_analysis/data.html","w")
    #file.write(html)
    #file.close()

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

