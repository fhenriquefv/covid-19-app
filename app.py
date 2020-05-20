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
import pathlib
import StaticPlots as sPlots
import DinamicPlots as dPlots
from flask_json import FlaskJSON, JsonError, json_response, as_json
import sys
from sklearn.externals import joblib

app = Flask(__name__)
json = FlaskJSON(app)
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

@app.route('/teste/<string:classe>/<string:tipo>', methods=['GET'])
def teste(classe, tipo):
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
    pastaClasse = ''
    if(classe == 'dinamic'):
        pastaClasse = '__custom'
    elif(classe == 'static'):
        pastaClasse = '__fixed'  

    diretorio = pathlib.Path('__temp/'+pastaClasse)
    
    arquivos = diretorio.glob('**/*.png')

    fileArray = []
    for file in arquivos:
        fullpath = str(file)
        fullpath.encode()
        *caminho, pasta, arquivo = fullpath.split('/')
        nome, extensao = arquivo.split('.')
        if(nome.startswith(tipo)):
            dicionario = get_file_type(nome, pasta)
            dicionario['caminho'] = fullpath
            fileArray.append(dicionario)
        

    #res = staticPlots.totalBarState(True, 'Population', 'totalBarEstado')
    '''res = BASEURL+staticPlots.totalBarState(True, 'Population', 'totalBarEstado')+' '
    res += BASEURL+staticPlots.totalBarCity('SP', True, 'Population', 'totalBarCidade')+' '
    res += BASEURL+staticPlots.PieInfected('SP', 'city', 'pieInfectedSP')+' '
    res += BASEURL+staticPlots.PieDeaths('Campinas-SP', 'state', 'pieDeathsCampinas')+' '
    res += BASEURL+staticPlots.PieRegion(True)+' ' '''
    return json_response(files=fileArray)

def get_file_type(filename, directory):
    dictionary = {'Nome': filename}
    letras = list(directory)
    tipo = ''
    if(letras[2] == 'p'):
        tipo = 'pizza'
    elif(letras[2] == 'ts'):
        tipo = 'temporal'
    elif(letras[2] == 't'):
        tipo = 'barra'
    elif(letras[2] == 'c' or letras[3] == 'c'):
        tipo = 'comparativo'
    elif(letras[2] == 'h'):
        tipo = 'mapa de calor'
    dictionary['Tipo'] = tipo

    mortes = ''
    if(letras[3] == 'i' or letras[4] == 'i'):
        mortes = 'infectados'
    elif(letras[3] == 'd' or letras[4] == 'd'):
        mortes = 'mortes'
    dictionary['Mortes'] = mortes

    alcance = ''
    if(letras[4] == 's' or letras[5] == 's'):
        alcance = 'estado'
    elif(letras[4] == 'c' or letras[5] == 'c'):
        alcance = 'cidade'
    else:
        alcance = 'regiao'
    dictionary['Alcance'] = alcance

    return dictionary    

    
    '''
    if(letras[1] == 'i' or letras[2] == 'i'):
        mortes = 'infectados'
    elif(letras[1] == 'd' or letras[2] == 'd'):
        mortes = 'mortes'
    '''
    



def file_exists(preffix, suffix):
    diretorio = pathlib.Path('__temp')
    
    arquivos = diretorio.glob('**/*.png')

    filepaths = []
    for file in arquivos:
        filepaths.append(str(file))
    
    nomes = []

    for fullpath in filepaths:
        fullpath.encode()
        *caminho, arquivo = fullpath.split('/')
        nome, extensao = arquivo.split('.')
        nomes.append(nome)
    
    
    matches = []


    for nome in nomes:
        if(nome.endswith(suffix) and nome.startswith(preffix)):
            matches.append(nome)    
    
    return len(matches) > 0

