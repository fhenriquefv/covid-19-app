# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin

import json
import logging
import os

import hashlib
from datetime import date
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
from flask_apscheduler import APScheduler
from sklearn.externals import joblib
import csv
#import joblib
app = Flask(__name__)
json = FlaskJSON(app)
#CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'


data = dl.DataLoad()
staticPlots = sPlots.StaticPlots(data)
dinamicPlots = dPlots.DinamicPlots(data)
BASEURL = 'https://covid-19-flask-api.herokuapp.com/'

scheduler = APScheduler()

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

@app.route("/absolutos/<string:date>/", defaults={'gvalue': None})
@app.route('/absolutos/<string:date>/<string:gvalue>', methods=['GET']) 
def mostrar_dados_gerais(date, gvalue):
    gtype = "state"
    if(gvalue != 'None'):
        gtype = 'city'
    return jsonify(data.DadosAbsolutos(date, gtype, gvalue))

@app.route("/historico/<string:date>/", defaults={'gvalue': None})
@app.route('/historico/<string:date>/<string:gvalue>', methods=['GET'])
def mostrar_historico(date, gvalue):
    gtype = "state"
    if(gvalue != 'None'):
        gtype = 'city'
    return jsonify(data.DadosHistoricos(date, gtype, gvalue))


@app.route('/Instances/<path:path>')
def mostrar_csv(path):
    return send_from_directory('Instances', path)

@app.route('/__temp/<path:path>')
def mostrar_graficos(path):
    return send_from_directory('__temp', path)

@app.route('/', methods=['GET'])
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
        if(tipo.startswith('c') or tipo.startswith('mc')):
            if(nome.startswith('c') or nome.startswith('mc')):
                dicionario = create_file_dictionary(nome, pasta)
                dicionario['caminho'] = BASEURL+fullpath
                if(not(dicionario['Tipo'] == 'temporal' and tipo == 't')):
                    fileArray.append(dicionario)
        else:
            if(nome.startswith(tipo)):
                dicionario = create_file_dictionary(nome, pasta)
                dicionario['caminho'] = BASEURL+fullpath
                if(not(dicionario['Tipo'] == 'temporal' and tipo == 't')):
                    fileArray.append(dicionario)
        

    #res = staticPlots.totalBarState(True, 'Population', 'totalBarEstado')
    '''res = BASEURL+staticPlots.totalBarState(True, 'Population', 'totalBarEstado')+' '
    res += BASEURL+staticPlots.totalBarCity('SP', True, 'Population', 'totalBarCidade')+' '
    res += BASEURL+staticPlots.PieInfected('SP', 'city', 'pieInfectedSP')+' '
    res += BASEURL+staticPlots.PieDeaths('Campinas-SP', 'state', 'pieDeathsCampinas')+' '
    res += BASEURL+staticPlots.PieRegion(True)+' ' '''
    return jsonify({'Filenames': fileArray})

def find(array, element):
    found = False
    for item in array:
        if(item == element):
            found = True
    return found 

def create_file_dictionary(filename, directory):
    dictionary = {'Nome': filename, 'AtualizadoEm': find_file_date(filename)}
    letras = list(directory)
    tipo = ''
    if(letras[2] == 'p'):
        tipo = 'pizza'
    elif(letras[2] == 't' and letras[3] == 's'):
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
    else:
        antesData, posData = filename.split('<')
        prefixo = list(antesData)
        tipo, tempo, *resto = antesData.split('_')
        print(tempo)
        if(tempo == 'total'):
            dictionary['Tempo'] = 'acumulado'
        else:
            dictionary['Tempo'] = 'diário'

        #find(prefixo, 'i')
        
        if(find(prefixo, 'i')):
            mortes = 'infectados'
        elif(find(prefixo, 'd')):
            mortes = 'mortes'

    dictionary['Mortes'] = mortes

    alcance = ''
    if(directory.endswith('s')):
        alcance = 'estado'
    elif(directory.endswith('c')):
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
    
def find_file_date(filename):
    prefixo, dataSufixo = filename.split('<')
    data, sufixo = dataSufixo.split('>')
    return data


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
    
    if(len(matches) > 0):
        return False
    else:
        return matches 

