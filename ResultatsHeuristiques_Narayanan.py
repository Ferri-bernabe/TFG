import pickle #will be useful to open the database of transactions
from heuristics import Heuristics #class with the heuristics that we will use

with open("data/complet_tx_groundtruth_last_10000.PICKLE", 'rb') as f:
        dades = pickle.load(f)
temp = dades
HeuristicClass = Heuristics()

print("Executant adressTypeForTransaction...")
res = 0
intents = 0
for i in range(len(temp)):
    l = HeuristicClass.adressTypeForTransaction(temp[i][1])
    if l != "no":
        res += 1
    intents += 1
print("S'han detectat " + str(res) + " adreçes de canvi" + " de " + str(intents) + " intents")

print("Executant detectionUsingDecimalPlaces...")
res = 0
intents = 0
for i in range(len(temp)):
    l = HeuristicClass.detectionUsingDecimalPlaces(temp[i][1])
    if l != "no":
        res += 1
    intents += 1
print("S'han detectat " + str(res) + " adreçes de canvi" + " de " + str(intents) + " intents")

print("Executant exactPaymentAmmount...")
res = 0
intents = 0
for i in range(len(temp)):
    l = HeuristicClass.exactPaymentAmmount(temp[i][1])
    if l != "no":
        res += 1
    intents += 1
print("S'han detectat " + str(res) + " adreçes de canvi" + " de " + str(intents) + " intents")

print("Executant optimalChange...")
res = 0
intents = 0
for i in range(len(temp)):
    l = HeuristicClass.optimalChange(temp[i][1])
    if l != "no":
        res += 1
    intents += 1
print("S'han detectat " + str(res) + " adreçes de canvi" + " de " + str(intents) + " intents")

print("Executant bip69...")
res = 0
intents = 0
for i in range(len(temp)):
    l = HeuristicClass.bip69(temp[i][1])
    if l != "no bip69":
        res += 1
    intents += 1
print("S'han detectat " + str(res) + " transaccions amb bip69" + " de " + str(intents) + " intents")

print("Executant addressReuse...")
res = 0
intents = 0
for i in range(len(temp)):
    l = HeuristicClass.addressReuse(temp[i][1], temp)
    if l != "no":
        res += 1
    intents += 1
print("S'han detectat " + str(res) + " adreçes de canvi" + " de " + str(intents) + " intents")

print("Executant tresholdVote...")
res = 0
intents = 0
for i in range(len(temp)):
    l = HeuristicClass.tresholdVote(temp[i][1], temp)
    if l != "no":
        res += 1
    intents += 1
print("S'han detectat " + str(res) + " adreçes de canvi" + " de " + str(intents) + " intents")

print("Executant multipleInputsForAll... (pot trigar bastant)")
l = HeuristicClass.multipleInputsForAll(temp)
print("S'han detectat en total " + str(len(l)) + " clusters")

print("Executant clusterizando... (pot trigar bastant)")
l = HeuristicClass.clusterizando(temp)
for clust in l:
    if "1JVyMj5GY2dPqg92d9Cm9DzWJJxPiiCTtW" in clust:
        print("El cluster de 1JVyMj5GY2dPqg92d9Cm9DzWJJxPiiCTtW es: ")
        print(clust)
print("S'han detectat en total " + str(len(l)) + " clusters")