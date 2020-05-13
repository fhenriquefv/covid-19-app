# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

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
CORS(app)

data = dl.DataLoad()
staticPlots = sPlots.StaticPlots(data)
dinamicPlots = dPlots.DinamicPlots(data)

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
    return 'Funcionou!'

@app.route('/teste', methods=['POST'])
def teste():
    #data = dl.DataLoad()
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()

    _relation['type'] = pd.Series(params['tipo'])
    _relation['param'] = pd.Series(params['parametro'])
    _relation['deaths'] = pd.Series(params["mortes"])
    #_relation["ratio"] = pd.Series(params["taxa"])
    _relation["select"] = pd.Series(params["selecionado"])

    
    hash_value = ''
    hash_value += str(_relation['type'].values[0])
    hash_value += str(_relation['param'].values[0])
    if _relation['deaths'].values[0]: 
        hash_value += 'deaths'
    else:
        hash_value += 'infected'

    #return str(_relation['select'].Value)
    res = dinamicPlots.ComparisonMultipleCitiesBar(_relation['select'].Value, _relation['deaths'].values[0], hash_value)
    return res
    '''
    #staticPlots.PieDeaths(_relation['select'].values[0],'state','pieGraphSP')
    #dinamicPlots.ComparisonStateBar(str(_relation['select'].Value[0]),str(_relation['select'].Value[1]),_relation['deaths'].values[0],'comparisonStateBar2')
    #dinamicPlots.ComparisonStateBar('RJ','SP',_relation['deaths'].values[0],'comparison')    
    return str(params)
    '''

@app.route('/comparison/states/<string:method>', methods=['POST'])
def comparar_estados(method):
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()

    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["estados"] = pd.Series(params["selecionado"])
    
    strMortes = str(_relation['deaths'].values[0])
    strEstados = str(_relation['estados'].Value)
    if method == 'Multiple':
        return 'Comparison Multiple States: '+strMortes+' '+strEstados
    else:
        return 'Comparison Two States: '+strMortes+' '+strEstados

@app.route('/comparison/cities/<string:method>', methods=['POST'])
def comparar_cidades(method):params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()

    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["cidades"] = pd.Series(params["selecionado"])
    
    strMortes = str(_relation['deaths'].values[0])
    strCidades = str(_relation['cidades'].Value)
    if method == 'Multiple':
        return 'Comparison Multiple Cities: '+strMortes+' '+strCidades
    else:
        return 'Comparison Two Cities: '+strMortes+' '+strCidades

@app.route('/heatmap/states', methods=['POST'])
def mapear_estados():
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()

    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["estados"] = pd.Series(params["selecionado"])
    
    strMortes = str(_relation['deaths'].values[0])
    strEstados = str(_relation['estados'].Value)
    if method == 'Multiple':
        return 'HeatMap Multiple States: '+strMortes+' '+strEstados
    else:
        return 'HeatMap Two States: '+strMortes+' '+strEstados

@app.route('/heatmap/cities', methods=['POST'])
def mapear_cidades():
    _relation = pd.DataFrame()

    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["cidades"] = pd.Series(params["selecionado"])
    
    strMortes = str(_relation['deaths'].values[0])
    strCidades = str(_relation['cidades'].Value)
    if method == 'Multiple':
        return 'HeatMap Multiple Cities: '+strMortes+' '+strCidades
    else:
        return 'HeatMap Two Cities: '+strMortes+' '+strCidades

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