@app.route('/temporalseries', methods=['POST'])
def gerar_temporal_series():

    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()
    
    _relation['ratio'] = pd.Series(params['taxa'])
    _relation['gtype'] = pd.Series(params['tipo'])
    _relation['gvalue'] = pd.Series(params['valor'])
    _relation['kind'] = pd.Series(params['kind'])
    _relation['time'] = pd.Series(params['time'])
    
    ratio = _relation['ratio'].values[0]
    gvalue = _relation['gvalue'].values[0]
    gtype = _relation['gtype'].values[0]
    kind = _relation['kind'].values[0]
    time = _relation['time'].values[0]
    prefixo = ''
    pasta = '__'
    fullpath = '__temp/__fixed/'
    if(gtype == 'city'):
        prefixo = 'tsc_'
        pasta += 'tsc'
    else:
        prefixo = 'tss_'
        pasta += 'tss'

    if(time == False):
        prefixo += 'total_'
    else:
        prefixo += 'day_'
    
    if(kind == 'infected'):
        prefixo += 'i_'
    else:
        prefixo += 'd_'


    fullpath += pasta+'/'
    
    timestamp = date.today()
    #hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = '<'+str(timestamp)+'>'

    hash_value += gvalue
    sufixo = gvalue

    dicionario = {}
    status = 200
    repetidos = file_exists(prefixo, sufixo)
    if(not repetidos):
        path = staticPlots.TemporalSeries(gvalue, gtype, time,ratio, kind, hash_value)
        fullpath = str(path)
        fullpath.encode()
        *caminho, pasta, arquivo = fullpath.split('/')
        *resto, nome, extensao = arquivo.split('.')
        dicionario = create_file_dictionary(nome, pasta)
    else:
        existente = repetidos[0]
        last_update = find_file_date(existente)
        if(timestamp == last_update):
            dicionario = create_file_dictionary(existente, pasta)
            fullpath += existente+'.png'
        else:
            path = staticPlots.TemporalSeries(gvalue, gtype, time,ratio, kind, hash_value)
            fullpath = str(path)
            fullpath.encode()
            *caminho, pasta, arquivo = fullpath.split('/')
            nome, extensao = arquivo.split('.')
            dicionario = create_file_dictionary(nome, pasta)
    dicionario['caminho'] = BASEURL+fullpath
    dicionario['selecionados'] = sufixo
    return jsonify(dicionario), status


