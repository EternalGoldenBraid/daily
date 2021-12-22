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
import json

import io
from flask import Response, jsonify
from matplotlib.backends.backend_agg import FigureCanvasAgg as FC
import datetime

from daily.data_analysis.data_models import (tag_freq,
        time_series, cluster, 
        naive_bayes, sk_naive_bayes_multinomial)

from daily.data_analysis.plots import (polar, polar_nice)

@bp.route("/data/index")
def index():

    return render_template("data_analysis/index.html")

@bp.route("/plots", methods=["GET"])
def plots():
    engine = db.get_engine()
    target = request.args.get('target')
    if target == 'tag_freq':
        return tag_freq(engine)
    elif target == 'eigen':
        return cluster(engine)
    elif target == 'polar':
        return polar(engine)
    elif target == 'polar_heat':
        return polar_nice(engine)
    return redirect(url_for('data_analysis.index'))

@bp.route("/data", methods=["GET", "POST"])
def data():
    engine = db.get_engine()
    args = request.args
    summary = None

    target = request.args.get('target')
    if target == 'nbayes':
        re_train = args.get('re_train')
        path = os.getcwd() +'/daily/data_analysis/summary.json'
        sk_naive_bayes_multinomial(engine, 
            save_path=path, evaluate_model=re_train)
        #naive_bayes(engine)
        with open(path,"r") as file: 
            summary = json.load(file)

    print(summary)
    return render_template("data_analysis/index.html", summary=summary)
                

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

