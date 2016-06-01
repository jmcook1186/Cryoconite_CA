# -*- coding: utf-8 -*-
"""
Created on Tuesday April 26 07:07:54 2016

@author: Joseph
"""

import numpy as np
import matplotlib.pyplot as pyplot
import copy

Xlist = []
XXlist = []
Ylist = []
YYlist = []
Zlist = []
ZZlist = []



# set variable values

T = 5 # number of timesteps
Imax = 175  # total grid length
Islope = 150 # length of slope
Idel = 3 # frequency of sediment delivery
del_area = 10 # number of rows populated by sediment delivery
J = 150 # width of grid
coverage = 0.15 # % coverage by cryoconite
SGLspeed = 0.3 # migration rate for single grain layers (0-1)
MGLspeed = 0.7 # migration rate for stacked sediment (0-1)
flatspeed = 0.2 # migration rate for cryoconite on flat ice
buffer = 6 # size of 'buffer zone' where cryoconite is discarded off grid



# Set initial conditions

a = np.random.choice([0,1,2,3,4,5,6,7],(Imax,J),p=[1-coverage,coverage/7,coverage/7,coverage/7,coverage/7,coverage/7,coverage/7,coverage/7])
b = copy.deepcopy(a)
pyplot.figure(figsize=(12,12))
imshow(b,cmap='coolwarm') #Greys
cbar=pyplot.colorbar(ticks=[0,1,2,3,4,5,6,7,8,9],orientation='horizontal')
tick_params(axis='y',direction='out')
tick_params(axis='x',direction='out')
#pyplot.savefig('CAmovie0')




# define automaton rules

def cellrules(Islope,Imax,Idel,del_area,J,coverage,SGLspeed,MGLspeed,flatspeed,buffer):
    
    # Initialize variables for stats
    X = 0
    XX = 0
    Y = 0
    YY = 0
    Z  = 0
    ZZ = 0    
    
    for i in arange(0,Islope,1):
        for j in arange(1,J-1,1):

            Q=np.random.choice([1,2,3],p=(0.34,0.33,0.33))

            if a[i,j] == 1:

                QQ = np.random.choice([0,1],p = (1-SGLspeed,SGLspeed))

                if QQ == 0:                 
                    a[i,j] = a[i,j]

                elif QQ == 1:
                    
                   if Q == 1:

                       a[i,j] = a[i,j]-1
                       a[i+1,j] = a[i+1,j]+1
   
                   elif Q == 2:

                       a[i,j] = a[i,j]-1
                       a[i+1,j+1] = a[i+1,j+1]+1
               
                   elif Q == 3:
                    
                       a[i,j] = a[i,j]-1
                       a[i+1,j-1] = a[i+1,j-1]+1

            if a[i,j] > 1:

                P = np.random.choice([0,1],p=(1-MGLspeed,MGLspeed))

                if P == 0:
                    a[i,j]=a[i,j]

                if P == 1:
                    
                    if Q == 1:
                        a[i,j] = a[i,j]-1
                        a[i+1,j] = a[i+1,j]+1
       
                    elif Q == 2:
                        a[i,j] = a[i,j]-1
                        a[i+1,j+1] = a[i+1,j+1]+1
                   
                    elif Q == 3:
                        a[i,j] = a[i,j]-1
                        a[i+1,j-1] = a[i+1,j-1]+1
         
 
    for i in arange(Islope-1,Imax-1,1):
        for j in arange(1,J-1,1):
            
            QQQ = np.random.choice((0,1),p=[1-flatspeed,flatspeed])

            if QQQ == 0:
                a[i,j] = a[i,j]
                
            elif QQQ == 1:
                if a[i,j] ==1:
                   a[i,j] = a[i,j]-1 
                   a[i+1,j] = a[i+1,j]+1
                   
                if a[i,j] > 1:
                    QQQQ = np.random.choice((1,2,3),p=[0.4,0.3,0.3])
                    
                    if QQQQ == 1:
                        a[i,j] = a[i,j]-1
                        a[i+1,j] = a[i+1,j]+1
                        
                    if QQQQ == 2:
                        a[i,j] = a[i,j]-1
                        a[i+1,j-1] = a[i+1,j-1]+1

                    if QQQQ == 3:
                        a[i,j] = a[i,j]-1
                        a[i+1,j+1] = a[i+1,j+1]+1
   

    if t % Idel == 0:
        for i in arange(0,del_area,1):
            for j in arange(0,J-1,1):
                a[i,j] = np.random.choice([0,1,2,3,4,5,6,7],p=[1-coverage,coverage/7,coverage/7,coverage/7,coverage/7,coverage/7,coverage/7,coverage/7])
    
    
    for i in arange(1,Imax-1,1):
        for j in arange (1,J-1,1):
            if a[i,j] < 0:
               a[i,j] = 0
    
    for i in arange(Imax-buffer,Imax,1):
        for j in arange (0,J,1):
            a[i,j] = 0

   
    for i in arange(1,Imax-buffer,1):
        for j in arange(1,J-1,1):
            if a[i,j] >= 1:
                X=X+1
                XX = XX + a[i,j]

    Xlist.append(X)
    XXlist.append(XX)
    
    
    for i in arange(1,Islope,1):
        for j in arange(1,J,1):
            if a[i,j] > 0:
                Y= Y+1
                YY = YY + a[i,j]

    Ylist.append(Y)
    YYlist.append(YY)
                
    for i in arange(Islope,Imax,1):
        for j in arange(1,J,1):
            if a[i,j] > 0:
                Z = Z+1
                ZZ = ZZ + a[i,j]

    Zlist.append(Z)
    ZZlist.append(ZZ)
    
    
    print(T)
    print('total coverage',X)
    print('coverage on slope',Y)
    print('Volume on Slope',YY)
    print('coverage on flat',Z)
    print('Volume on flat',ZZ)
    
    return a, Xlist,Ylist,Zlist,XXlist,YYlist,ZZlist
                



# Evolve surface over time, plot and save result per timestep

def run(T,Islope,Imax,Idel,del_area,J,coverage,SGLspeed,MGLspeed,flatspeed,buffer):
    for t in arange(1,T,1):
        cellrules(Islope,Imax,Idel,del_area,J,coverage,SGLspeed,MGLspeed,flatspeed,buffer)
        flag = 'CAmovie%s' % str(t)    
        pyplot.figure(figsize=(12,12))
        pyplot.imshow(a,cmap='coolwarm',label=flag)
        cbar=pyplot.colorbar(ticks=[0,1,2,3,4,5,6,7,8,9],orientation='horizontal')
        tick_params(axis='y',direction='out')
        tick_params(axis='x',direction='out')
 #       plt.savefig("%s.png" % flag)
        pyplot.clf # clear fig to prevent T plots being stored in memory


# run functions

run(T,Islope,Imax,Idel,del_area,J,coverage,SGLspeed,MGLspeed,flatspeed,buffer)

pyplot.figure(figsize=(10,10))
pyplot.plot(Xlist,label='Total coverage')
pyplot.plot(XXlist,label='Total Volume')
pyplot.plot(Ylist,label='Slope coverage')
pyplot.plot(YYlist,label='Slope Volume')
pyplot.plot(Zlist,label='Flat coverage')
pyplot.plot(ZZlist,label='Flat Volume')
pyplot.legend(loc='best')
