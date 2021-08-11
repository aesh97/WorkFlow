import networkx as nx
import json

import networkx.algorithms.community as nx_comm
import csv
import igraph as ig
import leidenalg as la



#loads json data from specified file (make sure this is correct for your computer)
file = open('/Users/adam/Desktop/WorkFlow/newJsonData/116.json', "r")

data = json.loads(file.read())
file.close()

unwanted = []
for bill in data:


#when analyzing the house use "== 'Senate'" otherwise use "== 'House'"
    if (bill['originChamber'] == 'House'):
        unwanted.append(bill)



for i in range(len(unwanted)):
    data.remove(unwanted[i])

#the attributes the nodes need to have are specified by this function
def makeObj(obj):
    
    return {'ID':obj["ID"], 'name': obj["name"], 'state' :obj["state"]}


#sets a given nodes attributes
def setTitle(obj, R, D, I, nodes):
    index = findID(nodes, obj["ID"])
    name = obj["name"].split()
    if (index in R):
        

        nodes[index]["title"] = name[len(name)-1] + "(R-"+obj["state"]+")"
    elif(index in D):
        nodes[index]["title"] = name[len(name)-1] + "(D-"+obj["state"]+")"
    else:
        nodes[index]["title"] = name[len(name)-1] + "(I-"+obj["state"]+")"
        
        
    
    #calculates the modularity of a network with respect to attribute

def Modularity(G, attribute):

    #this list will contain each unique cluster ID after the for loop
    Clusters = []
    for i in range(len(G.nodes())):
        if (not(G.nodes()[i][attribute] in Clusters)):
            Clusters.append(G.nodes()[i][attribute])


#this dictionary will map cluster ID to a list of node IDs in the cluster
    NodePartition = {}


    for num in Clusters:
        NodePartition[num] = []

    for node in G.nodes():
        NodePartition[G.nodes()[node][attribute]].append(node)

#this is the iterable we will feed into the modularity function
    NodeList = []


    for key in NodePartition:
        AddArr = []
        for number in NodePartition[key]:
            AddArr.append(number)

        NodeList.append(AddArr)

    return(nx_comm.modularity(G, NodeList, weight = 'weight'))

#clusters the nodes by party
def makePartyClusters(G, R, D, I):
    party = {}

    
    for bill in data:
        if (bill['sponsor'] == []):
            continue
        else:
            SponsNode = makeObj(bill['sponsor'][0])
            SponsNode['chamber'] = bill['originChamber']
            try:

            #if the node has a list associated with it, add the bill party to it
                party[findID(G.nodes(),SponsNode["ID"])].append(bill['sponsor'][0]['party'])


               
                        
                        
            except:

                #otherwise associate a list with it
                party[findID(G.nodes(),SponsNode["ID"])] = [bill['sponsor'][0]['party']]
#do the same for cosponsors
            for co in bill['cosponors']:
                coNode = makeObj(co)
                coNode['chamber'] = bill['originChamber']
                try:
                    party[findID(G.nodes(),coNode["ID"])].append(co['party'])
                except:
                    party[findID(G.nodes(),coNode["ID"])] = [co['party']]
#now that the data is gathered, we analyze (necessary because of party switching)
    for key in party:

        #if a node was both a republican and a democrat during a congress cluster them with the independents
        #if a node was ever independent cluster them with independents
        if ((party[key].count('R') > 0 and party[key].count('D') > 0) or party[key].count('I') > 0):
            I.append(key)
#this means that they were only ever republican
        elif (party[key].count('R') > 0):
            R.append(key)
        else:
#the only other possibility is that they are a democrat
            D.append(key)
        
        
    print("done partitioning by party")
#finds if the network has a node with a given ID
def findID(nodes, ID):
   

    
   
    for i in range(len(nodes)):
        
        
        if (nodes[i]["ID"] == ID):
            return i
        
    return -1


            
#formats nodes so they can be assigned to the network
def makeTupleList(NodeList):
    tupleOut = []

    

    i = 0

    for element in NodeList:
        tupleOut.append((i, element))

        i= i+1
    return tupleOut

