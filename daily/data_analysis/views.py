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

from daily.data_analysis.data_models import (tag_freq,
        time_series, cluster, bayes)

@bp.route("/data/index")
def index():

    return render_template("data_analysis/index.html")

@bp.route("/data", methods=["GET", "POST"])
def data():
    engine = db.get_engine()

    target = request.args.get('target')
    if target == 'tag_freq':
        return tag_freq(engine)
    elif target == 'eigen':
        return cluster(engine)
    elif target == 'bayes':
        bayes(engine)
        return render_template("data_analysis/index.html")

    return redirect(url_for('data_analysis.index'))
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