@app.route('/totalbar/<string:method>', methods=['POST'])
def gerar_grafico_barras(method):
    #data = dl.DataLoad()
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()
    
    _relation['ratio'] = pd.Series(params['taxa'])
    _relation['deaths'] = pd.Series(params["mortes"])

    timestamp = date.today()
    #hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = '<'+str(timestamp)+'>'

    taxa = _relation['ratio'].values[0]
    if(taxa == ''):
        taxa = None
        print('DANONE')
    mortes = _relation['deaths'].values[0]
    sufixo = ''
    dicionario = {}
    status = 200
    #_relation["ratio"] = pd.Series(params["taxa"])
    if(method == 'city'):
        _relation["state"] = pd.Series(params["estado"])
        estado = _relation['state'].values[0]
        prefixo = ''
        fullpath = '__temp/__fixed'
        pasta = '__'
        if(mortes):
            prefixo = 'tdbc_'
            pasta += 'tdbc'
        else:
            prefixo = 'tibc_'
            pasta += 'tibc'

        fullpath += pasta+'/'
        sufixo = str(estado)
        if(taxa == 'Population'):
            sufixo += '_b100k'
        else:
            sufixo += '_ba'

        repetidos = file_exists(prefixo, sufixo)
        if(not repetidos):
            path = staticPlots.totalBarCity(_relation['state'].values[0], mortes, taxa, hash_value+_relation['state'].values[0])
            fullpath = str(path)
            fullpath.encode()
            *caminho, pasta, arquivo = fullpath.split('/')
            nome, extensao = arquivo.split('.')
            dicionario = create_file_dictionary(nome, pasta)
        else:
            existente = repetidos[0]
            last_update = find_file_date(existente)
            if(timestamp == last_update):
                dicionario = create_file_dictionary(existente, pasta)
                fullpath += existente+'.png'
            else:
                path = staticPlots.totalBarCity(_relation['state'].values[0], mortes, taxa, hash_value+_relation['state'].values[0])
                fullpath = str(path)
                fullpath.encode()
                *caminho, pasta, arquivo = fullpath.split('/')
                nome, extensao = arquivo.split('.')
                dicionario = create_file_dictionary(nome, pasta)

    else:
        prefixo = ''
        fullpath = '__temp/__fixed'
        pasta = '__'
        if(mortes):
            prefixo = 'tdbs_'
            pasta += 'tdbs'
        else:
            prefixo = 'tibs_'
            pasta += 'tibs'
        
        fullpath += pasta+'/'

        
        if(taxa == 'Population'):
            sufixo += '_b100k'
        else:
            sufixo += '_ba'

        repetidos = file_exists(prefixo, sufixo)
        if(not repetidos):
            path = staticPlots.totalBarState(_relation['deaths'].values[0],taxa, hash_value)
            fullpath = str(path)
            fullpath.encode()
            *caminho, pasta, arquivo = fullpath.split('/')
            nome, extensao = arquivo.split('.')
            dicionario = create_file_dictionary(nome, pasta)
        else:
            existente = repetidos[0]
            last_update = find_file_date(existente)
            if(timestamp == last_update):
                dicionario = create_file_dictionary(existente, pasta)
                fullpath += existente+'.png'
            else:
                path = staticPlots.totalBarCity(_relation['state'].values[0], mortes, taxa, hash_value+_relation['state'].values[0])
                fullpath = str(path)
                fullpath.encode()
                *caminho, pasta, arquivo = fullpath.split('/')
                nome, extensao = arquivo.split('.')
                dicionario = create_file_dictionary(nome, pasta)
    dicionario['caminho'] = BASEURL+fullpath
    dicionario['selecionados'] = sufixo 
    return jsonify(dicionario), status

    

