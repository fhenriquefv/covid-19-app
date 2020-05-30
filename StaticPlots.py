#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
register_matplotlib_converters()
plt.style.use('seaborn')


# In[9]:


class StaticPlots:
    """
    The purpose of this class is create predetermined-sized 
    graphs and making the corresponding figures
    
    It inherets the data of its graphs from a instance of the
    DataLoad class
    """
    BR_Cases_By_State = None
    BR_Cases_By_City = None
    BR_Cases_Total = None
    states = None
    #cities = None
    data = None
    
    def __init__(self,data):
        
        """
        data: A instance of the DataLoad class
        --------------------------------------
        Example:
            sp = StaticPlots(DataLoad())
        """
        self.data = data
        self.BR_Cases_By_State = data.BR_Cases_By_State
        self.BR_Cases_By_City = data.BR_Cases_By_City
        self.BR_Cases_Total = data.BR_Cases_Total
        self.states = data.states
        #self.cities = data.cities
        
    def TemporalSeries(self, gvalue, gtype='state',ratio = None, hash_value=""):
        """
        gvalue: The name of the city or the code of the state
        
        gtype: Must be 'state' or 'city'
        
        hash_value: The suffix of the .png file name, must be unique
        """
        #gvalue = gvalue.decode('utf-8')
        #hash_value = hash_value.decode('utf-8')
        
        if gtype == 'state':
            _temp = self.BR_Cases_By_State[self.BR_Cases_By_State[gtype].values == gvalue]
            path = "__temp/__fixed/__tss/tss_"+hash_value+".png"
        else:
            _temp = self.BR_Cases_By_City[self.BR_Cases_By_City[gtype].values == gvalue]
            path = "__temp/__fixed/__tsc/tsc_"+hash_value+".png"
        
        Figure, Axes = plt.subplots(figsize=(8,8))

        Axes.plot_date("date","totalCases",data = _temp,linestyle="solid",label="Infectados",color='red',markevery=2)
        Axes.plot_date("date","deaths",data=_temp,linestyle="solid", label="Mortes",color='purple',markevery=2)

        Axes.set_title(u"Série Temporal - "+gvalue,fontsize=20)
        Axes.set_ylabel(u"Número",labelpad=10,fontsize=14)
        Axes.set_xlabel("Tempo (Dias)",labelpad=10,fontsize=14)
        #Axes.set_xticklabels(_temp["date"].dt.strftime("%d-%m-%Y"))

        Figure.legend(loc="upper left",bbox_to_anchor=(0.1,0.95),fontsize=12)
        Figure.autofmt_xdate()
        Figure.tight_layout()

        Figure.savefig(path,bbox_inches='tight')

        del _temp
        Axes.cla()
        Figure.clear()
        plt.close()
        return path
            
    
    def totalBarState(self,deaths=False,ratio = None, hash_value=""):
        """
        deaths: Must be a boolean value, if True, this function will
        create the graph considering the deaths values, if False, it
        will consider the number of infecteds
        
        ratio = None, 'Population', 'Area'
        
        hash_value: The suffix of the .png file name, must be unique
        """
        #hash_value = hash_value.decode('utf-8')
        _temp = self.BR_Cases_By_State[self.BR_Cases_By_State["date"] == self.BR_Cases_By_State.date.unique()[-1]]
        
        #Checks the value of the param
        if ratio == None:
            #If no ratio is specified, the desired ratio is 1
            d_ratio = pd.Series(1)
            label_ext = ""
            co = 1
            
        elif ratio == "Population":
            #If ratio is equal to 'Population'
            #The desired ratio will be a pandas Series of the
            #Population of each state
            d_ratio = pd.Series()
            for i in _temp["state"].values:
                d_ratio = d_ratio.append(pd.Series(self.data.getStateDemographicDataValue(
                                        i,"Population")),
                                        ignore_index = True)
            hash_value += "_b100k"
            label_ext = " /100000 habitantes"
            co = 100000
            
        elif ratio == "Area":
            #If ratio is equal to 'Population'
            #The desired ratio will be a pandas Series of the
            #Area of each state
            d_ratio = pd.Series()
            for i in _temp["state"].values:
                d_ratio = d_ratio.append(pd.Series(self.data.getStateDemographicDataValue(
                                        i,"Area")),
                                        ignore_index = True)
            hash_value += "_ba"
            label_ext = " / km2"
            co = 1
        
        #If the param deaths is False
        #The graph will consider the number of infecteds
        if deaths == False:
            l_values = _temp.totalCases
            l_index = _temp.state
            label = "Total de Infectados"+label_ext
            title = u"Número de Infectados Por Estado"+label_ext
            path = "__temp/__fixed/__tibs/tibs_"+hash_value+".png"
        #Else the graph will consider the number of deaths
        else:
            l_values = _temp.deaths
            l_index = _temp.state
            label = "Total de Mortes"+label_ext
            title = u"Número de Mortes Por Estado"+label_ext
            path = "__temp/__fixed/__tdbs/tdbs_"+hash_value+".png"
        
        #df is a temporary dataframe
        #the values column will be modified with the desired
        #ratio and the coefficient
        df = pd.DataFrame({"state":l_index,"values":l_values})
        df["values"] =  (df["values"].values*co/d_ratio.values)
        df.sort_values("values",inplace=True)
        
        #Create the plot 
        Figure, Axes = plt.subplots(figsize=(8,8))

        bar = sns.barplot(df["state"],df["values"],label=label,palette='inferno_r')
        
        for i in bar.patches:
            if ratio == "Population":
                string = str(int(i.get_height()))
            elif round(i.get_height(),2) > 0 and ratio == "Area":
                string = str(round(i.get_height(),2))
            else:
                string = "_"
            bar.annotate(string,(i.get_x(),i.get_height()),fontsize=10,ha='left')

        #Additional parameters
        Axes.set_title(title,fontsize=20)
        Axes.set_ylabel(u"Número",labelpad=10,fontsize=14)
        Axes.set_xlabel("Estado",labelpad=10,fontsize=14)

        #Figure parameters
        Figure.tight_layout()
        Figure.savefig(path,bbox_inches='tight')
        
        del l_values
        del l_index
        Figure.clear()
        plt.close()
        Axes.cla()
        del bar
        del _temp
        del df
        return path
    
    def totalBarCity(self,state,deaths=False,ratio=None,hash_value=""):
        """
        state: The code of the state
        
        deaths: Must be a boolean value, if True, this function will
        create the graph considering the deaths values, if False, it
        will consider the number of infecteds
        
        hash_value: The suffix of the .png file name, must be unique
        """
        _temp = self.BR_Cases_By_City[self.BR_Cases_By_City["date"] == self.BR_Cases_By_State.date.unique()[-1]]
        _temp = _temp[_temp["state"] == state]
        _temp = _temp[_temp["city"].values != "CASO SEM LOCALIZAÇÃO DEFINIDA-"+state]
        _temp.sort_values("totalCases",ascending=False,inplace=True)
        _temp = _temp.loc[_temp.index[:10]]
        
        if ratio is None:
            d_ratio = pd.Series(1)
            label_ext = ""
            co = 1
            
        elif ratio == "Population":
            d_ratio = pd.Series()
            for i in _temp["city"].values:
                d_ratio = d_ratio.append(pd.Series(self.data.getDemographicDataValue(
                                        state,i.split('-')[0],"Population")),
                                        ignore_index = True)
            hash_value += "_b100k"
            label_ext = "/100000 habitantes"
            co = 100000
        elif ratio == "Area":
            d_ratio = pd.Series()
            for i in _temp["city"].values:
                d_ratio = d_ratio.append(pd.Series(self.data.getDemographicDataValue(
                                        state,i.split('-')[0],"Area")),
                                        ignore_index = True)
            hash_value += "_ba"
            label_ext = "/km2"
            co = 1
            
        if deaths == False:
            l_values = _temp.totalCases
            l_index = _temp.state
            label = "Total de Infectados"+label_ext
            title = u"Maior Número de Infectados em "+state+" "+label_ext
            path = "__temp/__fixed/__tibc/tibc_"+hash_value+".png"
        else:
            l_values = _temp.deaths
            l_index = _temp.state
            label = "Total de Mortes"+label_ext
            title = u"Maior Número de Mortes em "+state+" "+label_ext
            path = "__temp/__fixed/__tdbc/tdbc_"+hash_value+".png"
            
        l_values = _temp.totalCases
        l_index = _temp.city
            
        df = pd.DataFrame({"city":l_index,"values":l_values})
        df["values"] = (df["values"].values/d_ratio.values)*co
        df.sort_values("values",inplace=True)
        
        Figure, Axes = plt.subplots(figsize=(8,8))
        
        bar = sns.barplot(df["city"],df["values"],palette='inferno_r')
        
        for i in bar.patches:
            for i in bar.patches:
                if ratio == "Population":
                    string = str(int(i.get_height()))
                elif round(i.get_height(),2) > 0 and ratio == "Area":
                    string = str(round(i.get_height(),2))
                else:
                    string = "_"

        bar.annotate(string,(i.get_x(),i.get_height()),fontsize=10,ha='left')

        Axes.set_title(title,fontsize=20)
        Axes.set_ylabel(u"Número",labelpad=10,fontsize=14)
        Axes.set_xlabel(u"Município",labelpad=10,fontsize=14)
        Axes.tick_params('x',rotation=90)
        
        Figure.tight_layout()
        
        Figure.savefig(path,bbox_inches='tight')
        
        del l_values
        del l_index
        Figure.clear()
        plt.close()
        Axes.cla()
        del bar
        del _temp
        del df
        return path
    
    def PieInfected(self,gvalue=None,gtype='state', hash_value = ""):
        
        #hash_value = hash_value.decode('utf-8')
        date = self.BR_Cases_By_City.date.unique()[-1]
        
        if gtype == 'state':
            _temp = self.BR_Cases_By_State[self.BR_Cases_By_State['date'] == date].sort_values("totalCases",ascending=False)
            _main = _temp[:5]
            _others = pd.DataFrame(None,columns=_main.columns)   
            _others.loc[0,"state"] = "Outros"
            _others.loc[0,"totalCases"] = sum(_temp[5:]["totalCases"].values)
            path = '__temp/__fixed/__pibs/pibs_'+hash_value+'.png'
        
        else:
            _temp = self.BR_Cases_By_City[(self.BR_Cases_By_City["state"] == gvalue) & (self.BR_Cases_By_City['date'] == date)].sort_values("totalCases",ascending=False)
            _main = _temp[:5]
            _others = pd.DataFrame(None,columns=_main.columns)   
            _others.loc[0,"city"] = "Outros"
            _others.loc[0,"totalCases"] = sum(_temp[5:]["totalCases"].values)
            path = '__temp/__fixed/__pibc/pibc_'+hash_value+'.png'

        _temp = pd.concat([_main,_others],ignore_index=True)
        colors = ['#FF214B','#FF5745','#FD6865','#FD8978','#FDA978','#DCDCDC']
        
        Figure, Axes = plt.subplots(figsize=(8,8))
        
        Axes.pie(_temp["totalCases"],labels=_temp[gtype], shadow=True,radius=2,autopct='%1.1f%%',colors=colors)
        Axes.axis('equal')

        Figure.tight_layout()
        Figure.savefig(path,bbox_inches='tight')

        del date
        del _temp
        del colors
        Axes.cla()
        Figure.clear()
        plt.close()
        return path
        
    def PieDeaths(self,gvalue=None,gtype='state',hash_value = ""):
        """
        gvalue: The name of the city or the code of the state
        
        gtype: Must be 'state' or 'city'
        
        hash_value: The suffix of the .png file name, must be unique
        """
    
        #hash_value = hash_value.decode('utf-8')
        date = self.BR_Cases_By_City.date.unique()[-1]
        
        if gtype == 'state':
            _temp = self.data.BR_Cases_By_State[self.data.BR_Cases_By_State['date'] == date].sort_values("deaths",ascending=False)
            _main = _temp[:5]
            _others = pd.DataFrame(None,columns=_main.columns)   
            _others.loc[0,"state"] = "Outros"
            _others.loc[0,"deaths"] = sum(_temp[5:]["deaths"].values)
            path = '__temp/__fixed/__pdbs/pdbs_'+hash_value+'.png'
        
        else:
            _temp = self.data.BR_Cases_By_City[(self.data.BR_Cases_By_City["state"] == gvalue) & (self.BR_Cases_By_City['date'] == date)].sort_values("deaths",ascending=False)
            _main = _temp[:5]
            _others = pd.DataFrame(None,columns=_main.columns)   
            _others.loc[0,"city"] = "Outros"
            _others.loc[0,"deaths"] = sum(_temp[5:]["deaths"].values)
            path = '__temp/__fixed/__pdbc/pdbc_'+hash_value+'.png'
        
        _temp = pd.concat([_main,_others],ignore_index=True)

        colors = ['#FF214B','#FF5745','#FD6865','#FD8978','#FDA978','#DCDCDC']
        
        Figure, Axes = plt.subplots(figsize=(8,8))
        
        Axes.pie(_temp["deaths"],labels=_temp[gtype], shadow=True,radius=2,autopct='%1.1f%%',colors=colors)
        Axes.axis('equal')

        Figure.tight_layout()
        Figure.savefig(path,bbox_inches='tight')

        del date
        del _temp
        del _main
        del _others
        del colors
        Axes.cla()
        Figure.clear()
        plt.close()
        return path
        
    def PieRegion(self,deaths=False, hash_value=""):
        """
        gvalue: The name of the city or the code of the state
        
        gtype: Must be 'state' or 'city'
        
        hash_value: The suffix of the .png file name, must be unique
        """
    
        if deaths == False:
            gtype = "totalCases"
            path = "__temp/__fixed/__pibr/pibr_"+hash_value+".png"
        else:
            gtype = "deaths"
            path = "__temp/__fixed/__pdbr/pdbr_"+hash_value+".png"
            
        reg = {'Norte':["AM","RR","AP","PA","TO","RO","AC"],
        'Nordeste':["MA","PI","CE","RN","PE","PB","SE","AL","BA"],
        'Centro-Oeste':["MT","MS","GO"],
        'Sudeste':["RJ","SP","MG","ES"],
        'Sul':["PR","RS","SC"]}
        total = {'Norte':0,'Nordeste':0,'Centro-Oeste':0,'Sudeste':0,'Sul':0}

        date = self.BR_Cases_By_State.date.unique()[-1]

        _temp = self.BR_Cases_By_State[self.BR_Cases_By_State.date == date]

        for i in reg.keys():
            for j in reg[i]:
                total[i] += _temp[_temp['state']==j][gtype].values[0]

        _temp = pd.DataFrame(total.values(),total.keys(),[gtype])

        colors = ['#00FA9A','#FD6865','#40E0D0','#DA70D6','#FDA978']

        Figure, Axes = plt.subplots(figsize=(8,8))

        Axes.pie(_temp[gtype],labels=_temp.index, shadow=True,radius=2,autopct='%1.1f%%',colors=colors)
        Axes.axis('equal')

        Figure.tight_layout()
        Figure.savefig(path,bbox_inches='tight')

        del _temp
        del colors
        del reg
        del total
        #del path
        del gtype
        Axes.cla()
        Figure.clear()
        plt.close()
        return path

    def MakeTemporalSeries(self):
        plt.ioff()
        for i in self.states["State"]:
            self.TemporalSeries(i,'state',i)
            for j in self.cities.loc[i]:
                if j != False:
                    self.TemporalSeries(j.encode('utf-8'),'city',j.encode('utf-8'))
                else: 
                    break

