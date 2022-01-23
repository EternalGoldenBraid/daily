from daily.data_analysis import bp
from daily import db
from daily.models import User, Rating, Tag, rating_as, event_as
from daily.data_analysis.forms import (KPrototypes_network_form,
        Kmodes_elbow_form, Tag_network_form)

from flask import Response, jsonify, session
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
            create_graph, create_graph_v2,
            plot_tag_graph)

from daily.data_analysis.helpers import plot_img

@bp.route("/data/index")
def index():

    if not 'summary' in session.keys(): summary=None
    else: summary = session['summary']

    kproto_network_form = KPrototypes_network_form()
    kmodes_elbow_form = Kmodes_elbow_form()
    tag_network_form = Tag_network_form()
    return render_template("data_analysis/index.html",
            kproto_network = kproto_network_form,
            kmodes_elbow=kmodes_elbow_form,
            tag_network=tag_network_form,
            summary=summary)

@bp.route("/plots", methods=["GET", "POST"])
def plots():
    engine = db.get_engine()
    target = request.args.get('target')

    kproto_network_form = KPrototypes_network_form()
    kmodes_elbow_form = Kmodes_elbow_form()

    if target == 'tag_freq':
        return tag_freq(engine)
    elif target == 'eigen':
        #return cluster(engine)
        cluster(engine)
    elif target == 'polar':
        return polar(engine)
    elif target == 'polar_heat':
        return polar_nice(engine)
    elif target == 'kmodes_network':
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

        form = kproto_network_form
        #TODO: Add support for range of k plots returned.
        k = form.k.data
        timespan = form.timespan.data
        version = form.version.data
        fit = form.fit.data
        freq_threshold = form.freq_threshold.data
        d_set = form.d_set.data

        path = os.path.join(THIS_FOLDER, f'results/kmodes_clusters.json')
        if fit: kprototypes_cluster(engine,path = path, d_set=d_set,
                    k=k,timespan=timespan,freq_threshold=freq_threshold)

        try:
            with open(path,"r") as file: 
                clusters = json.load(file)
                # TODO: Why is data not len() == k after reading but is len() == 5
                # during saving.
                #data=clusters[f'k{k}'][0],
                data=clusters[f'k{k}'],
                data = data[0]
                frequencies=clusters[f'k{k}_counts']

                if len(data) != k: raise KeyError # Related to the above comment.
        except (FileNotFoundError, KeyError) as e:
            flash("Data not found, please train the model")
            return redirect( url_for('data_analysis.index', code=301))

        #G = nx.cubical_graph()
        G = nx.Graph()

        fig = plt.figure(figsize=(10,10))

        if version == 1:
            return create_graph(G=G,fig=fig,
                    clusters=data,
                    frequencies=frequencies)
        elif version == 2:
            return create_graph_v2(G=G,fig=fig,
                    clusters=data,
                    frequencies=frequencies)

    elif target == 'kmodes_elbow':
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, f'results/{target}.json')

        # TODO: Add retrain flag to decide whether to serve and old or newly trained img.
        form = kmodes_elbow_form
        timespans = form.timespan.data
        freq_threshold = form.freq_threshold.data
        fit = form.fit.data
        init = form.init.data
        fig_count = len(timespans)

        if fig_count <= 2:
            n_row = fig_count
            fig, axs = plt.subplots(n_row,figsize=(12,8))
            #fig, axs = plt.subplots(1,n_row)
            fig.suptitle("Cost curves")

            if fig_count == 1:
                axs = [axs]
        elif fig_count % 2 == 0:
            n_row = 2
            n_col = int(fig_count/n_row)
            fig, axs = plt.subplots(n_row, n_col,figsize=(12,8))
            axs = axs.flatten()
        elif fig_count == 3:
            n_row = fig_count
            fig, axs = plt.subplots(n_row, figsize=(12,8))
            axs = axs.flatten()

        for ax, timespan in zip(axs, timespans):
            key=f'kmodes_{init}_elbow_dT_{timespan}'
            if fit:
                kmodes_elbow_cost(engine,fig=fig,axis=ax, path=path, 
                        key=key, init=init,timespan=timespan, d_set='binary',
                        freq_threshold=freq_threshold)
            try:
                # TODO: Is it bad to open and close the file within the loop? Performance?
                with open(path,"r") as file: 
                    costs = json.load(file)
            
                x = list(costs[key].keys())
                y = list(costs[key].values())
                ax.plot(x,y)
                ax.set_title( f"Days: {timespan}, Init: {init}",fontsize='small')
                ax.set_xlabel('K'); ax.set_ylabel('Cost')
                #return redirect( url_for('data_analysis.index', code=301))

            except (FileNotFoundError, KeyError) as e:
                flash("Data not found, please train the model")
                return redirect( url_for('data_analysis.index', code=301))

        return plot_img(fig)
    elif target == 'tag_network':
        form = Tag_network_form()
        version = form.version.data
        timespan = form.timespan.data
        freq_threshold = form.freq_threshold.data

        fig = plt.figure(figsize=(14,14))
        return plot_tag_graph(engine, fig, 
                version=version, timespan=timespan, freq_threshold=freq_threshold,
                )
        #plot_tag_graph(engine, fig, 
        #        version=version, timespan=timespan, freq_threshold=freq_threshold,
        #        )

    return redirect(url_for("data_analysis.index"))

#@bp.route("/data/kmodes_data", methods=["GET"])
#def kmodes_data():
#    """ Endpoint for data queries for kmodes """
#
#    path = os.getcwd() +'/daily/data_analysis/kmodes_clusters.json'
#    with open(path,"r") as file: 
#        clusters = json.load(file)
#    return jsonify(clusters)

@bp.route("/data", methods=["GET", "POST"])
def data():
    """ Runs models for numerical output, no plots """
    engine = db.get_engine()
    args = request.args
    summary = None

    target = request.args.get('target')
    if target == 'nbayes':
        re_train = args.get('re_train')
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path_summary = os.path.join(THIS_FOLDER, f'results/{target}_summary.json')
        path_model = os.path.join(THIS_FOLDER, f'results/{target}_model.json')
        sk_naive_bayes_multinomial(engine, 
            path_summary=path_summary, path_model=path_model, fit=re_train)
        #naive_bayes(engine)
        with open(path_summary,"r") as file: 
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
    kmodes_elbow_form = Kmodes_elbow_form()
    session['summary'] = summary

    return redirect( url_for('data_analysis.index', code=200))
                
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

from daily.data_analysis.gnn import get_data
@bp.route("/data/pack", methods=["GET", "POST"])
def data_pack():
    target = request.args.get('target')
    engine = db.engine
    get_data.get_event_tag_data(engine)
    return redirect( url_for('data_analysis.index', code=200))