@app.route('/pie/<string:coverage>', methods=['POST'])
def gerar_grafico_pizza(coverage):
    #data = dl.DataLoad()
    params = pd.DataFrame(request.get_json()) 

    timestamp = date.today()
    #hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = '<'+str(timestamp)+'>'

    _relation = pd.DataFrame()
    _relation['deaths'] = pd.Series(params["mortes"])
    mortes = _relation['deaths'].values[0]

    dicionario = {}
    status = 200
    sufixo = ''

    pasta = '__'
    fullpath = '__temp/__fixed/'
    if(coverage == 'region'):
        prefixo = ''
        if(mortes):
            prefixo = 'pdbr_'
            pasta += 'pdbr'
        else:
            prefixo = 'pibr_'
            pasta += 'pibr'
        
        fullpath += pasta+'/'
        
        repetidos = file_exists(prefixo, '')
        if(not repetidos):
            path = staticPlots.PieRegion(mortes, hash_value)
            fullpath = str(path)
            fullpath.encode()
            *caminho, pasta, arquivo = fullpath.split('/')
            nome, extensao = arquivo.split('.')
            dicionario = create_file_dictionary(nome, pasta)
        else:
            existente = repetidos[0]
            last_update = find_file_date(existente)
            if(timestamp == last_update):
                dicionario = create_file_dictionary(existente, pasta)
                fullpath += existente+'.png'
            else:
                path = staticPlots.PieRegion(mortes, hash_value)
                fullpath = str(path)
                fullpath.encode()
                *caminho, pasta, arquivo = fullpath.split('/')
                nome, extensao = arquivo.split('.')
                dicionario = create_file_dictionary(nome, pasta)
    else:
        
        if(coverage == 'city'):
            _relation['gvalue'] = pd.Series(params['valor'])
            gvalue = _relation['gvalue'].values[0]
            hash_value += gvalue
            sufixo = gvalue
        else:
            gvalue = None
        if(mortes):
            prefixo = ''
            pasta = '__'
            fullpath = '__temp/__fixed/'
            if(coverage == 'state'):
                prefixo = 'pdbs_'
                pasta += 'pdbs'
            else:
                prefixo = 'pdbc_'
                pasta += 'pdbc'

            fullpath += pasta+'/'

            repetidos = file_exists(prefixo, sufixo)
            if(not repetidos):
                path = staticPlots.PieDeaths(gvalue,coverage,hash_value)
                fullpath = str(path)
                fullpath.encode()
                *caminho, pasta, arquivo = fullpath.split('/')
                nome, extensao = arquivo.split('.')
                dicionario = create_file_dictionary(nome, pasta)
                dicionario['caminho'] = BASEURL+fullpath
            else:
                existente = repetidos[0]
                last_update = find_file_date(existente)
                if(timestamp == last_update):
                    dicionario = create_file_dictionary(existente, pasta)
                    fullpath += existente+'.png'
                else:
                    path = staticPlots.PieDeaths(gvalue,coverage,hash_value)
                    fullpath = str(path)
                    fullpath.encode()
                    *caminho, pasta, arquivo = fullpath.split('/')
                    nome, extensao = arquivo.split('.')
                    dicionario = create_file_dictionary(nome, pasta)
        else:
            prefixo = ''
            pasta = '__'
            fullpath = '__temp/__fixed/'
            if(coverage == 'state'):
                prefixo = 'pibs_'
                pasta += 'pibs'
            else:
                prefixo = 'pibc_'
                pasta += 'pibc'
            fullpath += pasta+'/'
            repetidos = file_exists(prefixo, sufixo)
            if(not repetidos):
                path = staticPlots.PieInfected(gvalue,coverage,hash_value)
                fullpath = str(path)
                fullpath.encode()
                *caminho, pasta, arquivo = fullpath.split('/')
                nome, extensao = arquivo.split('.')
                dicionario = create_file_dictionary(nome, pasta)
                dicionario['caminho'] = BASEURL+fullpath
            else:
                existente = repetidos[0]
                last_update = find_file_date(existente)
                if(timestamp == last_update):
                    dicionario = create_file_dictionary(existente, pasta)
                    fullpath += existente+'.png'
                else:
                    path = staticPlots.PieInfected(gvalue,coverage,hash_value)
                    fullpath = str(path)
                    fullpath.encode()
                    *caminho, pasta, arquivo = fullpath.split('/')
                    nome, extensao = arquivo.split('.')
                    dicionario = create_file_dictionary(nome, pasta)

    dicionario['caminho'] = BASEURL+fullpath
    dicionario['selecionados'] = sufixo    
    return jsonify(dicionario), status
    
    

@app.route('/comparison/states/<string:method>', methods=['POST'])
def comparar_estados(method):
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()

    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["estados"] = pd.Series(params["selecionado"])
    _relation["time"] = pd.Series(params["time"])
    
    deaths = _relation['deaths'].values[0]
    states = _relation['estados'].Value
    time = _relation["time"].values[0]


    timestamp = date.today()
    #hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = '<'+str(timestamp)+'>'

    i = 0
    sufixo = ''
    for state in states:
        if(i == len(states) - 1):
            sufixo += state
        else:
            sufixo += state+'X'
        i += 1
    
    hash_value += sufixo
    dicionario = {}
    status = 200
    fullpath = '__temp/__custom/'
    pasta = '__'
    if(deaths):
        prefixo = 'mcdbs_'
        pasta += 'mcdbs'
    else:
        prefixo = 'mcibs_'
        pasta += 'mcibs'

    if(time == True):
        prefixo += "t_"

    fullpath += pasta+'/'
    repetidos = file_exists(prefixo, sufixo)
    if(not repetidos):
        path = dinamicPlots.ComparisonMultipleStates(states,deaths,time,hash_value)
        fullpath = str(path)
        fullpath.encode()
        *caminho, pasta, arquivo = fullpath.split('/')
        nome, extensao = arquivo.split('.')
        dicionario = create_file_dictionary(nome, pasta)
        
    else:
        existente = repetidos[0]
        last_update = find_file_date(existente)
        if(timestamp == last_update):
            dicionario = create_file_dictionary(existente, pasta)
            fullpath += existente+'.png'
        else:
            path = dinamicPlots.ComparisonMultipleStates(states,deaths,hash_value)
            fullpath = str(path)
            fullpath.encode()
            *caminho, pasta, arquivo = fullpath.split('/')
            nome, extensao = arquivo.split('.')
            dicionario = create_file_dictionary(nome, pasta)

    dicionario['caminho'] = BASEURL+fullpath
    dicionario['selecionados'] = sufixo
    return jsonify(dicionario), status

