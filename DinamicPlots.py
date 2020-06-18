#!/usr/bin/env python
# coding: utf-8

# In[4]:


import numpy as np
import pandas as pd
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
register_matplotlib_converters()
plt.style.use('seaborn')


# In[8]:


class DinamicPlots:
    
    """
    This class purpose is to create comparison plots or
    more specific graphs.
    """
    
    BR_Cases_By_State = None
    BR_Cases_By_City = None
    BR_Cases_Total = None
    states = None
    
    def __init__(self,data):
        """
        data -> a DataLoad class instance
        
        Example:
        
        dp = DinamicPlots(DataLoad())
        """
        self.BR_Cases_By_State = data.BR_Cases_By_State
        self.BR_Cases_By_City = data.BR_Cases_By_City
        self.BR_Cases_Total = data.BR_Cases_Total
        self.states = data.states
               
            
    def ComparisonStateBar(self,state1,state2,deaths=False,hash_value=""):
        #hash_value = hash_value.decode('utf-8')
        
        _temp = self.BR_Cases_By_State[self.BR_Cases_By_State["state"].values == state1].copy()
        _temp2 = self.BR_Cases_By_State[self.BR_Cases_By_State["state"].values == state2].copy()
    
        legend = "Estados"
        title = state1+" x "+state2
        
        if deaths == True:
            _temp = _temp[_temp["deaths"] > 0]
            _temp2 = _temp2[_temp2["deaths"] > 0]
            
            _type = "deaths"
            path = u"__temp/__custom/__cdbs/cdbs_"+hash_value+".png"
        else:
            _type = "totalCases"
            path = u"__temp/__custom/__cibs/cibs_"+hash_value+".png"
        
        lenght = len(_temp.index)
        lenght2 = len(_temp2.index)
        
        _temp.loc[:,"date"] = range(lenght)
        _temp2.loc[:,"date"] = range(lenght2)
        
        _temp.index = range(lenght)
        _temp2.index = range(lenght2)
        
        comp = lenght if lenght<=lenght2 else lenght2
        
        #Create the plots
        Figure, Axes = plt.subplots(figsize=(8,8))

        if comp > 0:
            sns.barplot("date",_type,"state",data=pd.concat([_temp[:comp],_temp2[:comp]]),palette='inferno')
            Axes.plot("date",_type,data=_temp.loc[:comp-1],color='blue',label="_")
            Axes.plot("date",_type,data=_temp2.loc[:comp-1],color='red',label="_")
        elif lenght >0:
            sns.barplot("date",_type,"state",data=_temp,palette='inferno')
            Axes.plot("date",_type,data=_temp.loc[:comp-1],color='blue',label="_")
        elif lenght2 >0:
            sns.barplot("date",_type,"state",data=_temp2,palette='inferno')
            Axes.plot("date",_type,data=_temp2.loc[:comp-1],color='red',label="_")
        
        Axes.legend(fontsize=12).set_title(legend,prop={"size":14})
        Axes.set_title(state1+" x "+state2,fontsize=20)
        Axes.set_ylabel(u"Número",labelpad=10,fontsize=14)
        Axes.set_xlabel("Dias desde o Primeiro Infectado",labelpad=10,fontsize=14)

        plt.xticks(range(comp)[::int(comp/4)],range(comp)[::int(comp/4)])
        
        Figure.tight_layout()
        Figure.savefig(path)
        Figure.clear()
        
        plt.close()
        Axes.cla()
        del lenght
        del lenght2
        del _temp
        del _temp2
        del comp
        return path
        
    def ComparisonMultipleStates(self,states,deaths=False,time = False,hash_value=""):
        #hash_value = hash_value.decode('utf-8')
        
        states_list = []
        
        for i in states:
            states_list.append(self.BR_Cases_By_State[self.BR_Cases_By_State["state"].values == i].copy())
    
        legend = "Estados"
        title = u"Comparação"
        
        if deaths == True:
            for i in states_list:
                i = i[i["deaths"] > 0]
                i = i[i["deaths"] > 0]
            
            if time == False:
                _type = "deaths"
                path = u"__temp/__custom/__mcdbs/mcdbs_t_"+hash_value+".png"
            else:
                _type = "newDeaths"
                path = u"__temp/__custom/__mcdbs/mcdbs_"+hash_value+".png"
            
            xlabel = "Dias desde a Primeira Morte"
        else:
            if time == False:
                _type = "totalCases"
                path = u"__temp/__custom/__mcibs/mcibs_t_"+hash_value+".png"
            if time == False:
                _type = "newCases"
                path = u"__temp/__custom/__mcibs/mcibs_"+hash_value+".png"
        
            xlabel = "Dias desde o Primeiro Infectado"
        Figure, Axes = plt.subplots(figsize=(8,8))
        
        aux = 0
        for i in states_list:
            lenght = len(i.index)
            i.loc[:,"date"] = range(lenght)
            i.index = range(lenght)

            Axes.plot("date",_type,data=i,label=states[aux])
            aux+=1
        
        Axes.legend(fontsize=12).set_title(legend,prop={"size":14})
        Axes.set_title(u"Comparação de Múltiplos Estados",fontsize=20)
        Axes.set_ylabel(u"Número",labelpad=10,fontsize=14)
        Axes.set_xlabel(xlabel,labelpad=10,fontsize=14)
        
        Figure.tight_layout()
        Figure.savefig(path)
        Figure.clear()
        
        plt.close()
        Axes.cla()
        del states_list
        return path

    def ComparisonMultipleCities(self,cities,deaths=False,time = False,hash_value=""):
        #hash_value = hash_value.decode('utf-8')
        
        cities_list = []
        
        for i in cities:
            cities_list.append(self.BR_Cases_By_City[self.BR_Cases_By_City["city"].values == i].copy())
    
        legend = "Cidades"
        title = "Comparação"
        
        if deaths == True:
            for i in cities_list:
                i = i[i["deaths"] > 0]
                i = i[i["deaths"] > 0]
            
            if time == False:
                _type = "deaths"
                path = u"__temp/__custom/__mcdbc/mcdbc_"+hash_value+".png"
            else:
                _type = "newDeaths"
                path = u"__temp/__custom/__mcdbc/mcdbc_t_"+hash_value+".png"
            
            xlabel = "Dias desde a Primeira Morte"
        else:
            if time == False:
                _type = "totalCases"
                path = u"__temp/__custom/__mcibc/mcibc_"+hash_value+".png"
            else:
                _type = "newCases"
                path = u"__temp/__custom/__mcibc/mcibc_t_"+hash_value+".png"
        
            xlabel = "Dias desde o Primeiro Infectado"
        Figure, Axes = plt.subplots(figsize=(8,8))
        
        aux = 0
        for i in cities_list:
            lenght = len(i.index)
            i.loc[:,"date"] = range(lenght)
            i.index = range(lenght)

            Axes.plot("date",_type,data=i,label=cities[aux])
            aux+=1
        
        Axes.legend(fontsize=12).set_title(legend,prop={"size":14})
        Axes.set_title(u"Comparação de Múltiplas Cidades",fontsize=20)
        Axes.set_ylabel(u"Número",labelpad=10,fontsize=14)
        Axes.set_xlabel(xlabel,labelpad=10,fontsize=14)
        
        Figure.tight_layout()
        Figure.savefig(path)
        Figure.clear()
        
        plt.close()
        Axes.cla()
        del cities_list
        return path
        
    def HeatmapState(self,states_list,deaths=False,hash_value=""):
        df = pd.DataFrame()
        
        bol_expr1 = self.BR_Cases_By_State["state"] == states_list[0]
        
        if deaths == True:
            bol_expr2 = self.BR_Cases_By_State["deaths"] > 0
            title = "Dias desde a Primeira Morte"
            path = "__temp/__custom/__hdbs/hdbs_"+hash_value+".png"
            gtype = 'deaths'
        else:
            bol_expr2 = True
            title = "Dias desde o Primeiro Infectado"
            path = "__temp/__custom/__hibs/hibs_"+hash_value+".png"
            gtype = 'totalCases'
        
        bol = bol_expr1 & bol_expr2
        comp = len(self.BR_Cases_By_State[bol])
        
        for i in states_list[1:]:
            bol_expr1 = self.BR_Cases_By_State["state"] == i
            bol = bol_expr1 & bol_expr2
            
            lenght = len(self.BR_Cases_By_State[bol])
            comp = lenght if lenght < comp else comp
        
        for i in states_list:
            bol_expr1 = self.BR_Cases_By_State["state"] == i
            bol = bol_expr1 & bol_expr2
            
            _temp = self.BR_Cases_By_State[bol].copy()
            _temp["date"] = range(len(_temp.date))
            df = df.append(_temp.loc[_temp.index[:comp]])
            
        pivot = df.pivot('state','date',gtype)
        
        Figure, Axes = plt.subplots(figsize=(8,8))
        sns.heatmap(pivot,cmap="inferno_r",fmt="",ax=Axes)
        Axes.set_xlabel(title,fontsize=14)
        Axes.set_ylabel("_")
        Axes.tick_params(rotation=0)
        
        Figure.tight_layout()
        Figure.savefig(path)
        
        del df
        del lenght
        del comp
        del _temp
        Axes.cla()
        Figure.clear()
        plt.close()
        del pivot
        return path

    def HeatmapCity(self,cities_list,deaths=False,hash_value=""):
        df = pd.DataFrame()
        
        bol_expr1 = self.BR_Cases_By_City["city"].values == cities_list[0]
        
        if deaths == True:
            bol_expr2 = self.BR_Cases_By_City["deaths"]>0
            title = "Dias desde a Primeira Morte"
            path = "__temp/__custom/__hdbc/hdbc_"+hash_value+".png"
            gtype = 'deaths'
        else:
            bol_expr2 = True
            title = "Dias desde o Primeiro Infectado"
            path = "__temp/__custom/__hibc/hibc_"+hash_value+".png"
            gtype = 'totalCases'
            
        bol = bol_expr1 & bol_expr2
        comp = len(self.BR_Cases_By_City[bol])
        
        for i in cities_list[1:]:
            bol_expr1 = self.BR_Cases_By_City["city"].values == i
            bol = bol_expr1 & bol_expr2
            
            lenght = len(self.BR_Cases_By_City[bol])
            
            comp = lenght if lenght < comp else comp

        for i in cities_list:
            bol_expr1 = self.BR_Cases_By_City["city"].values == i
            bol = bol_expr1 & bol_expr2
            
            _temp = self.BR_Cases_By_City[bol].copy()
            _temp["date"] = range(len(_temp.date))
            df = df.append(_temp.loc[_temp.index[:comp]])

        pivot = df.pivot('city','date',gtype)

        Figure, Axes = plt.subplots(figsize=(8,8))
        sns.heatmap(pivot,cmap="inferno_r",fmt="",ax=Axes)
        Axes.set_xlabel(title,fontsize=14)
        Axes.set_ylabel("_")
        Axes.tick_params(rotation=0)
        
        Figure.tight_layout()
        Figure.savefig(path)
        
        del df
        del comp
        del _temp
        Axes.cla()
        Figure.clear()
        plt.close()
        del pivot
        return path

