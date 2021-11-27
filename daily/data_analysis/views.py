from daily.models import User, Rating, Tag, rating_as, event_as
from flask import (render_template, redirect, flash,
        url_for, request)
from flask_login import (current_user, login_user,
                    logout_user, login_required)

from daily.data_analysis import bp
from daily import db

import matplotlib
import matplotlib.pyplot as plt,mpld3
import matplotlib.dates as mdates

from collections import Counter
import numpy as np
import pandas as pd
from numpy.random import default_rng
import os





@bp.route("/data", methods=["GET", "POST"])
@login_required
def data():

    rng = default_rng()
    #fig, ax = plt.subplots(2, figsize=(8,8), projection='3d')

    """ Sleep ratings """
    engine = db.get_engine()
    s= pd.read_sql('rating',engine, index_col=False)

    s['date'] = pd.to_datetime(s['date']).dt.date
    #s['date'] = pd.to_datetime(s['date']).dt.normalize()


    #s_date = s[['date','rating_sleep']]
    s_date = s
    #s_date = s_date.set_index(s_date['date'])

    #idx = pd.date_range(min(s['date']), max(s['date']), freq='D')
    #s_date.index = pd.DatetimeIndex(s_date.index)
    #s_date = s_date.reindex(idx)

    #s_date = s_date.set_index(s_date['date'])
    #s_date = s_date[:3]
    #idx = pd.date_range(min(s_date['date']), max(s_date['date']), freq='D')


    #fig.autofmt_xdate()
    #ax[0].scatter(range(209),s_date['rating_sleep'],s=5)
    #ax.plot(s_date['rating_sleep'],c='g')
    #ax.plot('date',data=s_date['rating_sleep'])
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
    #ax.xaxis.set_major_locator(mdates.MonthLocator())
    #ax.xaxis.set_minor_locator(mdates.MonthLocator())
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    #ax.set_xticks(np.arange(s_date['date'].size))
    #ax.set_xticklabels(s_date['date'])
    #ax.xaxis.set_major_locator(mdates.YearLocator(1, month=1, day=1))
    #plt.xticks(rotation=30)



    """ TAGS """
    tags = pd.read_sql('tag',engine, index_col=False)
    tags.columns = tags.columns.str.replace('id','tag.id')

    event_tag = pd.read_sql('event_tags',engine, index_col=False)

    events = pd.read_sql('event',engine, index_col=False)
    events.columns = events.columns.str.replace('id','event.id')

    match = pd.merge(event_tag,events,on='event.id')
    match = pd.merge(match,tags,on='tag.id')

    tags_name = match.groupby('rating_date')['tag_name'].apply(list)
    tags_id = match.groupby('rating_date')['tag.id'].agg(list) # Series

    data = np.zeros((events.size,tags.size))
    for row, day in enumerate(tags_id):
        a = Counter(day)
        for col in a.keys():
            data[row][col]=a[col]


    
    print(data)
    #data = (data-np.mean(data,axis=0))/np.std(data,axis=0)
    data = (data-np.mean(data,axis=0))
    cov = np.cov(data, rowvar=False)
    e_values, e_vectors = np.linalg.eigh(cov)
    print(data)

    # Sort eigenvalues and their eigenvectors in descending order
    e_ind_order = np.flip(e_values.argsort())
    e_values = e_values[e_ind_order]
    # note that we have to re-order the columns, not rows
    e_vectors = e_vectors[:, e_ind_order] 
    # pca
    prin_comp_evd = data @ e_vectors

    print(prin_comp_evd)

    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111, projection='3d')
    #ax[1].scatter(
    ax.scatter(
        prin_comp_evd[:, 0], prin_comp_evd[:, 1], prin_comp_evd[:, 2]
        )
    plt.show()

    #plt.gcf().autofmt_xdate()

    #print (mpld3.fig_to_html(fig1, d3_url=None, mpld3_url=None, no_extras=False, template_type='general', figid=None, use_http=False))
    #html = mpld3.fig_to_html(fig)
    #file = open("daily/templates/data_analysis/data.html","w")
    #file.write(html)
    #file.close()
    return render_template("data_analysis/data.html")
