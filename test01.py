# Developer: Pedro Feijó
############    Segmentar Pilha de Carvão ############
############    Gerar slices ############
############    Calcular Volume ############
import pptk
import pandas as pd
import numpy as np #somente dados numéricos
import matplotlib.pyplot as plt
import sys
from descartes import PolygonPatch
import alphashape
import random
from PIL import Image
import os
import glob 
from scipy.spatial import ConvexHull

#LER NUVEM DE PONTOS
arquivo= "/home/feijo/Documents/volumecarvao/selecao_teste/points_fig_493.txt" 
dados_df= np.loadtxt(arquivo, delimiter= ' ')
dados_df= dados_df[:,:3] # ajustar arquivo txt - (linha , coluna)
dados=dados_df[dados_df[:,0].argsort()] #ordenar eixo x
dados_x= dados[:,0]
dados_y= dados[:,1]
dados_z= dados[:,2]


intervalo= 100 # se ficar menor não fecha o polígono
for i in range(len(dados_y)//intervalo):
    points = [(x,z) for x,z in zip(dados_x[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]

    #DEFININDO ALPHA
    alpha_shape = alphashape.alphashape(points,0.02)
    # alpha_shape = alphashape.alphashape(points) # calculo do alpha automatico
        
    fig, ax = plt.subplots()
    ax.scatter(*zip(*points))
    
    plt.xlim([np.min(dados_x), np.max(dados_x)])
    plt.ylim([np.min(dados_z), np.max(dados_z)])
    plt.axis("off") 

    #fig.savefig('/home/feijo/Documents/carvao_ufc/pilhasegmentada2/fig01_{}.png'.format(i))

    ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
    # plt.show()
    plt.xlim([np.min(dados_x), np.max(dados_x)]) # limitando o espaço de plotar em y
    plt.ylim([np.min(dados_z), np.max(dados_z)]) # limitando o espaço de plotar em z
    plt.axis("off") # sem eixos 
    
    #Plotar arquivo .txt de cada slice
    # np.savetxt('/home/feijo/Documentos/carvao_ufc/CHAO/result_chao/points_fig_{}.txt'.format(i), points, delimiter=' ') 
    fig.savefig('/home/feijo/Documents/volumecarvao/selecao_teste/1/fig_{}.png'.format(i))
    print(i) 

    points_slice = [(x,y,z) for x,y,z in zip(dados_x[i*intervalo: (i+1)*intervalo],dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]
    np.savetxt('/home/feijo/Documents/volumecarvao/selecao_teste/1/points_fig_{}.txt'.format(i), points_slice, delimiter=' ') 

    plt.close()

#     #identificar o numero de slices na path
# folder = '/home/feijo/Documents/volumecarvao/selecao_teste/1' # path dos slices
# filepaths = glob.glob(folder+ "/*.txt", recursive= True) 
# print ("Numero total de slices".format(len(filepaths))) # Número de arquivos na path

# total=0
# voltotal=0


# for i in range(len(filepaths)):
#     img = np.asarray(Image.open("/home/feijo/Documentos/carvao_ufc/selecao_teste/points_fig_{}.txt".format(i)).convert('L'))
#     #img = np.loadtxt("/home/feijo/Documents/volumecarvao/selecao_teste/1/points_fig_{}.txt".format(i), delimiter=' ')
    
#     dados_x= img[:,0]
#     dados_y= img[:,1]
#     dados_z= img[:,2]
        
#     # Eixo X - Comprimento
#     x_ordenado=sorted(dados_x)
#     x_max = max(x_ordenado)
#     x_min = min(x_ordenado)
#     xc = x_max - x_min
    
#     # Eixo Y - Largura
#     y_ordenado=sorted(dados_y)
#     y_max = max(y_ordenado)
#     y_min = min(y_ordenado)
#     yc = y_max - y_min

#     # Eixo Z - Altura
#     z_ordenado=sorted(dados_z)
#     z_max = max(z_ordenado)
#     z_min = min(z_ordenado)
#     zc = z_max - z_min

#     img493 = np.loadtxt("/home/feijo/Documents/volumecarvao/selecao_teste/points_fig_493.txt")
#     # fig.savefig('/home/feijo/Documents/volumecarvao/selecao_teste/1/fig_493.png', img493)
#     ponto493= np.array(img493)
#     volume2 = ConvexHull(ponto493).volume


#     points = np.array(img)  # your points
#     volume = ConvexHull(points).volume
#     print(volume)
#     voltotal += volume
    
#     print(i) 
#     print("Comprmento slice {} : {} metros".format(i,xc))
#     print("Largura do slice {} : {} metros".format(i,yc))
#     print("Altura  do slice {} : {} metros".format(i,zc))
#     print("Volume do slice {}".format(volume))
#     print("Volume Total {} m³".format(voltotal))

#     print("VOLUME DE UM ÚNICO SLICE {} m³".format(volume2))
