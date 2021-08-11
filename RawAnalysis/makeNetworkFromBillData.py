import networkx as nx
import json
import community as community_louvain
import networkx.algorithms.community as nx_comm
import csv
import igraph as ig
import leidenalg as la



#loads json data from specified file
file = open('/Users/adam/Desktop/WorkFlow/newJsonData/108.json', "r")

data = json.loads(file.read())
file.close()

unwanted = []
for bill in data:


#when analyzing the house use "== 'Senate'" otherwise use "== 'House'"
    if (bill['originChamber'] == 'House'):
        unwanted.append(bill)



for i in range(len(unwanted)):
    data.remove(unwanted[i])


def makeObj(obj):
    
    return {'ID':obj["ID"], 'name': obj["name"], 'state' :obj["state"]}

def setTitle(obj, R, D, I, nodes):
    index = findID(nodes, obj["ID"])
    name = obj["name"].split()
    if (index in R):
        

        nodes[index]["title"] = name[len(name)-1] + "(R-"+obj["state"]+")"
    elif(index in D):
        nodes[index]["title"] = name[len(name)-1] + "(D-"+obj["state"]+")"
    else:
        nodes[index]["title"] = name[len(name)-1] + "(I-"+obj["state"]+")"
        
        
    
    

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
                party[findNode(SponsNode, G.nodes())].append(bill['sponsor'][0]['party'])


               
                        
                        
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

def findID(nodes, ID):
   

    
   
    for i in range(len(nodes)):
        
        
        if (nodes[i]["ID"] == ID):
            return i
        
    return -1


            

def makeTupleList(NodeList):
    tupleOut = []

    

    i = 0

    for element in NodeList:
        tupleOut.append((i, element))

        i= i+1
    return tupleOut

def makeRawWeight(nodes):
    
    relations = {}


    #loops though each bill in the data
    for bill in data:
       

        
        #the list of nodes involved in the bill
        involved = []

        #populating that list, making sure no duplicates appear
        try:
            Spons = makeObj(bill['sponsor'][0])
            Spons['chamber'] = bill['originChamber']

            involved.append(Spons)
        except:
            continue
        for co in bill['cosponors']:
            Cosp = makeObj(co)
            Cosp['chamber'] = bill['originChamber']

            if (co["withdrawn"] == False and findID(involved, Cosp["ID"]) == -1):
               

            
                involved.append(Cosp)
        #list of IDs of each node invovled
        indexInvolved = []


        for node in involved:
            location = findID(nodes,node["ID"])
            if (location == -1):
                print('weird')
            else:
                
            
                indexInvolved.append(location)

        for i in range(len(indexInvolved)):
            for j in range(len(indexInvolved)):

                if (i != j):

                    try:
                        relations[indexInvolved[i]].append(indexInvolved[j])

                        
                        
                        
                    except:
                        relations[indexInvolved[i]]=[indexInvolved[j]]

                    
                
                
                        
  
                
                            
            
                             
                             

    
        


    print('done making edges')
    return relations

        
    

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

    
    G = nx.Graph()

 

    



    TupList = makeTupleList(nodes)

  
    

    

    
    G.add_nodes_from(TupList)

    

  

    #calls a function

    
    EdgeData = makeRawWeight(nodes)
    for key in EdgeData:
        
       
       
        

        connects = EdgeData[key]
        connects.sort()

        minim = -1
        for num in connects:
            if (num > minim):
                
                G.add_edge(key, num, weight = connects.count(num))
                minim = num
       
    
    

    R = []
    D = []
    I = []
    makePartyClusters(G,R,D,I)
    part = [R, D, I]

    print('Party Modularity: ' + str(round(nx_comm.modularity(G, part),3))) 



    for i in range(len(G.nodes())):
        
        setTitle(G.nodes()[i], R, D, I, G.nodes())

    partition = community_louvain.best_partition(G)
    comms = []
    for key in partition:
        if (not(partition[key] in comms)):
            comms.append(partition[key])
            
        G.nodes()[key]['cluster'] = partition[key]
    print('Louvain Modularity: ' + str(round(Modularity(G, 'cluster'),3)))
    print('Number of Communities: ' + str(len(comms)))
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

    subCommunity = 0
    for community in comms:
        

        H = nx.Graph(G)
        subComms = []
        
        for node in G.nodes():
            
            if (H.nodes()[node]['cluster'] != community):
                H.remove_node(node)
        
        subPart = community_louvain.best_partition(H)
        for key in subPart:
            if (not(subPart[key] in subComms)):
                subComms.append(subPart[key])
            G.nodes()[key]['SubClust'] = subCommunity + subPart[key]
        subCommunity = subCommunity + len(subComms)+1
                    

    print("Modularity after subclustering Louvain:" + str(round(Modularity(G,'SubClust'),3)))
    nx.write_graphml(G,"/Users/adam/Desktop/WorkFlow/RawAnalysis/Graph.graphml")
    
    J = ig.Graph().Read_GraphML('/Users/adam/Desktop/WorkFlow/RawAnalysis/Graph.graphml')
    partition2 = la.find_partition(J, la.ModularityVertexPartition, weights = 'weight')
    

    for i in range(len(partition2)):
        for j in range(len(partition2[i])):
            G.nodes()[partition2[i][j]]['LeidenCluster'] = i

    print('Leiden Modularity:' + str(round(Modularity(G, 'LeidenCluster'),3)))
    print('Leiden Groups:' + str(len(partition2)))


   

    
            
    nx.write_gexf(G, "108Visualization.gexf")

    



  

    
            
    
    

    
    

    

   
            
            
       
       
       



if __name__=="__main__":
    main()
