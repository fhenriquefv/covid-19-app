# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin

import json
import logging
import os

import hashlib
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import BRKGA as brkga
import DataLoad as dl
import StaticPlots as sPlots
import DinamicPlots as dPlots
from sklearn.externals import joblib

app = Flask(__name__)
#CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'


data = dl.DataLoad()
staticPlots = sPlots.StaticPlots(data)
dinamicPlots = dPlots.DinamicPlots(data)
BASEURL = 'https://covid-19-flask-api.herokuapp.com/'

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

@app.route('/__temp/<path:path>')
def send_js(path):
    return send_from_directory('__temp', path)

@app.route('/')
def home():
    return 'Funcionou!'

@app.route('/teste', methods=['POST'])
def teste():
    #data = dl.DataLoad()
    #params = pd.DataFrame(request.get_json()) 

    #_relation = pd.DataFrame()

    '''
    _relation['type'] = pd.Series(params['tipo'])
    _relation['param'] = pd.Series(params['parametro'])
    _relation['deaths'] = pd.Series(params["mortes"])
    #_relation["ratio"] = pd.Series(params["taxa"])
    _relation["select"] = pd.Series(params["selecionado"])
    '''

    #res = staticPlots.totalBarState(True, 'Population', 'totalBarEstado')
    res = BASEURL+staticPlots.totalBarState(True, 'Population', 'totalBarEstado')+' '
    res += BASEURL+staticPlots.totalBarCity('SP', True, 'Population', 'totalBarCidade')+' '
    res += BASEURL+staticPlots.PieInfected('SP', 'city', 'pieInfectedSP')+' '
    res += BASEURL+staticPlots.PieDeaths('Campinas-SP', 'state', 'pieDeathsCampinas')+' '
    res += BASEURL+staticPlots.PieRegion(True)+' '
    return res

@app.route('/totalbar/<string:method>', methods=['POST'])
def gerar_grafico_barras(method):
    #data = dl.DataLoad()
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()

    
    _relation['ratio'] = pd.Series(params['taxa'])
    _relation['deaths'] = pd.Series(params["mortes"])

    timestamp = datetime.datetime.now().timestamp()
    hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = hash_object.hexdigest()
    #_relation["ratio"] = pd.Series(params["taxa"])
    if(method == 'city'):
        _relation["state"] = pd.Series(params["estado"])
        path = staticPlots.totalBarCity(_relation['state'].values[0], _relation['deaths'].values[0], _relation['ratio'].values[0], hash_value)
    else:
        path = staticPlots.totalBarState(_relation['deaths'].values[0], _relation['ratio'].values[0], hash_value)
    return BASEURL+path

    

@app.route('/pie/<string:coverage>', methods=['POST'])
def gerar_grafico_pizza(coverage):
    #data = dl.DataLoad()
    params = pd.DataFrame(request.get_json()) 

    timestamp = datetime.datetime.now().timestamp()
    hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = hash_object.hexdigest()

    _relation = pd.DataFrame()
    _relation['deaths'] = pd.Series(params["mortes"])
    mortes = _relation['deaths'].values[0]

    if(coverage == 'region'):
        path = staticPlots.PieRegion(mortes)
    else:
        if(coverage == 'city'):
            _relation['gvalue'] = pd.Series(params['valor'])
            gvalue = _relation['gvalue'].values[0]
        else:
            gvalue = None
        if(mortes):
            path = staticPlots.PieDeaths(gvalue,coverage,hash_value)
        else:
            path = staticPlots.PieInfected(gvalue,coverage,hash_value)
    
    return BASEURL+path
    
    

@app.route('/comparison/states/<string:method>', methods=['POST'])
def comparar_estados(method):
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()

    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["estados"] = pd.Series(params["selecionado"])
    
    deaths = _relation['deaths'].values[0]
    states = _relation['estados'].Value

    timestamp = datetime.datetime.now().timestamp()
    hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = hash_object.hexdigest()

    i = 0
    for state in states:
        if(i == len(states) -1)
            hash_value += states
        else
            hash_value += states+'X'
        i += 1

    if method == 'Multiple':
        path = dinamicPlots.ComparisonMultipleStatesBar(states,deaths,hash_value)
    else:
        path = dinamicPlots.ComparisonStateBar(states[0],states[1],deaths,hash_value)

    
    return BASEURL+path

@app.route('/comparison/cities/<string:method>', methods=['POST'])
def comparar_cidades(method):
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()

    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["cidades"] = pd.Series(params["selecionado"])
    
    #Tratar os dados
    deaths = _relation['deaths'].values[0]
    cities = _relation['cidades'].Value
    timestamp = datetime.datetime.now().timestamp()
    hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = hash_object.hexdigest()

    i = 0
    for city in cities:
        if(i == len(cities) -1)
            hash_value += city
        else
            hash_value += city+'X'
        i += 1

    path = ''
    if method == 'Multiple':
        path = dinamicPlots.ComparisonMultipleCitiesBar(cities, deaths, hash_value)
    else:
        path = dinamicPlots.ComparisonCityBar(cities[0], cities[1], deaths, hash_value)
        #return 'Comparison Two Cities: '+strMortes+' '+strCidades
    return BASEURL+path


@app.route('/heatmap/states', methods=['POST'])
def mapear_estados():
    #Coleta de dados
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()
    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["estados"] = pd.Series(params["selecionado"])

    #Estados e mortes
    states_list = _relation['estados'].Value
    deaths = _relation['deaths'].values[0]

    #Hashvaluee
    timestamp = datetime.datetime.now().timestamp()
    hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = hash_object.hexdigest()

    
    i = 0
    for city in cities:
        if(i == len(cities) -1)
            hash_value += city
        else
            hash_value += city+'X'
        i += 1

    path = dinamicPlots.HeatmapState(states_list,deaths,hash_value)
    return BASEURL+path

@app.route('/heatmap/cities', methods=['POST'])
def mapear_cidades():
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()

    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["cidades"] = pd.Series(params["selecionado"])

    #Estados e mortes
    cities_list = _relation['cidades'].Value
    deaths = _relation['deaths'].values[0]

    timestamp = datetime.datetime.now().timestamp()
    hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = hash_object.hexdigest()

    i = 0
    for city in cities:
        if(i == len(cities) -1)
            hash_value += city
        else
            hash_value += city+'X'
        i += 1


    path = dinamicPlots.HeatmapCity(cities_list,deaths,hash_value)
    return BASEURL+path



@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


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