@app.route('/comparison/cities/<string:method>', methods=['POST'])
def comparar_cidades(method):
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()

    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["cidades"] = pd.Series(params["selecionado"])
    _relation["time"] = pd.Series(params["time"])
    
    deaths = _relation['deaths'].values[0]
    states = _relation['cidades'].Value
    time = _relation["time"].values[0]


    timestamp = date.today()
    #hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = '<'+str(timestamp)+'>'
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
    dicionario = {}
    status = 200
    fullpath = '__temp/__custom/'
    pasta = '__'
    if(deaths):
        prefixo = 'mcdbc_'
        pasta += 'mcdbc'
    else:
        prefixo = 'mcibc_'
        pasta += 'mcibc'

    if(time == True):
        prefixo += "t_"
    fullpath += pasta+'/'
    repetidos = file_exists(prefixo, sufixo)
    if(not repetidos):
        path = dinamicPlots.ComparisonMultipleCities(cities, deaths, time, hash_value)
        fullpath = str(path)
        fullpath.encode()
        *caminho, pasta, arquivo = fullpath.split('/')
        nome, extensao = arquivo.split('.')
        dicionario = create_file_dictionary(nome, pasta)
    else:
        existente = repetidos[0]
        last_update = find_file_date(existente)
        if(timestamp == last_update):
            dicionario = create_file_dictionary(existente, pasta)
            fullpath += existente+'.png'
        else:
            path = dinamicPlots.ComparisonMultipleCities(cities, deaths, time, hash_value)
            fullpath = str(path)
            fullpath.encode()
            *caminho, pasta, arquivo = fullpath.split('/')
            nome, extensao = arquivo.split('.')
            dicionario = create_file_dictionary(nome, pasta)
    

    dicionario['caminho'] = BASEURL+fullpath
    dicionario['selecionados'] = sufixo
        #path = dinamicPlots.ComparisonCityBar(cities[0], cities[1], deaths, hash_value)
        #return 'Comparison Two Cities: '+strMortes+' '+strCidades
    return jsonify(dicionario), status


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
    timestamp = date.today()
    #hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = '<'+str(timestamp)+'>'

    
    i = 0
    sufixo = ''
    for state in states_list:
        if(i == len(states_list) -1):
            sufixo += state
        else:
            sufixo += state+'X'
        i += 1

    hash_value += sufixo
    fullpath = '__temp/__custom/'
    pasta = '__'
    if(deaths):
        prefixo = 'hdbs_'
        pasta += 'hdbs'
    else:
        prefixo = 'hibs_'
        pasta += 'hibs'
    fullpath += pasta+'/'

    dicionario = {}
    status = 200
    repetidos = file_exists(prefixo, sufixo)
    if(not repetidos):
        path = dinamicPlots.HeatmapState(states_list,deaths,hash_value)
        fullpath = str(path)
        fullpath.encode()
        *caminho, pasta, arquivo = fullpath.split('/')
        nome, extensao = arquivo.split('.')
        dicionario = create_file_dictionary(nome, pasta)
    else:
        existente = repetidos[0]
        last_update = find_file_date(existente)
        if(timestamp == last_update):
            dicionario = create_file_dictionary(existente, pasta)
            fullpath += existente+'.png'
        else:
            path = dinamicPlots.HeatmapState(states_list,deaths,hash_value)
            fullpath = str(path)
            fullpath.encode()
            *caminho, pasta, arquivo = fullpath.split('/')
            nome, extensao = arquivo.split('.')
            dicionario = create_file_dictionary(nome, pasta)
    
    dicionario['caminho'] = BASEURL+fullpath
    dicionario['selecionados'] = sufixo
    return jsonify(dicionario), status

