#!/usr/bin/python3

############    LAPISCO / GPAR                   ############
############    Developer: Pedro Feijó           ############
############    Adatpação IHM: Adriano Rodrigues
############    Segmentação                      ############
############    Calcular Volume                  ############

import pptk
import pandas as pd
import numpy as np
import sys
from descartes import PolygonPatch
import alphashape
import random
from PIL import Image
import os
import glob
import matplotlib.pyplot as plt

# Get script file root name
root = os.path.dirname(os.path.abspath(__file__)) + '/'

folder = root+'selecao_teste' # path dos slices
try:
    os.mkdir(folder)
except:
    pass
##### Segmentar Nuvem de Pontos

# nuvem = root + 'pontos.txt'
# nuvem = root + 'ensaio9teste15.txt'
nuvem = root + 'ensaio9alinhado.txt'
try:
    xyz= np.loadtxt(nuvem, delimiter= ' ')
except:
    sys.exit('File ' + nuvem + ' does not exists!')
xyz= xyz[:,:3]

z = xyz[:,2]
bxplt = plt.boxplot(z)
M1 = bxplt['whiskers'][1]._y[0]
M2 = bxplt['whiskers'][1]._y[1]
m1 = bxplt['whiskers'][0]._y[0]
m2 = bxplt['whiskers'][0]._y[1]
# plt.show()
v = pptk.viewer(xyz,z)
v.color_map('jet',scale=[m1,M2])
v.wait()

sel = v.get('selected')
len(sel)
selected = xyz[sel,:]
z = selected[:,2]
bxplt = plt.boxplot(z)
M1 = bxplt['whiskers'][1]._y[0]
M2 = bxplt['whiskers'][1]._y[1]
m1 = bxplt['whiskers'][0]._y[0]
m2 = bxplt['whiskers'][0]._y[1]
v_sel = pptk.viewer(selected,z)
v_sel.color_map('jet',scale=[m1,M2])
np.savetxt('selected.txt', selected) # Transposta dos dados

# LER NUVEM DE PONTOS
arquivo= root+"selected.txt"
dados_df= np.loadtxt(arquivo, delimiter= ' ')
dados_df= dados_df[:,:3] # ajustar arquivo txt - (linha , coluna)
dados=dados_df[dados_df[:,0].argsort()] #ordenar eixo x
dados_x= dados[:,0]
dados_y= dados[:,1]
dados_z= dados[:,2]

# SEPARAR EM SLICES NO EIXO X COM INTERVALOR DE 1000
intervalo= 1000 # se ficar menor não fecha o polígono
for i in range(len(dados_x)//intervalo):
    points = [(y,z) for y,z in zip(dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]

    # DEFININDO ALPHA
    alpha_shape = alphashape.alphashape(points, 0.)
    # alpha_shape = alphashape.alphashape(points) # calculo do alpha automatico
        
    fig, ax = plt.subplots()
    ax.scatter(*zip(*points))
    
    plt.xlim([np.min(dados_y), np.max(dados_y)])
    plt.ylim([np.min(dados_z), np.max(dados_z)])
    plt.axis("off") 


    ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
    plt.xlim([np.min(dados_y), np.max(dados_y)]) # limitando o espaço de plotar em y
    plt.ylim([np.min(dados_z), np.max(dados_z)]) # limitando o espaço de plotar em z
    plt.axis("off") # sem eixos 
    
    # Plotar arquivo .txt de cada slice
    fig.savefig(root+'selecao_teste/fig_{}.png'.format(i))
    print(i) 

    points_slice = [(x,y,z) for x,y,z in zip(dados_x[i*intervalo: (i+1)*intervalo],dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]
    np.savetxt(root+'selecao_teste/points_fig_{}.txt'.format(i), points_slice, delimiter=' ') 

    plt.close()

# Identificar o numero de slices na path
folder = root+'selecao_teste' # path dos slices
filepaths = glob.glob(folder+ "/*.png", recursive= True)  
print (len(filepaths)) # Número de arquivos na path

total=0

for i in range(len(filepaths)):
    img = np.asarray(Image.open(root+"/selecao_teste/fig_{}.png".format(i)).convert('L'))
    img = 1 * (img < 255)
    m,n = img.shape
    total += img.sum() 
    print("{} white pixels, out of {} pixels in total.".format(img.sum(), m*n)) 
    
print("Número total de pixels {}".format(total))

somaslices = total
volumeareaporpixels= somaslices*0.005657 #relação pixels to m3 

print("Volume total = {} m³".format(volumeareaporpixels))