@app.route('/temporalseries', methods=['POST'])
def gerar_temporal_series():

    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()
    
    _relation['ratio'] = pd.Series(params['taxa'])
    _relation['gtype'] = pd.Series(params['tipo'])
    _relation['gvalue'] = pd.Series(params['valor'])
    
    ratio = _relation['ratio'].values[0]
    gvalue = _relation['gvalue'].values[0]
    gtype = _relation['gtype'].values[0]
    prefixo = ''
    if(gtype == 'city'):
        prefixo = 'tsc_'
    else:
        prefixo = 'tss_'
    
    timestamp = datetime.datetime.now().timestamp()
    hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = hash_object.hexdigest()

    hash_value += gvalue
    sufixo = gvalue

    if(not file_exists(prefixo, sufixo)):
        path = BASEURL+staticPlots.TemporalSeries(gvalue, gtype, ratio, hash_value)
    else:
        path = 'ERRO'
    return path


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


    taxa = _relation['ratio'].values[0]
    mortes = _relation['deaths'].values[0]

    #_relation["ratio"] = pd.Series(params["taxa"])
    if(method == 'city'):
        _relation["state"] = pd.Series(params["estado"])
        estado = _relation['state'].values[0]
        prefixo = ''
        if(mortes):
            prefixo = 'tdbc_'
        else:
            prefixo = 'tibc_'

        sufixo = str(estado)
        if(taxa == 'Population'):
            sufixo += '_b100k'
        else:
            sufixo += '_ba'

        if(not file_exists(prefixo, sufixo)):
            path = BASEURL+staticPlots.totalBarCity(_relation['state'].values[0], mortes, taxa, hash_value+_relation['state'].values[0])
        else:
            path = 'ERRO'
    else:
        prefixo = ''
        if(mortes):
            prefixo = 'tdbs_'
        else:
            prefixo = 'tibs_'

        sufixo = ''
        if(taxa == 'Population'):
            sufixo += '_b100k'
        else:
            sufixo += '_ba'

        if(not file_exists(prefixo, sufixo)):
            path = BASEURL+staticPlots.totalBarState(_relation['deaths'].values[0], _relation['ratio'].values[0], hash_value)
        else:
            path = 'ERRO'
    return path

    

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
        prefixo = ''
        if(mortes):
            prefixo = 'pdbr'
        else:
            prefixo = 'pibr'

        if(not file_exists(prefixo, '')):
            path = BASEURL+staticPlots.PieRegion(mortes)
        else:
            path = 'ERRO'
    else:
        sufixo = ''
        if(coverage == 'city'):
            _relation['gvalue'] = pd.Series(params['valor'])
            gvalue = _relation['gvalue'].values[0]
            hash_value += gvalue
            sufixo = gvalue
        else:
            gvalue = None
        if(mortes):
            prefixo = ''
            if(coverage == 'state'):
                prefixo = 'pdbs'
            else:
                prefixo = 'pdbc_'
            if(not file_exists(prefixo, sufixo)):
                path = BASEURL+staticPlots.PieDeaths(gvalue,coverage,hash_value)
            else:
                path = 'ERRO'
        else:
            prefixo = ''
            if(coverage == 'state'):
                prefixo = 'pibs_'
            else:
                prefixo = 'pibc_'
            if(not file_exists(prefixo, sufixo)):
                path = BASEURL+staticPlots.PieInfected(gvalue,coverage,hash_value)
            else:
                path = 'ERRO'
    
    return path
    
    

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
    sufixo = ''
    for state in states:
        if(i == len(states) - 1):
            sufixo += state
        else:
            sufixo += state+'X'
        i += 1
    
    hash_value += sufixo

    if method == 'Multiple':
        if(deaths):
            prefixo = 'mcdbs_'
        else:
            prefixo = 'mcibs_'
        if(not file_exists(prefixo, sufixo)):
            path = BASEURL+dinamicPlots.ComparisonMultipleStatesBar(states,deaths,hash_value)
        else:
            path = 'ERRO'
    else:
        if(deaths):
            prefixo = 'cdbs_'
        else:
            prefixo = 'cibs_'
        if(not file_exists(prefixo, sufixo)):
            path = BASEURL+dinamicPlots.ComparisonStateBar(states[0],states[1],deaths,hash_value)
        else:
            path = 'ERRO'

    
    return path

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
    sufixo = ''
    for city in cities:
        if(i == len(cities) -1):
            sufixo += city
        else:
            sufixo += city+'X'
        i += 1
    hash_value += sufixo

    path = ''
    prefixo = ''
    if method == 'Multiple':
        if(deaths):
            prefixo = 'mcdbc_'
        else:
            prefixo = 'mcibc_'
        if(not file_exists(prefixo, sufixo)):
            path = BASEURL+dinamicPlots.ComparisonMultipleCitiesBar(cities, deaths, hash_value)
        else:
            path = 'ERRO'
    else:
        if(deaths):
            prefixo = 'cdbc_'
        else:
            prefixo = 'cibc_'
        if(not file_exists(prefixo, sufixo)):
            path = BASEURL+dinamicPlots.ComparisonStateBar(states[0],states[1],deaths,hash_value)
        else:
            path = 'ERRO'
        #path = dinamicPlots.ComparisonCityBar(cities[0], cities[1], deaths, hash_value)
        #return 'Comparison Two Cities: '+strMortes+' '+strCidades
    return path


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
    sufixo = ''
    for state in states_list:
        if(i == len(states_list) -1):
            sufixo += state
        else:
            sufixo += state+'X'
        i += 1

    hash_value += sufixo
    if(deaths):
        prefixo = 'hdbs_'
    else:
        prefixo = 'hibs_'
    if(not file_exists(prefixo, sufixo)):
        path = BASEURL+dinamicPlots.HeatmapState(states_list,deaths,hash_value)
    else:
        path = 'ERRO'
    return path

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
    sufixo = ''
    for city in cities_list:
        if(i == len(cities_list) -1):
            sufixo += city
        else:
            sufixo += city+'X'
        i += 1

    hash_value += sufixo

    
    if(deaths):
        prefixo = 'hdbc_'
    else:
        prefixo = 'hibc_'

    if(not file_exists(prefixo, sufixo)):
        path = BASEURL+dinamicPlots.HeatmapCity(cities_list,deaths,hash_value)
    else:
        path = 'ERRO'
    return path



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
