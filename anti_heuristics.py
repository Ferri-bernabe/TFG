import decimal
import bitcoin_core_rpc

class AntiHeuristics:
    def __init__(self, wallet):
        r = []
        self.originWalletLabel = wallet

    def defensa1AddressType(self,trans, destination_address):
        imposible = False
        #afegir un input de diferent tipus del que hi ha
        temp = trans[1]
        amount_a_sumar = 0
        #1.Mirar quins inputs tinc per gastar
        inputs = bitcoin_core_rpc.rpc_wallet_call("listunspent", {}, self.originWalletLabel)
        
        #2. Mirar en la transaccó de quins tipus son els inputs (han de ser del mateix tipus per obligació)
        startBy = ""
        for i,inputss in enumerate(temp):
            if i%2 == 0:
                for inputt in inputss:
                    if inputt[0][0] != "b":
                        startBy = inputt[0][0]
                    else:
                        startBy = inputt[0][:4]
        #3. Agafar algún input que no estigui ya en la transacció de diferent tipus
        if len(inputs['result']) == 0:
            #vol dir que no hi ha inputs per gastar
            imposible = True
        else:
            #vol dir que hi ha inputs per gastar
            res = []
            trobat = False
            for inputsGastar in inputs['result']:
                #nomes s'ha de mirar que sigui de diferent tipus ja que no estarà en la trans mai si es de diferent tipus
                if trobat == False:
                    if inputsGastar['address'][0] != "b":
                        if inputsGastar['address'][0] != startBy:
                            res = [inputsGastar['address'], inputsGastar['amount']]
                            trobat = True
                            break
                    else:
                        if inputsGastar['address'][:4] != startBy:
                            res = [inputsGastar['address'], inputsGastar['amount']]
                            trobat = True
                            break
            if trobat == False:
                imposible = True
            else:
                if imposible == False:
                    trans[1][0].append(res)
                    amount_a_sumar += res[1]
        for i, outputss in enumerate(trans[1]):
            if i % 2 != 0:
                for outputt in outputss:
                    if outputt[0] != destination_address:
                        outputt[1] += amount_a_sumar
                        break
        if imposible == True:
            print("Impossible defensar aquesta transacció")

        return trans
    
    def defensa2AddressType(self, trans, destination_address, destination_wallet_label, destination_address_type):
        #el usuari ens dona una altra adreça del mateix tipus per a fer el pagament
        new_destination_address = bitcoin_core_rpc.get_new_address(destination_wallet_label, destination_address_type, label='')

        #buscar la destination_address i treure-li "algo"
        canvi = 0
        trobat = False
        for i,outputss in enumerate(trans[1]):
            if i % 2 != 0:
                for outputt in outputss:
                    if outputt[0] == destination_address:
                        trobat = True
                        canvi = 0.5 * outputt[1]
                        outputt[1] -= canvi
                        break
        if trobat == True:
            res = [new_destination_address, canvi]
            trans[1][1].append(res)
        return trans

    def defensa1DetectionUsingDecimalPlaces(self, trans, destination_address):
        #la idea es pagar 0.00000001 de més ja que així li afegim decimals
        cantitat_extra = 0.00000001
        input_amount = 0

        #1.Afegim un input per a poder afegir-li la cantitat extra a la direcció de destí
        inputs = bitcoin_core_rpc.rpc_wallet_call("listunspent", {}, self.originWalletLabel)
        imposible = False

        if len(inputs['result']) == 0:
            imposible = True
        trobat = True
    
        if trobat == True:
            #2.Li afegim a la destination_address la cantitat extra
            for i,outputss in enumerate(trans[1]):
                if i % 2 != 0:
                    for outputt in outputss:
                        if outputt[0] == destination_address:
                            outputt[1] += cantitat_extra
                            break

            #3. Li posem la cantitat sobrant (input - cantitat_extra) a la direcció de canvi
            for i,outputss in enumerate(trans[1]):
                if i % 2 != 0:
                    for outputt in outputss:
                        if outputt[0] != destination_address:
                            outputt[1] += (input_amount - cantitat_extra)
        else:
            imposible = True
        
        if imposible == True:
            print("Impossible defensar aquesta transacció")

        return trans
    
    def find_decimals(self,value):
        return (abs(decimal.Decimal(str(value)).as_tuple().exponent))
    
    def defensa2DetectionUsingDecimalPlaces(self, trans, destination_address, destination_wallet_label, destination_address_type):
        #el usuari ens dona una altra adreça del mateix tipus per a fer el pagament
        new_destination_address = bitcoin_core_rpc.get_new_address(destination_wallet_label, destination_address_type, label='')

        #li treiem la meitat a la dest_address
        amount_a_sumar = 0
        for outputt in trans[1][1]:
            if outputt[0] == destination_address:
                amount_a_sumar = outputt[1] * 0.5
                outputt[1] = outputt[1] * 0.5
        
        #afegim la new_dest als outputs
        res = [new_destination_address, amount_a_sumar]
        trans[1][1].append(res)

        #mirem que les 2 adreces tinguin més de 2 decimals, sino, afegim 0,00000001 a l'adreça que no en tingui
        trobat = False
        direccion_con_decimales = ""
        for outputt in trans[1][1]:
            if self.find_decimals(outputt[1]) <= 2:
                trobat = True
                outputt[1] += 0.00000001
                direccion_con_decimales = outputt[0]
                break
        
        #li treiem 0.00000001 a l'altra adreça
        if trobat == True:
            for outputt in trans[1][1]:
                if self.find_decimals(outputt[1]) >= 2 and outputt[0] != direccion_con_decimales:
                    trobat = True
                    outputt[1] -= 0.00000001
                    break
        return trans
    
    def defensa1ExactPaymentAmmount(self,trans, destination_address):
        #la idea es afegir 1 input més i 1 output de retorn
        imposible = False
        temp = trans[1]
        amount_a_sumar = 0

        #mirar quins inputs tinc per gastar
        inputs = bitcoin_core_rpc.rpc_wallet_call("listunspent", {}, self.originWalletLabel)

        if len(inputs['result']) == 0:
            #vol dir que no hi ha inputs per gastar
            imposible = True
        else:
            #vol dir que hi ha inputs per gastar
            res = []

            #s'ha de mirar que no estigui la adreça a posar en la transacció
            trobat = False
            vegades_input_afegit = 0
            for inputsGastar in inputs['result']:
                trobat2 = False
                i = 0
                while(trobat2 == False and i < len(trans[1][0])):
                    if inputsGastar['address'] == str(trans[1][0][i][0]):
                        trobat2 = True
                        break
                    i += 1
                if trobat2 == False:
                    if vegades_input_afegit == 0:
                        res = [inputsGastar['address'], inputsGastar['amount']]
                        #trans[1][0].append(res)
                        vegades_input_afegit += 1
                        trobat = True
                        break
            if trobat == False:
                imposible = True
                    
            if imposible == False:
                trans[1][0].append(res)
                amount_a_sumar += res[1]

            #afegir un altre output de retorn
            return_address = bitcoin_core_rpc.get_new_address(self.originWalletLabel, "legacy", label='')
            res = [return_address, 0]
            trans[1][1].append(res)

            for i, outputss in enumerate(trans[1]):
                if i % 2 != 0:
                    for outputt in outputss:
                        if outputt[0] != destination_address:
                            outputt[1] += amount_a_sumar
                            break
            
            if imposible == True:
                print("Impossible defensar aquesta transacció")

            return trans

    def defensa2ExactPaymentAmmount(self, trans, destination_address, destination_wallet_label, destination_address_type):
        #la idea es pagar la meitat que s'hagi de pagar a cada direcció, tenint en compte que l'usuari ens dona una altra direcció per pagar-li allà
        new_destination_address = bitcoin_core_rpc.get_new_address(destination_wallet_label, destination_address_type, label='')

        trobat = False
        canvi = 0
        for i,outputss in enumerate(trans[1]):
            if i % 2 != 0:
                for outputt in outputss:
                    if outputt[0] == destination_address:
                        trobat = True
                        canvi = outputt[1] * 0.5
                        outputt[1] -= canvi
                        break
        if trobat == True:
            res = [new_destination_address, canvi]
            trans[1][1].append(res)
        return trans 

    def defensa1OptimalChange(self, trans, destination_address):
        #la idea es afegir inputs fins que el valor de retorn sigui > que tots els inputs
        imposible = False
        temp = trans[1]
        amount_a_sumar = 0

        #mirar quins inputs tinc per gastar
        inputs = bitcoin_core_rpc.rpc_wallet_call("listunspent", {}, self.originWalletLabel)
        if len(inputs['result']) == 0:
            print("imposible")
            #vol dir que no hi ha inputs per gastar
            imposible = True

        #mirar quin es l'output que es més petit que algún dels inputs i agafar-lo
        output_canvi_heur = 0
        for i,outputss in enumerate(temp):
            if i % 2 != 0:
                trobat = False
                for outputt in outputss:
                    for j,inputss in enumerate(temp):
                        if j % 2 == 0:
                            for inputt in inputss:
                                if outputt[1] < inputt[1]:
                                    if trobat == False:
                                        trobat = True
                                        output_canvi_heur = outputt[1]
                                        break
        #encontrar el input más grande
        input_mes_gran = 0
        for i,inputss in enumerate(temp):
            if i % 2 == 0:
                for inputt in inputss:
                    if inputt[1] > input_mes_gran:
                        input_mes_gran = inputt[1]
        
        # añadir inputs hasta que el valor de output_canvi_heur sea más grande que el input más grande
        trobat = False
        pseudotrans = trans[:]

        #s'ha de mirar que no estigui la adreça a posar en la transacció
        trobat = False
        for inputsGastar in inputs['result']:
            trobat2 = False
            i = 0
            while(trobat2 == False and i < len(trans[1][0])):
                if inputsGastar['address'] == str(trans[1][0][i][0]):
                    trobat2 = True
                    break
                i += 1
            if trobat2 == False: 
                res = [inputsGastar['address'], inputsGastar['amount']]
                pseudotrans[1][0].append(res)
                amount_a_sumar += res[1]
                output_canvi_heur += res[1]
                if output_canvi_heur > input_mes_gran:
                    trobat = True
                    break
        if trobat == False:
            imposible = True
        if imposible == False:
            trans = pseudotrans[:]

        for i, outputss in enumerate(trans[1]):
                if i % 2 != 0:
                    for outputt in outputss:
                        if outputt[0] != destination_address:
                            outputt[1] += amount_a_sumar
                            break
        
        if imposible == True:
            print("Impossible defensar aquesta transacció")

        return trans
    
    def defensa2OptimalChange(self, trans, destination_address, destination_wallet_label, destination_address_type):
        #la idea del optimal change es que 1 unic output < algun input, per tant, la idea es fer un pagament a l'usuari en 2 adreces, on 1 sigui < que algun input
        #1. Nova adreça
        new_destination_address = bitcoin_core_rpc.get_new_address(destination_wallet_label, destination_address_type, label='')
        cantitat_extra = 0.00000001
        imposible = False

        #2. Buscar un valor que sigui cantitat_extra = 0.00000001 < que un input qualsevol
        trobat = False
        valor_new_address = 0
        for i,inputss in enumerate(trans[1]):
            if i % 2 == 0:
                for inputt in inputss:
                    if inputt[1] - cantitat_extra > 0:
                        trobat = True
                        valor_new_address = inputt[1] - cantitat_extra
        if trobat == False:
            imposible = True
        else:
            #Buscar en els outputs la destination_address i restar-li valor_new_address
            for i,outputss in enumerate(trans[1]):
                if i % 2 != 0:
                    for outputt in outputss:
                        if outputt[0] == destination_address:
                            outputt[1] -= valor_new_address
                            break
            res = [new_destination_address, valor_new_address]

            trans[1][1].append(res)
        
        if imposible == True:
            print("Impossible defensar aquesta transacció")
        
        return trans
    
    def defensaBip69(self, trans):
         #la idea es ordenar els inputs i outputs segons el bip69
        temp = trans[1]
        #separamos los inputs y los outputs
        inputss = temp[0]
        outputss = temp[1]

        #ordenamos primero los inputs según las direcciones
        inputs_final = []
        while (len(inputss) > 0):
            mes_petit = inputss[0][0]
            posicio = 0
            for i,inputt in enumerate(inputss):
                if inputt[0] < mes_petit:
                    mes_petit = inputt[0]
                    posicio = i
                else:
                    if inputt[0] == mes_petit:
                        if inputt[1] < inputss[posicio][1]:
                            mes_petit = inputt[0]
                            posicio = i
            res = [inputss[posicio][0], inputss[posicio][1]]
            inputs_final.append(res)
            inputss.pop(posicio)

        #ordenamos segundo los outputs según los valores
        outputs_final = []
        while (len(outputss) > 0):
            mes_petit = outputss[0][1]
            posicio = 0
            for i,outputt in enumerate(outputss):
                if outputt[1] < mes_petit:
                    mes_petit = outputt[1]
                    posicio = i
                else:
                    if outputt[1] == mes_petit:
                        if outputt[0] < outputss[posicio][0]:
                            mes_petit = outputt[1]
                            posicio = i
            res = [outputss[posicio][0], outputss[posicio][1]]
            outputs_final.append(res)
            outputss.pop(posicio)
        
        trans_final = [trans[0], [inputs_final, outputs_final]]
        return trans_final

            

