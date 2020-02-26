############    LAPISCO / GPAR            ############
############    Developer: Pedro Feijó    ############
############    Segmentação               ############
############    Calcular Volume           ############
import pptk
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import sys
from descartes import PolygonPatch
import alphashape
import random
from PIL import Image
import os
import glob 

##### Segmentar Nuvem de Pontos

nuvem= "/home/feijo/Documentos/carvao_ufc/pontos_1574700886/pontos_1574700886.txt" 
xyz= np.loadtxt(nuvem, delimiter= ' ')
xyz= xyz[:,:3]

v = pptk.viewer(xyz)
v.wait()

sel = v.get('selected')
len(sel)
xyz[sel,:]
v_sel = pptk.viewer(xyz[sel,:])
np.savetxt("selected.txt", xyz[sel,:]) #transposta dos dados


#LER NUVEM DE PONTOS
arquivo= "/home/feijo/Documentos/carvao_ufc/selected.txt" 
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


    ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
    plt.xlim([np.min(dados_y), np.max(dados_y)]) # limitando o espaço de plotar em y
    plt.ylim([np.min(dados_z), np.max(dados_z)]) # limitando o espaço de plotar em z
    plt.axis("off") # sem eixos 
    
    #Plotar arquivo .txt de cada slice
    fig.savefig('/home/feijo/Documentos/carvao_ufc/selecao_teste/fig_{}.png'.format(i))
    print(i) 

    points_slice = [(x,y,z) for x,y,z in zip(dados_x[i*intervalo: (i+1)*intervalo],dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]
    np.savetxt('/home/feijo/Documentos/carvao_ufc/selecao_teste/points_fig_{}.txt'.format(i), points_slice, delimiter=' ') 

    plt.close()


#identificar o numero de slices na path
folder = '/home/feijo/Documentos/carvao_ufc/selecao_teste' # path dos slices
filepaths = glob.glob(folder+ "/*.png", recursive= True)  
print (len(filepaths)) # Número de arquivos na path

total=0

for i in range(len(filepaths)):
    img = np.asarray(Image.open("/home/feijo/Documentos/carvao_ufc/selecao_teste/fig_{}.png".format(i)).convert('L'))
    img = 1 * (img < 255)
    m,n = img.shape
    total += img.sum() 
    print("{} white pixels, out of {} pixels in total.".format(img.sum(), m*n)) 
    
print("Número total de pixels {}".format(total))

somaslices = total
volumeareaporpixels= somaslices*0.005657 #relação pixels to m3 

print("Volume total = {} m³".format(volumeareaporpixels))


