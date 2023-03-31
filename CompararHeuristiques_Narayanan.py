import pickle #will be useful to open the database of transactions
from heuristics import Heuristics #class with the heuristics that we will use
import comparar

with open("data/complet_tx_groundtruth_last_10000.PICKLE", 'rb') as f:
        dades = pickle.load(f)
temp = dades
HeuristicClass = Heuristics()

# Abre el archivo y lee las líneas
with open('data/change-ground-truth-last_10000.csv', 'r') as file:
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