#!/usr/bin/python3
# -*- coding: utf-8 -*-


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
# ##### Segmentar Nuvem de Pontos

# # Choose a txt point cloud file
# # nuvem = root + 'pontos.txt'
# # nuvem = root + 'ensaio9teste15.txt'
# nuvem = root + 'ensaio9alinhado.txt'

# try:
#     # Try to load the txt point cloud into a numpy float matrix
#     xyz = np.loadtxt(nuvem, delimiter= ' ')
# except:
#     # Display error message if load fails
#     sys.exit('Error loading ' + nuvem + '!')

# # Filter x, y and z coordinates
# xyz = xyz[:,:3]
# # Register z values (used to coloring)
# z = xyz[:,2]

# # Filter z data to exclude outliers and help colouring
# bxplt = plt.boxplot(z)
# m1 = bxplt['whiskers'][0]._y[0] # Minimum value of the minimum range
# m2 = bxplt['whiskers'][0]._y[1] # Maximum value of the minimum range
# M1 = bxplt['whiskers'][1]._y[0] # Minimum value of the maximum range
# M2 = bxplt['whiskers'][1]._y[1] # Maximum value of the maximum range
# # plt.show() # displays boxplot

# # Load point cloud to viewer referencing z axis to colors
# v = pptk.viewer(xyz,z)
# # Displays point cloud
# v.color_map('jet',scale=[m1,M2])
# # Waits for keypress: 'Enter' to confirm and 'Esc' to cancel
# v.wait()

# # Collects selected points indexes
# sel = v.get('selected')
# len(sel)
# # Create a numpy matrixes of selected points
# selected = xyz[sel,:]
# # Register z values (used to coloring)
# z = selected[:,2]

# # Filter z data to exclude outliers and help colouring
# bxplt = plt.boxplot(z)
# m1 = bxplt['whiskers'][0]._y[0] # Minimum value of the minimum range
# m2 = bxplt['whiskers'][0]._y[1] # Maximum value of the minimum range
# M1 = bxplt['whiskers'][1]._y[0] # Minimum value of the maximum range
# M2 = bxplt['whiskers'][1]._y[1] # Maximum value of the maximum range

# # Load point cloud to viewer referencing z axis to colors
# v_sel = pptk.viewer(selected,z)
# # Displays point cloud
# v_sel.color_map('jet',scale=[m1,M2])
# # Save archive with selected points
# np.savetxt('selected.txt', selected) # Transposta dos dados

# LER NUVEM DE PONTOS
# Set root path to selected points
arquivo  = root + "1mCuboinho.txt"
# Try to load the txt point cloud into a numpy float matrix
dados_df = np.loadtxt(arquivo, delimiter= ' ')
dados_df = dados_df[:,:3] # ajustar arquivo txt - (linha , coluna)

dados   = dados_df[dados_df[:,0].argsort()] # ordenar eixo x
dados_x = dados[:,0]
dados_y = dados[:,1]
dados_z = dados[:,2]

# SEPARAR EM SLICES NO EIXO X COM INTERVALOR DE 1000
intervalo= 1000 # se ficar menor não fecha o polígono
for i in range(len(dados_x)//intervalo):
    points = [(y,z) for y,z in zip(dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]

    # DEFININDO ALPHA
    alpha_shape = alphashape.alphashape(points, 0.)
    # alpha_shape = alphashape.alphashape(points) # calculo do alpha automatico
    
    fig, ax = plt.subplots()
    ax.scatter(*zip(*points))
    
    # plt.xlim([np.min(dados_y), np.max(dados_y)])
    # plt.ylim([np.min(dados_z), np.max(dados_z)])
    # plt.axis("off") 

    ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
    # plt.xlim([np.min(dados_y), np.max(dados_y)]) # limitando o espaço de plotar em y
    # plt.ylim([np.min(dados_z), np.max(dados_z)]) # limitando o espaço de plotar em z
    # plt.axis("off") # sem eixos
    
    # Plotar arquivo .txt de cada slice
    fig.savefig(root+'selecao_teste/fig_{}.png'.format(i))
    print(i) 

    points_slice = [(x,y,z) for x,y,z in zip(dados_x[i*intervalo: (i+1)*intervalo],dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]
    np.savetxt(root+'selecao_teste/points_fig_{}.txt'.format(i), points_slice, delimiter=' ') 

    plt.close()

    
# Identificar o numero de slices na path

filepaths = glob.glob(pathToSlices+ "/*.txt", recursive= True)  
print (len(filepaths)) # Número de arquivos na path

total = 0
voltotal=0

for j in range(len(filepaths)):
    dados_df2 = np.loadtxt("/home/feijo/Documents/volumecarvao/selecao_teste/points_fig_{}.txt".format(j), delimiter=' ')
#     dados_df2= np.loadtxt(img2,delimiter= ' ')
    dados_df2= dados_df2[:,:3] # ajustar arquivo txt - (linha , coluna)
    dados2=dados_df2[dados_df2[:,0].argsort()] #ordenar eixo x
    dados_x2= dados2[:,0]
    dados_y2= dados2[:,1]
    dados_z2= dados2[:,2]
    intervalo2=100
    for a in range(len(dados_y2)//intervalo2): 
            points2 = [(x,z) for x,z in zip(dados_x2[a*intervalo2: (a+1)*intervalo2],dados_z2[a*intervalo2: (a+1)*intervalo2])]
    #     dados_df2= np.loadtxt(img2,delimiter= ' ')
            # dados_df2= dados_df2[:,:3] # ajustar arquivo txt - (linha , coluna)
            # dados2=dados_df2[dados_df2[:,0].argsort()] #ordenar eixo x
            # dados_x2= dados2[:,0]
            # dados_y2= dados2[:,1]
            # dados_z2= dados2[:,2]
            intervalo2=100
            #DEFININDO ALPHA
            alpha_shape = alphashape.alphashape(points2,0.2)
    #         alpha_shape = alphashape.alphashape(points) # calculo do alpha automatico

            allfig, ax = plt.subplots()
            ax.scatter(*zip(*points2))

            # plt.xlim([np.min(dados_x2), np.max(dados_x2)])
            # plt.ylim([np.min(dados_z2), np.max(dados_z2)])
            # plt.axis("off") 

            ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
            # plt.show()
            # plt.xlim([np.min(dados_x2), np.max(dados_x2)]) # limitando o espaço de plotar em y
            # plt.ylim([np.min(dados_z2), np.max(dados_z2)]) # limitando o espaço de plotar em z
            # plt.axis("off") # sem eixos 

            points_slice2 = [(x,y,z) for x,y,z in zip(dados_x2[a*intervalo2: (a+1)*intervalo2],dados_y2[a*intervalo2: (a+1)*intervalo2],dados_z2[a*intervalo2: (a+1)*intervalo2])]

            pointstotal = np.array(points_slice2)  # your points
            volume = ConvexHull(pointstotal).volume
            print("slice {}_{}".format(j,a))
            print(volume)
            voltotal += volume
                
print("Volume do slice {}".format(volume))
print("Volume Total {} m³".format(voltotal))      



