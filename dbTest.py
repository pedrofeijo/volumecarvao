#!/usr/bin/python3
import requests
import json

## Sobe nuvem txt no DB
# headers = {'md5hash':'a0b9e00682ae9df6f3bd5968e5ad473c','user':'1'}
# files = {'file': ('pontos_raw.txt', open('pontos_raw.txt', 'rb'), 'text/plain')}
# r = requests.post('http://localhost:8503/pointCloudData', headers=headers, files=files)

## Verifica nuvem txt no DB
# payload = {"responseType":"fieldList","initDate":"2000-09-10 00:00:00","endDate":"2100-09-10 23:59:59"}
# r = requests.get('http://localhost:8503/pointCloudData', params=payload)

## Baixa nuvem raw txt do DB
# payload = {"responseType":"pcdFile","id":"39","pcdType":"raw"}
# r = requests.get('http://localhost:8503/pointCloudData', params=payload)
# headerData = json.dumps(dict(r.headers))
# headerData = json.loads(headerData)
# fileName = headerData["Content-Disposition"].split("=")[1] 
# with open(fileName, 'wb') as fd:
#     for chunk in r.iter_content(chunk_size=128):
#         fd.write(chunk)

payload = {"responseType":"pcdFile","id":"38","pcdType":"segmented"}
r = requests.get('http://localhost:8503/pointCloudData', params=payload)
headerData = json.dumps(dict(r.headers))
headerData = json.loads(headerData)
fileName = headerData["Content-Disposition"].split("=")[1] 
# fileName = "/your/own/path/"+headerData["Content-Disposition"].split("=")[1] 

with open(fileName, 'wb') as fd:
    for chunk in r.iter_content(chunk_size=128):
        fd.write(chunk)

## Apaga nuvem raw 38
# payload = {"id":"38"}
# r = requests.delete('http://localhost:8503/pointCloudData', params=payload)

## Cria/atualiza um arquivo segmentado
# headers = {
#     'stp_mass':  '{"stp_1a":0, "stp_1b":0, "stp_2a":0, "stp_2b":0, "stp_2c":0, "stp_2d":0, "stp_3a":100, "stp_3b":0}',
#     'stp_volume':'{"stp_1a":0, "stp_1b":0, "stp_2a":0, "stp_2b":0, "stp_2c":0, "stp_2d":0, "stp_3a":200, "stp_3b":0}',
#     'md5hash':'0c7be3fb075968511da35bc547c904aa',
#     'user':'1',
#     'id':'38',
#     'logistics':'TCLD',
#     'method':'SAVAut',
#     'type':'entrada'
# }
# files = {'file': ('pontos_seg.txt', open('pontos_seg.txt', 'rb'), 'text/plain')}
# r = requests.put('http://localhost:8503/pointCloudData', headers=headers, files=files)

print(r.text)