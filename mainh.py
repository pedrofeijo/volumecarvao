# -*- coding: utf-8 -*-
#!/usr/bin/python3

############    LAPISCO / GPAR                   ############
############    Developer: Pedro Feijó           ############
############    Adatpação IHM: Adriano Rodrigues
############    Segmentação                      ############
############    Calcular Volume                  ############

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import alphashape
import random
import glob
import pptk
import sys
import os
from   PIL import Image
from   descartes import PolygonPatch
from scipy.spatial import ConvexHull

# Get script file's root name
root = os.path.dirname(os.path.abspath(__file__)) + '/'

# Path to slices figures
pathToSlices = root + 'selecao_teste' # path dos slices
try:
    # Tries to make the directory "selecao_teste"
    os.mkdir(pathToSlices)
except:
    pass

# LER NUVEM DE PONTOS
# Set root path to selected points
arquivo  = root + "100Kmergedstockpiles.txt"
# Try to load the txt point cloud into a numpy float matrix
dados_df = np.loadtxt(arquivo, delimiter= ' ')
dados_df = dados_df[:,:3] # ajustar arquivo txt - (linha , coluna)

dados   = dados_df[dados_df[:,0].argsort()] # ordenar eixo x
dados_x = dados[:,0]
dados_y = dados[:,1]
dados_z = dados[:,2]

# SEPARAR EM SLICES NO EIXO X COM INTERVALOR DE 1000
intervalo= 1000 # se ficar menor não fecha o polígono
total = 0
voltotal=0
for i in range(len(dados_x)//intervalo):
    points = [(y,z) for y,z in zip(dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]

    # DEFININDO ALPHA
    alpha_shape = alphashape.alphashape(points,0.)
    # alpha_shape = alphashape.alphashape(points) # calculo do alpha automatico
    
    fig, ax = plt.subplots()
    ax.scatter(*zip(*points))
    
    ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2)) #0,2
    
    # Plotar arquivo .txt de cada slice
    # fig.savefig(root+'selecao_teste/fig_{}.png'.format(i))
    print(i) 

    points_slice = [(x,y,z) for x,y,z in zip(dados_x[i*intervalo: (i+1)*intervalo],dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]

    plt.close(fig)
    #plt.close(allfig)

    dados_df2= np.array(points_slice)[:,:3] # ajustar arquivo txt - (linha , coluna)
    dados2 = dados_df2[dados_df2[:,0].argsort()] #ordenar eixo x
    dados_x2= dados2[:,0]
    dados_y2= dados2[:,1]
    dados_z2= dados2[:,2]
    intervalo2=100
    for a in range(len(dados_y2)//intervalo2): 
            points2 = [(x,z) for x,z in zip(dados_x2[a*intervalo2: (a+1)*intervalo2],dados_z2[a*intervalo2: (a+1)*intervalo2])]

            #DEFININDO ALPHA
            alpha_shape = alphashape.alphashape(points2,0.)

            allfig, ax = plt.subplots()
            ax.scatter(*zip(*points2))

            ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))  #0,2
            points_slice2 = [(x,y,z) for x,y,z in zip(dados_x2[a*intervalo2: (a+1)*intervalo2],dados_y2[a*intervalo2: (a+1)*intervalo2],dados_z2[a*intervalo2: (a+1)*intervalo2])]

            plt.close(fig)
            plt.close(allfig)

            pointstotal = np.array(points_slice2)  # your points
            volume = ConvexHull(pointstotal).volume
            print("slice {}_{}".format(i,a))
            print(volume)
            voltotal += volume

    plt.close(fig)
    # plt.close(allfig)
               
print("Volume do slice {}".format(volume))
print("Volume Total {} m³".format(voltotal))      



