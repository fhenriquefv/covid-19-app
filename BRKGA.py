#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# In[2]:


class BRKGA:

    
    #Genetic Parameters
    _capacity = []
    _cost =[]
    _obj = 0
    _obj_evolution = []
    #Population Parameters
    _psize = 0
    _csize = 0
    _elite = 0
    _mutant = 0
    #Number of Iterations
    _n = 0
    
    def __init__(self, cp_array, ct_array, c_size, p_size, elite, mutant, n_it, obj = False):
        
        """
        cp_array -> list of the capacities of the facilities sorted by index order
        
        ct_array -> list of the costs of the facilities sorted by index order
        
        c_size -> int vale, size of the chromosome
        
        p_size -> int value, size of the population
        
        m -> float value, represents the limit to simultaneous facilities
        
        elite -> int value, number of elites per population
        
        mutant -> int value, number of mutants per population
        
        n_it -> int value, number of iterations
        
        obj -> bool value, False(to return value) or True (to return cover)
        """
        if(type(cp_array) is list or type(cp_array) is np.ndarray):
            self._cover = cp_array
        else:
            raise ValueError("The value of the parameter \"cp_array\" is invalid, please enter a valid list or ndarray.")
        
        if(type(ct_array) is list or type(ct_array) is np.ndarray):
            self._cost = ct_array
        else:
            raise ValueError("The value of the parameter \"ct_array\" is invalid, please enter a valid list or ndarray.")

        if(type(p_size) is int or type(p_size) is np.int64):
            self._psize = p_size
        else:
            raise ValueError("The value of the parameter \"p_size\" is invalid, please enter a valid integer.")
            
        if(type(c_size) is int or type(c_size) is np.int64):
            self._csize = c_size
        else:
            raise ValueError("The value of the parameter \"c_size\" is invalid, please enter a valid integer.")
            
        if(type(elite) is int or type(c_size) is np.int64):
            self._elite = elite
        else:
            raise ValueError("The value of the parameter \"elite\" is invalid, please enter a valid integer.")
            
        if(type(mutant) is int or type(c_size) is np.int64):
            self._mutant = mutant
        else:
            raise ValueError("The value of the parameter \"mutant\" is invalid, please enter a valid integer.")
            
        
        if(type(n_it) is int or type(c_size) is np.int64):
            self._n = n_it
        else:
            raise ValueError("The value of the parameter \"n_it\" is invalid, please enter a valid integer value.")
        
        if(type(obj) is bool or type(c_size) is np.int64):
            self._obj = obj
        else:
            raise ValueError("The value of the parameter \"obj\", please enter a valid boolean.")
         
    def Encoder(self, size):
        """
        size -> int value, size of the array
        
        This function creates a array of the specified size with random values in it
        """
        gene = pd.Series(np.random.rand(size))
        return gene
    
    def Decoder(self,encoded_list,obj):
        """
        encoded_list -> list, a list containing random values
        
        obj -> bool value, objective of the application, will determine the return value
        
        This function will return a tuple of containing the objective value and the gene, respectively
        """
        
        #decoded_list will receive the corresponding index 
        #for the sorted values of the encoded_list
        decoded_list = encoded_list.sort_values(kind='mergesort').index
        
        #this variable represents the total cost of keeping
        #facilities operational
        cost = 0
        
        #this variable represents the total cover of the
        #operational facilities 
        cover = 0
        
        #this variable will be the gene with the specified
        #chromossome size
        gene = []
        for i in decoded_list[0:self._csize]:
            #cost of the current element it subtracts the value
            #because the objective function in which it is considered
            #is minimizing
            cost-=self._cost[i]
            #cover of the current element
            cover += self._cover[i]
            #appends the actual value to the gene
            gene.append(i)
                
        #if Obj == False, the objective of the function
        #is to minimize the cost, if Obj == True, the
        #objective is to maximize coverage
        if obj == False:
            return cost, gene
        else:
            return cover, gene
        
    def Crossover(self,parent1, parent2):
        """
        parent1 -> list, the elite-parent
        
        parent2 -> list, the non-elite parent
        
        This function takes a elite-parent and a normal parent
        to generate a son chromossome 
        """
        #son a priori have the same elements of the elite-parent
        #it will change according to the coin toss later
        son = list(parent1)
        
        #converts the list to Pandas Series
        p1 = pd.Series(parent1)
        p2 = pd.Series(parent2)
        
        #all common values between the two parents
        common_values = []
        #this loop will search for the common values and
        #add it to the list
        for i in p1.index:
            if p1[i] in p2.values:
                common_values.append(p1[i])

        #a dictionary that will receive the common values as key
        #and a tuple of its position where the value is in each
        #parent
        tpl = {x:0 for x in common_values}
        for i in range(0,len(common_values)):
            tpl[common_values[i]] =  (p1[p1==common_values[i]].index[0],p2[p2 == common_values[i]].index[0])

            
        #loop that generates the coin toss
        for i in range(0,len(p1)):
            coin = np.random.rand()
            if(coin <= 0.5):
                #if the value is in common_values, to avoid duplicity, it will permute
                #the position of the value in the i'th position with it's corresponding
                #position in the other parent
                if p1[i] in common_values:
                    son[tpl[p1[i]][1]],son[tpl[p1[i]][0]] =son[tpl[p1[i]][0]],son[tpl[p1[i]][1]]
                elif p2[i] in common_values:
                    son[tpl[p2[i]][1]],son[tpl[p2[i]][0]] =son[tpl[p2[i]][0]],son[tpl[p2[i]][1]]
                else:
                    #if the selected value is not commom to both, it will do the crossover
                    #normaly
                    son[i] = p2.loc[i]
        return son
                
    def Elite(self,solutions, population, e):
        #creates the array of elite chromossomes
        elite = []
        #creates the array of the "e" best solutions
        elite_sol = solutions.sort_values(ascending=False, kind='mergesort')
        #takes the best solution of this population
        self._obj_evolution.append(elite_sol[elite_sol.index[0]])
        for i in range(0,e):
            #appends to the elite array the best solutions and removes
            #it from the population to avoid duplicity issues
            elite.append(population[elite_sol.index[i]])
        
        for i in elite:
            if i in population:
                population.remove(i)
        return elite_sol, elite
    
    def Mutant(self,m):
        #list of mutant genes
        mutant = []
        #list of the solution of the mutant genes
        mutant_sol = []
        #this loop will create m mutant cromossomes
        for i in range(0,m):
            encoded_gene = self.Encoder(len(self._cost))
            sol, decoded_gene = self.Decoder(encoded_gene,self._obj)
            mutant.append(decoded_gene)
            mutant_sol.append(sol)
        return mutant_sol, mutant
    
    
    def Solve(self):
        """
        This is the main function of the BRKGA class, it will call the other
        functions and solve the problem for the given parameters
        """
        #Clears the objective evolution
        self._obj_evolution = []
        #Counter of iterations
        count = 0
        
        #Holds the values that will be in the next
        #population
        next_population = []
        
        #Holds the corresponding values of the
        #next population solutions
        next_solutions = pd.Series()
        
        #This is the array of the best elite
        #found in each solution
        best_chromossomes = []
        
        #This is the array of the best elite
        #found corresponding solutions
        best_solutions = []
        
        while(count < self._n):
            
            #actual population
            population = []
            
            #actual solution
            solutions = pd.Series()
            
            #the list of the elite chromossomes and
            #they corresponding solution value
            elite = []
            elite_sol= []
            
            mutant = []
            mutant_sol = []
            #First Population
            if count == 0:
                
                #creates the population
                for i in range(0,self._psize):
                    chromossome = self.Encoder(len(self._cost))
                    obj, decoded_chromossome = self.Decoder(chromossome,self._obj)
                    solutions = solutions.append(pd.Series(obj),ignore_index=True)
                    population.append(decoded_chromossome)
                #creates the elites chromossomes
                elite_sol, elite = self.Elite(solutions,population,self._elite)
                #creates the mutant chromossomes
                mutant_sol, mutant = self.Mutant(self._mutant)
                
                #adds the elite chromossomes to the next generation
                for i in range(0,self._elite):
                    next_population.append(elite[i])
                    next_solutions = next_solutions.append(pd.Series(elite_sol[elite_sol.index[i]]),ignore_index=True)
                    #if the chromossome is not in the best_solutions, we add it to the list
                    if not(elite[i] in best_chromossomes) and not(elite_sol[elite_sol.index[i]] in best_solutions):
                        best_chromossomes.append(elite[i])
                        best_solutions.append(elite_sol[i])
                    
                #adds the mutant chromossomes to the next generation
                for i in range(0,self._mutant):
                    next_population.append(mutant[i])
                    next_solutions = next_solutions.append(pd.Series(mutant_sol[i]),ignore_index=True)

                #calculates how many chromossomes are needed to complete the population
                p_left = self._psize - self._elite - self._mutant
                
                for i in range(0,p_left):
                    elite_parent = elite[np.random.randint(0,self._elite)]
                    
                    normal_parent = population[np.random.randint(0,len(population))]
                    son = self.Crossover(elite_parent,normal_parent)
                    
                    
                    #cost of the son's solution to cost-wise objective
                    cost = 0
                    #cover of the son's solution to cover-wise objective
                    cover = 0
                    
                    #this loop calculates the son objective value
                    for j in son:
                        if self._obj == False:
                            cost -= self._cost[j]
                        else:
                            cover+= self._cover[j]
                    
                    sol = 0
                    
                    if self._obj == False:
                        sol = cost
                    else:
                        sol = cover
                    next_population.append(son)
                    next_solutions = next_solutions.append(pd.Series(sol),ignore_index=True)
            else:
                population = []
                solutions = pd.Series()
                
                #appends the previous value of next_population to the popultation array
                for i in next_population:
                    population.append(i)
                #and clears the next_population to 
                next_population = []
                
                for i in next_solutions.index:
                    solutions = solutions.append(pd.Series(next_solutions.loc[i]),ignore_index=True)
                    
                next_solutions = pd.Series()
                next_population = []
                
                #creates the elites chromossomes
                elite_sol, elite = self.Elite(solutions,population,self._elite)
                #creates the mutant chromossomes
                mutant_sol, mutant = self.Mutant(self._mutant)
            
                 #adds the elite chromossomes to the next generation
                for i in range(0,self._elite):
                    next_population.append(elite[i])
                    next_solutions = next_solutions.append(pd.Series(elite_sol[elite_sol.index[i]]),ignore_index=True)
                    #if the chromossome is not in the best_solutions, we add it to the list
                    if not(elite[i] in best_chromossomes) and not(elite_sol[elite_sol.index[i]] in best_solutions):
                        best_chromossomes.append(elite[i])
                        best_solutions.append(elite_sol[elite_sol.index[i]])
                    
                #adds the mutant chromossomes to the next generation
                for i in range(0,self._mutant):
                    next_population.append(mutant[i])
                    next_solutions = next_solutions.append(pd.Series(mutant_sol[i]),ignore_index=True)
                    
                #calculates how many chromossomes are needed to complete the population
                p_left = self._psize - self._elite - self._mutant
                
                for i in range(0,p_left):
                    elite_parent = elite[np.random.randint(0,self._elite)]
                    normal_parent = population[np.random.randint(0,len(population))]
                    son = self.Crossover(elite_parent,normal_parent)
                    
                    
                    #cost of the son's solution to cost-wise objective
                    cost = 0
                    #cover of the son's solution to cover-wise objective
                    cover = 0
                    #this loop calculates the son objective value
                    for j in son:
                        if self._obj == False:
                            cost -= self._cost[j]
                        else:
                            cover+= self._cover[j]
                    
                    sol = 0
                    
                    if self._obj == False:
                        sol = cost
                    else:
                        sol = cover
                    next_population.append(son)
                    next_solutions = next_solutions.append(pd.Series(sol),ignore_index=True)
            count+=1
        return best_solutions, best_chromossomes
    
    def getObjectiveEvolution(self):
        return self._obj_evolution