#despite the name this is the function that takes a network as an input and assigns the fowler weight accordingly
def makeRawWeight(G):
    
    for bill in data:
        if(bill['sponsor']==[]):
            continue
        else:

            SponsorNode = makeObj(bill['sponsor'][0])
            SponsorNode['chamber'] = bill['originChamber']

            SponsGraphIndex = findID(G.nodes(),SponsorNode["ID"])

            cosponsorsIndex = []

            for co in bill['cosponors']:
                CoNode = makeObj(co)
                CoNode['chamber'] = bill['originChamber']

                Index = findID(G.nodes(),CoNode["ID"])

                if ((Index in cosponsorsIndex) or co['withdrawn'] == True):
                    continue
                else:
                    cosponsorsIndex.append(Index)


            for coIndex in cosponsorsIndex:
                if (G.has_edge(coIndex, SponsGraphIndex)):
                    G[coIndex][SponsGraphIndex]['weight'] = G[coIndex][SponsGraphIndex]['weight'] + (1/len(cosponsorsIndex))
                else:
                    G.add_edge(coIndex,SponsGraphIndex, weight = (1/len(cosponsorsIndex)))
                    

    

        
    

def main():

    nodes = []
    


    #loops through each bill in data
    for bill in data:



      



       #if there isn't a sponors listed the bill is ignored, otherwise a node is created if it is necessary

        try:

           
            SponsObj = makeObj(bill['sponsor'][0])
            SponsObj['chamber'] = bill['originChamber']
            if (findID(nodes, SponsObj["ID"])==-1):
                nodes.append(SponsObj)
        except:
            continue
        
        
            
       
        

        

    



        
        #nodes are created for cosponsors if necessary

        for co in bill['cosponors']:
            if (co["withdrawn"] == True):
                continue
          
            CosponsObj = makeObj(co)
            CosponsObj['chamber'] = bill['originChamber']
            if (findID(nodes, CosponsObj["ID"])==-1):
                nodes.append(CosponsObj)
        
                
    print('done with  making nodes')

    
    G = nx.DiGraph()

 

    



    TupList = makeTupleList(nodes)

  
    

    

    
    G.add_nodes_from(TupList)

    

  

    #calls a function

    
    EdgeData = makeRawWeight(G)
    
       
    
    

    R = []
    D = []
    I = []
    makePartyClusters(G,R,D,I)
    part = [R, D, I]

    print('Party Modularity: ' + str(round(nx_comm.modularity(G, part),3))) 



    for i in range(len(G.nodes())):
        
        setTitle(G.nodes()[i], R, D, I, G.nodes())

    
    totalWeight = 0
    for node in G.nodes():
        weighted = 0
        
        for edge in nx.edges(G, node):
            weighted = weighted + G[edge[0]][edge[1]]['weight']

        totalWeight = totalWeight + weighted

    totalWeight = totalWeight / len(G.nodes())

    print('Mean weighted degree:' + str(round(totalWeight, 3)))
    print('Number of Nodes:' + str(len(G.nodes())))
        
            
            
    with open("/Users/adam/Desktop/WorkFlow/Geo/capitals.csv") as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            for i in range(len(G.nodes())):
                if G.nodes()[i]["state"] == row[3]:
                    G.nodes()[i]["Latitude"] = float(row[4])
                    G.nodes()[i]["Longitude"] = float(row[5])

    
    nx.write_graphml(G,"/Users/adam/Desktop/WorkFlow/fowlerData/Graph.graphml")
    
    J = ig.Graph().Read_GraphML('/Users/adam/Desktop/WorkFlow/fowlerData/Graph.graphml')
    partition2 = la.find_partition(J, la.ModularityVertexPartition, weights = 'weight')
    

    for i in range(len(partition2)):
        for j in range(len(partition2[i])):
            G.nodes()[partition2[i][j]]['LeidenCluster'] = i

    print('Leiden Modularity:' + str(round(Modularity(G, 'LeidenCluster'),3)))
    print('Leiden Groups:' + str(len(partition2)))


   

    
            
    nx.write_gexf(G, "fowerVis.gexf")

    



  

    
            
    
    

    
    

    

   
            
            
       
       
       



if __name__=="__main__":
    main()
