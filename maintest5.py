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

# # Segmentar Nuvem de Pontos
# nuvem= "/home/feijo/Documents/volumecarvao/pontos_1574705224.txt" 
# xyz= np.loadtxt(nuvem, delimiter= ' ') #padronizar o formato txt com ou sem virgula dkdkke
# xyz= xyz[:,:3]

# # v = pptk.viewer(xyz)
# v = pptk.viewer(xyz)
# v.wait()

# sel = v.get('selected')
# len(sel)
# xyz[sel,:]
# v_sel = pptk.viewer(xyz[sel,:])
# np.savetxt("/home/feijo/Documents/volumecarvao/selected.txt", xyz[sel,:]) #transposta dos dados

# plt.close()


#LER NUVEM DE PONTOS
arquivo= "/home/feijo/Documents/volumecarvao/selected.txt" 
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

    #DEFININDO ALPHA
    alpha_shape = alphashape.alphashape(points, 0.)
    # alpha_shape = alphashape.alphashape(points) # calculo do alpha automatico
        
    fig, ax = plt.subplots()
    ax.scatter(*zip(*points))
    
    plt.xlim([np.min(dados_y), np.max(dados_y)])
    plt.ylim([np.min(dados_z), np.max(dados_z)])
    plt.axis("off") 

    # fig.savefig('/home/feijo/Documents/carvao_ufc/pilhasegmentada2/fig01_{}.png'.format(i))

    ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
    # plt.show()
    plt.xlim([np.min(dados_y), np.max(dados_y)]) # limitando o espaço de plotar em y
    plt.ylim([np.min(dados_z), np.max(dados_z)]) # limitando o espaço de plotar em z
    plt.axis("off") # sem eixos 
    
    #Plotar arquivo .txt de cada slice
    # np.savetxt('/home/feijo/Documentos/carvao_ufc/CHAO/result_chao/points_fig_{}.txt'.format(i), points, delimiter=' ') 
    fig.savefig('/home/feijo/Documents/volumecarvao/selecao_teste/fig1_{}.png'.format(i))
    print(i) 

    points_slice = [(x,y,z) for x,y,z in zip(dados_x[i*intervalo: (i+1)*intervalo],dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]
    np.savetxt('/home/feijo/Documents/volumecarvao/selecao_teste/points_fig1_{}.txt'.format(i), points_slice, delimiter=' ') 

    plt.close()

#identificar o numero de slices na path
folder = '/home/feijo/Documents/volumecarvao/selecao_teste' # path dos slices
filepaths = glob.glob(folder+ "/*.txt", recursive= True) 
print ("Numero total de slices".format(len(filepaths))) # Número de arquivos na path

for j in range(len(filepaths)):
#   img = np.asarray(Image.open("/home/feijo/Documentos/carvao_ufc/selecao_teste/points_fig_{}.txt".format(i)).convert('L'))
    img2 = np.loadtxt("/home/feijo/Documents/volumecarvao/selecao_teste/points_fig1_{}.txt".format(j), delimiter=' ')
    dados_df2= np.loadtxt(img2, delimiter= ' ')
    dados_df2= dados_df2[:,:3] # ajustar arquivo txt - (linha , coluna)
    dados2=dados_df2[dados_df2[:,0].argsort()] #ordenar eixo x
    dados_x2= dados2[:,0]
    dados_y2= dados2[:,1]
    dados_z2= dados2[:,2]

    intervalo2=1000

    for a in range(len(dados_y2)//intervalo2):
            
        points2 = [(x,z) for x,z in zip(dados_x2[a*intervalo2: (a+1)*intervalo2],dados_z2[a*intervalo2: (a+1)*intervalo2])]

        #DEFININDO ALPHA
        alpha_shape = alphashape.alphashape(points2,0.02)
        # alpha_shape = alphashape.alphashape(points) # calculo do alpha automatico
            
        fig, ax = plt.subplots()
        ax.scatter(*zip(*points2))
        
        plt.xlim([np.min(dados_x2), np.max(dados_x2)])
        plt.ylim([np.min(dados_z2), np.max(dados_z2)])
        plt.axis("off") 

        # fig.savefig('/home/feijo/Documents/carvao_ufc/pilhasegmentada2/fig01_{}.png'.format(i))

        ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
        # plt.show()
        plt.xlim([np.min(dados_x2), np.max(dados_x2)]) # limitando o espaço de plotar em y
        plt.ylim([np.min(dados_z2), np.max(dados_z2)]) # limitando o espaço de plotar em z
        plt.axis("off") # sem eixos 
        
        #Plotar arquivo .txt de cada slice
        # np.savetxt('/home/feijo/Documentos/carvao_ufc/CHAO/result_chao/points_fig_{}.txt'.format(i), points, delimiter=' ') 
        fig.savefig('/home/feijo/Documents/volumecarvao/selecao_teste/1/fig2_{}.png'.format(a))
        print(j) 

        points_slice2 = [(x,y,z) for x,y,z in zip(dados_x2[a*intervalo2: (a+1)*intervalo2],dados_y2[a*intervalo2: (a+1)*intervalo2],dados_z2[a*intervalo2: (a+1)*intervalo2])]
        np.savetxt('/home/feijo/Documents/volumecarvao/selecao_teste/1/points_fig2_{}.txt'.format(a), points_slice2, delimiter=' ') 

        plt.close()

total=0
voltotal=0

for z in range(len(filepaths)):
#   img = np.asarray(Image.open("/home/feijo/Documentos/carvao_ufc/selecao_teste/points_fig_{}.txt".format(i)).convert('L'))
    img3 = np.loadtxt("/home/feijo/Documents/volumecarvao/selecao_teste/1/points_fig2_{}.txt".format(z), delimiter=' ')
    
    dados_x= img3[:,0]
    dados_y= img3[:,1]
    dados_z= img3[:,2]
        
    # Eixo X - Comprimento
    x_ordenado=sorted(dados_x)
    x_max = max(x_ordenado)
    x_min = min(x_ordenado)
    xc = x_max - x_min
    
    # Eixo Y - Largura
    y_ordenado=sorted(dados_y)
    y_max = max(y_ordenado)
    y_min = min(y_ordenado)
    yc = y_max - y_min

    # Eixo Z - Altura
    z_ordenado=sorted(dados_z)
    z_max = max(z_ordenado)
    z_min = min(z_ordenado)
    zc = z_max - z_min
    
    pointstotal = np.array(img3)  # your points
    volume = ConvexHull(pointstotal).volume
    print(volume)
    voltotal += volume
    
    print(i) 
    print("Comprmento slice {} : {} metros".format(z,xc))
    print("Largura do slice {} : {} metros".format(z,yc))
    print("Altura  do slice {} : {} metros".format(z,zc))
    print("Volume do slice {}".format(volume))
    print("Volume Total {} m³".format(voltotal))
    # np.savetxt('/home/feijo/Downloads/pontos_18_02_20/test2/ResultadoVolume.txt'.format(voltotal)) 