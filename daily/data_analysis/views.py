from daily.data_analysis import bp
from daily import db
from daily.models import User, Rating, Tag, rating_as, event_as
from daily.data_analysis.forms import KPrototypes_network_form, KPrototypes_cost_form

from flask import Response, jsonify
from flask import (render_template, redirect, flash,
        url_for, request)
from flask_login import (current_user, login_user,
                    logout_user, login_required)

#import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import networkx as nx
import numpy as np
import pandas as pd
from numpy.random import default_rng
#from scipy import stats

import os
import json
import io
from collections import Counter

from matplotlib.backends.backend_agg import FigureCanvasAgg as FC
import datetime

from daily.data_analysis.data_models import (tag_freq,
        time_series, 
        cluster, kmodes_cluster, kprototypes_cluster, kmodes_elbow_cost,
        naive_bayes, sk_naive_bayes_multinomial)

from daily.data_analysis.plots import (
            polar, polar_nice,
            create_graph, create_graph_v2)

from daily.data_analysis.helpers import plot_img

@bp.route("/data/index")
def index():

    kproto_network_form = KPrototypes_network_form()
    kproto_cost_form = KPrototypes_cost_form()
    return render_template("data_analysis/index.html",
            kproto_network = kproto_network_form,
            kproto_cost = kproto_cost_form)

@bp.route("/plots", methods=["GET", "POST"])
def plots():
    engine = db.get_engine()
    target = request.args.get('target')

    kproto_network_form = KPrototypes_network_form()
    kproto_cost_form = KPrototypes_cost_form()

    if target == 'tag_freq':
        return tag_freq(engine)
    elif target == 'eigen':
        #return cluster(engine)
        #cluster(engine)
        return render_template("data_analysis/kmodes.html")
    elif target == 'polar':
        return polar(engine)
    elif target == 'polar_heat':
        return polar_nice(engine)
    elif target == 'kmodes_network':

        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'kmodes_cluster.json')

        #path = os.getcwd() +'/daily/data_analysis/kmodes_clusters.json'
        #TODO: Add support for range of k plots returned.
        k = kproto_network_form.k.data
        timespan = kproto_network_form.timespan.data

        # TODO Add tickbox for retraining.
        retrain=True
        if retrain: 
            #kmodes_cluster(engine, path = path, timespan=timespan,freq_threshold=4)
            kprototypes_cluster(engine,path = path,
                    k=k,timespan=timespan,freq_threshold=2)
        with open(path,"r") as file: 
            clusters = json.load(file)
        G = nx.Graph()
        #G = nx.cubical_graph()
        fig = plt.figure(figsize=(10,10))
        #return create_graph(G=G,fig=fig,
        #        clusters=clusters[f'k{k}'],
        #        weights=clusters[f'k{k}_counts'])
        return create_graph_v2(G=G,fig=fig,
                clusters=clusters[f'k{k}'],
                frequencies=clusters[f'k{k}_counts'])
    elif target == 'kmodes_elbow':
        path = os.getcwd() +'/daily/data_analysis/kmodes_clusters.json'

        # TODO: Add retrain flag to decide whether to serve and old or newly trained img.
        return kmodes_elbow_cost(engine)

    return render_template("data_analysis/index.html",
            kproto_network = kproto_network_form,
            kproto_cost = kproto_cost_form)


@bp.route("/data/kmodes_data", methods=["GET"])
def kmodes_data():
    """ Endpoint for data queries for kmodes """

    path = os.getcwd() +'/daily/data_analysis/kmodes_clusters.json'
    with open(path,"r") as file: 
        clusters = json.load(file)
    return jsonify(clusters)

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
    elif target == 'kmodes':
        re_train = args.get('re_train')
        #path = os.getcwd() +'/daily/data_analysis/summary.json'
        #sk_naive_bayes_multinomial(engine, 
        #    save_path=path, evaluate_model=re_train)
        ##naive_bayes(engine)
        #with open(path,"r") as file: 
        #    summary = json.load(file)
        #return render_template("data_analysis/kmodes.html")

        return kmodes_elbow_cost(engine)

    kproto_network_form = KPrototypes_network_form()
    kproto_cost_form = KPrototypes_cost_form()
    return render_template("data_analysis/index.html",
            kproto_network = kproto_network_form,
            kproto_cost = kproto_cost_form)
                

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

