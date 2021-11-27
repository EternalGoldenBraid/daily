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

import numpy as np
import pandas as pd
from numpy.random import default_rng
import os





@bp.route("/data", methods=["GET", "POST"])
@login_required
def data():

    rng = default_rng()
    fig, ax = plt.subplots()

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
    print(s_date[:3])
    ax.plot(s_date['rating_sleep'])
    ax.set_xticks(np.arange(s_date['date'].size))
    ax.set_xticklabels(s_date['date'])
    plt.xticks(rotation=30)

    #plt.gcf().autofmt_xdate()

    #print (mpld3.fig_to_html(fig1, d3_url=None, mpld3_url=None, no_extras=False, template_type='general', figid=None, use_http=False))
    html = mpld3.fig_to_html(fig)
    file = open("daily/templates/data_analysis/data.html","w")
    file.write(html)
    file.close()
    return render_template("data_analysis/data.html")