@app.route('/heatmap/cities', methods=['POST'])
def mapear_cidades():
    params = pd.DataFrame(request.get_json()) 

    _relation = pd.DataFrame()

    _relation['deaths'] = pd.Series(params["mortes"])
    _relation["cidades"] = pd.Series(params["selecionado"])

    #Estados e mortes
    cities_list = _relation['cidades'].Value
    deaths = _relation['deaths'].values[0]

    timestamp = date.today()
    #hash_object = hashlib.md5(str(timestamp).encode())
    hash_value = '<'+str(timestamp)+'>'

    i = 0
    sufixo = ''
    for city in cities_list:
        if(i == len(cities_list) -1):
            sufixo += city
        else:
            sufixo += city+'X'
        i += 1

    hash_value += sufixo

    fullpath = '__temp/__custom/'
    pasta = '__'
    if(deaths):
        prefixo = 'hdbc_'
        pasta += 'hdbc'
    else:
        prefixo = 'hibc_'
        pasta += 'hibc'

    fullpath += pasta+'/'

    dicionario = {}
    status = 200
    repetidos = file_exists(prefixo, sufixo)
    if(not repetidos):
        path = dinamicPlots.HeatmapCity(cities_list,deaths,hash_value)
        fullpath = str(path)
        fullpath.encode()
        *caminho, pasta, arquivo = fullpath.split('/')
        nome, extensao = arquivo.split('.')
        dicionario = create_file_dictionary(nome, pasta)            
    else:
        existente = repetidos[0]
        last_update = find_file_date(existente)
        if(timestamp == last_update):
            dicionario = create_file_dictionary(existente, pasta)
            fullpath += existente+'.png'
        else:
            path = dinamicPlots.HeatmapCity(cities_list,deaths,hash_value)
            fullpath = str(path)
            fullpath.encode()
            *caminho, pasta, arquivo = fullpath.split('/')
            nome, extensao = arquivo.split('.')
            dicionario = create_file_dictionary(nome, pasta)
    dicionario['caminho'] = BASEURL+fullpath
    dicionario['selecionados'] = sufixo
    return jsonify(dicionario), status



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

@app.route('/grafico/<string:mortes>/<string:estado>', methods=['GET'])
def pegar_dados_csv(mortes, estado):
    with open('Instances/Cities/'+mortes+'/'+estado+'.csv', 'r', encoding="ISO-8859-1") as csv_file:
        
        csv_reader = csv.reader(csv_file, delimiter=',')

        csv_reader.__next__()
        
        cidades = []

        for row in csv_reader:
            cidades.append(row[0])
    return jsonify(cidades)


@app.route('/datas', methods=['GET'])
def pegar_datas():
    with open('Instances/Dates/dates.csv', 'r', encoding="ISO-8859-1") as csv_file:
        
        csv_reader = csv.reader(csv_file, delimiter=',')

        csv_reader.__next__()
        
        datas = []

        for row in csv_reader:
            datas.append(row[1])
    return jsonify(datas)


@app.route('/dados/estados', methods=['GET'])
def pegar_estados():
    states = []
    for s in data.states.values:
        states.append(s[0])
    return jsonify(states)

'''
@app.route('/dados/cidades/<string:estado>', methods=['GET'])
def pegar_cidades(estado):
    date = data.BR_Cases_By_City.date.unique()[-1]
    _temp = data.BR_Cases_By_City[data.BR_Cases_By_City["state"].values == estado].copy()
    _main = _temp[:5]
    _others = pd.DataFrame(None,columns=_main.columns)  
    _temp = pd.concat([_main,_others],ignore_index=True)
    _temp2 = data.getStateDemographicDataValue('RJ', 'Population')
    return jsonify({'Na mão': _temp, 'No método': _temp2})
'''

def criar_instancias():
    print('Executando a primeira vez')
    data.saveInstances()

if __name__ == '__main__':
    scheduler.add_job(id = 'New Instances', func = criar_instancias, trigger = 'interval', seconds = 3600*24)
    scheduler.start()
    criar_instancias()
    app.run(host='0.0.0.0', port=PORT)
