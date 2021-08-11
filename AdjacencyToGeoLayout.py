import json
import pandas as pd
import networkx as nx
import networkx.algorithms.community as nx_comm
import community as community_louvain
import numpy as np
import csv

def setTitle(obj, party, name, state):
    check = name.split()
    obj['title'] = check[len(check)-1] + "("+party+"-"+state+")"
Map = {}
file = open('/Users/adam/Desktop/WorkFlow/newJsonData/116.json')
data = json.loads(file.read())
file.close()
#loops through the bills skipping ones passed by the house (can easily be changed to filter out senate or nothing at all)
for bill in data:
    
    if (bill['sponsor'] == [] or bill['originChamber'] == 'House'):
        continue
    else:
        Map[bill['sponsor'][0]['ID']] = {'name': bill['sponsor'][0]['name'], 'state': bill['sponsor'][0]['state'], 'party':  bill['sponsor'][0]['party']}
        
        for co in bill['cosponors']:
            Map[co['ID']] = {'name': co['name'], 'state': co['state'], 'party': co['party']}
           

#this is the file that contains the SDMS adjacency matrix
matrixFile = '/Users/adam/Desktop/sdsm_S116.csv'
IDs = pd.read_csv(matrixFile).head()



IdList = []
count = 0 
for col in IDs.columns:
    if (count == 0):
        count += 1
        continue
    
    IdList.append(col)
    

matrix = np.loadtxt(open(matrixFile, 'rb'), delimiter = ",",skiprows = 1,usecols =  tuple(range(1,len(Map)+1)))

#the matrix is converted to np.matrix and then in to a network



G = nx.from_numpy_matrix(matrix)


#then the attributes will be added using the Map dictionary

for i in range(len(G.nodes())):
    G.nodes()[i]['ID'] = IdList[i]
    

    G.nodes()[i]['name'] = Map[G.nodes()[i]['ID']]['name']
    G.nodes()[i]['state'] = Map[G.nodes()[i]['ID']]['state']
    G.nodes()[i]['party'] = Map[G.nodes()[i]['ID']]['party']

#Geo information is added next
with open("/Users/adam/Desktop/WorkFlow/Geo/capitals.csv") as file:
    reader = csv.reader(file, delimiter=',')
    for row in reader:
        for i in range(len(G.nodes())):
            if G.nodes()[i]["state"] == row[3]:
                G.nodes()[i]["Latitude"] = float(row[4])
                G.nodes()[i]["Longitude"] = float(row[5])

for node in G.nodes():
    setTitle(G.nodes()[node], G.nodes()[node]['party'], G.nodes()[node]['name'], G.nodes()[node]['state'])
    
nx.write_gexf(G, "SDSMVis.gexf")

    






    
    
