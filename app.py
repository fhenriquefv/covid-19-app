# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request

import json
import logging
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import BRKGA as brkga

from sklearn.externals import joblib

app = Flask(__name__)


@app.route('/brkga', methods=['POST'])
def run_brkga():
    dem = pd.read_csv("Instances/RJDemographicData.csv", index_col=0)
    dem = dem.reindex(index=sorted(dem.index))

    prox = pd.read_csv(
        "Instances/Neighboorhood/RJNeighboorhood.csv", dtype=int, index_col=0)
    prox.columns = prox.columns.to_numpy(int)
    prox = prox.reindex(index=sorted(prox.index), columns=sorted(prox.columns))

    params = pd.DataFrame(request.get_json()) 
    #pd.read_json(request.get_json(), dtype={
    #                      "N": int, "M": int, "P": int, "Elite": int, "Mutant": int, "K": int, "S": str, "Type": bool})

    _relation = pd.read_csv("Input/Facilities.csv", index_col=0)

    facilities_cost = []
    facilities_cover = []

    for i in _relation["Cost"].values:
        facilities_cost.append(i.copy())

    for i in _relation["Cover"].values:
        facilities_cover.append(i.copy())

    for i in range(0, params["N"]["Value"]):
        facilities_cover[i] = facilities_cover[i] / \
            dem["Urban Density (People/Km2)"][i] * \
            _relation["City"].value_counts()[_relation["City"][i]]
        facilities_cost[i] = facilities_cost[i]*_relation["City"].value_counts(
        )[_relation["City"][i]]/dem["Urban Density (People/Km2)"][i]

    Heuristic = brkga.BRKGA(facilities_cover, facilities_cost,
                            params["M"]["Value"], params["P"]["Value"],
                            params["Elite"]["Value"], params["Mutant"]["Value"],
                            params["K"]["Value"], params["Type"]["Value"])

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


@app.route('/')
def home():
    return 'It works.'


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
