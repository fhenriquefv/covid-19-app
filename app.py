# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, send_from_directory

import json
import logging
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import BRKGA as brkga
import DataLoad as dl
import StaticPlots as sPlots
import DinamicPlots as dPlots
from sklearn.externals import joblib

app = Flask(__name__)


@app.route('/brkga', methods=['POST'])
def run_brkga():
	
    data = dl.DataLoad()
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()
    _relation['City'] = pd.Series(params["City"]["Value"])
    _relation["Cover"] = pd.Series(params["Cover"]["Value"])
    _relation["Cost"] = pd.Series(params["Cost"]["Value"])
    
    facilities_cost = []
    facilities_cover = []

    
    for i in _relation["Cost"].values:
        facilities_cost.append(i.copy())

    for i in _relation["Cover"].values:
        facilities_cover.append(i.copy())


# In[139]:


    for i in range(0,params["N"]["Value"]):
        location = _relation["City"][i]
        state = location.split('-')[0]
        city_id = int(location.split('-')[1])
    
        redundance = _relation["City"].value_counts()[_relation["City"].value_counts().index == location][location]
        density = data.DemographicData[state].loc[city_id]["Density"]
    
        facilities_cover[i]= facilities_cover[i]/density*redundance
        facilities_cost[i] = facilities_cost[i]*redundance/density

    Heuristic = brkga.BRKGA(facilities_cover, facilities_cost,
                            params["M"]["Value"], params["P"]["Value"],
                            params["Elite"]["Value"], params["Mutant"]["Value"],
                            params["K"]["Value"], params["Type"]["Value"])


    Heuristic = brkga.BRKGA(facilities_cover,facilities_cost,
                        params["M"]["Value"],params["P"]["Value"],
                        params["Elite"]["Value"],params["Mutant"]["Value"],
                        params["K"]["Value"],params["Type"]["Value"])

    solutions, facilities = Heuristic.Solve()

    best_solutions = Heuristic.getObjectiveEvolution()

    Fig = plt.figure(figsize=(5, 5),)
    plt.plot(range(0, params["K"]["Value"]),
             pd.Series(best_solutions), figure=Fig)
    plt.xlabel("Iterations")
    plt.ylabel("Obj. Value (1/1000)")
    plt.title("Evolution of The Objective Value")
    Fig.savefig("Exit/Evolution_"+params["S"]["Value"]+".png")

    exit_data = pd.DataFrame(facilities)
    exit_data["obj_value"] = solutions
    exit_data["final_cost"] = 0
    exit_data["final_cover"] = 0

    for i in exit_data.index:
        cover = 0
        cost = 0
        #
        for j in exit_data.loc[i][:params["M"]["Value"]]:
            cost += _relation["Cost"][j]
            cover += _relation["Cover"][j]

        exit_data.loc[i, "final_cost"] = cost
        exit_data.loc[i, "final_cover"] = cover

    exit_data = exit_data.sort_values("obj_value", ascending=False)
    return exit_data.to_json()


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(APP_ROOT, 'classifier.pkl')

PORT = 5000

logging.basicConfig(filename='movie_classifier.log', level=logging.DEBUG)
model = joblib.load(MODEL)
label = {0: 'negative', 1: 'positive'}


#@app.route('/brkga', methods=['POST'])
#def brkga():
#    data = request.get_json()
#    return jsonify(data)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route('/__temp/<path:path>')
def send_js(path):
    return send_from_directory('__temp', path)

@app.route('/')
def home():
    return 'Funcionou!.'

@app.route('/teste', methods=['POST'])
def teste():
    data = dl.DataLoad()
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()
    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["ratio"] = pd.Series(params["taxa"])
    _relation["select"] = pd.Series(params["selecionado"]["Value"])

    staticPlots = sPlots.StaticPlots(data)
    dinamicPlots = dPlots.DinamicPlots(data)
    #staticPlots.PieDeaths(_relation['select'].values[0],'state','pieGraphSP')
    #dinamicPlots.ComparisonStateBar(_relation['select'].values[0],_relation['select'].values[1],_relation['deaths'].values[0],'comparisonStateBar')
    dinamicPlots.ComparisonStateBar('RJ','SP',_relation['deaths'].values[0],'comparison')
    
    
    return 'Funcionou'

    

def predict(model, text):
    return label[model.predict([text])[0]]


@app.route('/review', methods=['GET'])
def extract():
    """Return the movie review sentiment score.

    Returns a JSON object :
    {
         "sentiment": "positive"
    }
    """
    if request.method == 'GET':
        description = request.args.get('text', '')

        result = {
            'sentiment': predict(model, description)
        }
        return json.dumps(result)


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=PORT)
