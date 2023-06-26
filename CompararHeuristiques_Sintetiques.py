import pickle #will be useful to open the database of transactions
from heuristics import Heuristics #class with the heuristics that we will use
import comparar

with open("data_synthetic/complet_tx_synthetic_data.PICKLE", 'rb') as f:
        dades = pickle.load(f)
temp = dades
HeuristicClass = Heuristics()
dades2 = []
for trans in temp:
    temporal = [trans[0], list(trans[1:])]
    dades2.append(temporal)
temp = dades2

with open('data_synthetic/change_ground_truth_synthetic_data.csv', 'r') as file:
    lineas = file.readlines()

# Separa los valores en cada línea y conviértelos en una lista de tuplas
lista_completa = [list(linea.strip().split(',')) for linea in lineas]

print("Executant AdressTypeClustering...")
cluster = HeuristicClass.addressTypeCluster(temp)
comparar.compararListas(lista_completa, cluster)

print("Executant DetectionUsingDecimalPlacesClustering...")
cluster = HeuristicClass.detectionUsingDecimalPlacesCluster(temp)
comparar.compararListas(lista_completa, cluster)

print("Executant OptimalChangeClustering...")
cluster = HeuristicClass.optimalChangeCluster(temp)
comparar.compararListas(lista_completa, cluster)

print("Executant TresholdVoteCluster...")
cluster = HeuristicClass.tresholdVoteCluster(temp)
comparar.compararListas(lista_completa, cluster)