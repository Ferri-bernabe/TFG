def compararListas(lista_res, cluster):
    acertats = 0
    intents = 0

    for res in lista_res:
        for opcio in cluster:
            if res[0] == opcio[0]:
                if res[1] == opcio[1]:
                    acertats += 1 
                intents += 1
    
    print("S'han encertat " + str(acertats) + " de " + str(intents) + " intents. ")
    print("La mida de la llista es de " + str(len(lista_res)))
