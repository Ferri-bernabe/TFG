import decimal

class Heuristics:
    def __init__(self):
        r = []

    def multipleInputsForUser(self,user_address, transactions_list):
        user_cluster_list = [] #this will be the addresses linked to the user cluster
        #searching all the direct addresses that share transaction with user_address
        user_cluster_list.append(user_address)
        for transaction in transactions_list:
            for i, inputs in enumerate(transaction):
                if i % 2 == 0: # si el índice es divisible entre 2
                    for inputt in inputs:
                        if user_address in inputt:
                            for i in range(0,len(inputs)):
                                if inputs[i][0] not in user_cluster_list:
                                    user_cluster_list.append(inputs[i][0])
        
        #searching all the indirect addresses that share transaction with a shared adress with user_address
        for transaction in transactions_list:
            for i, inputs in enumerate(transaction):
                if i % 2 == 0: # si el índice es divisible entre 2 (inputs]
                    for i in range(0,len(inputs)):
                        for clustered_input in user_cluster_list:
                            if clustered_input == inputs[i][0]:
                                for j in range(0, len(inputs)):
                                    if inputs[j][0] not in user_cluster_list:
                                        user_cluster_list.append(inputs[j][0])
        
        return user_cluster_list
    
    def multipleInputsForUserImproved(self, user_address, transactions_list):
        user_cluster_list = []
        temp_list = {}
        user_cluster_list.append(user_address)
        temp_list[user_address] = False
        
        trobat = False
        while trobat == False:
            temp_list2 = temp_list.copy()
            for x in temp_list.keys():
                for transaction in transactions_list:
                    for i, inputs in enumerate(transaction):
                        if i % 2 == 0: # si el índice es divisible entre 2
                            for inputt in inputs:
                                if x in inputt:
                                    for i in range(0,len(inputs)):
                                        if inputs[i][0] not in user_cluster_list:
                                            user_cluster_list.append(inputs[i][0])
                                            temp_list2[inputs[i][0]] = False
                temp_list2[x] = True                                
            
            temp_list = temp_list2.copy()
            trobat2 = True
            for y in temp_list2.values():
                if y == False:
                    trobat2 = False
                    trobat = False
            if trobat2:
                trobat = True
        return user_cluster_list
        
    
    def multipleInputsForAll(self, transactions_list):
        '''
        all_cluster_list = [] #this will be the list with all the clustered addresses
        inputs_seen = [] # set to keep track of inputs that have been added to a cluster
        #idea
        #1. Per a cada adreça que no estigui en la llista all_cluster_list, aplicar-li el multipleInputsForUser i afegir-la
        counter = 0
        for transaction in transactions_list:
            for i, inputs in enumerate(transaction):
                trobat = False
                if i % 2 == 0: # si el índice es divisible entre 2
                    for j in range(0, len(inputs)):
                        if inputs[j][0] not in inputs_seen:
                            if trobat == False:
                                l = self.multipleInputsForUser(inputs[j][0], transactions_list)
                                all_cluster_list.append(l)
                                for L in l:
                                    inputs_seen.append(L)
                                trobat = True
        return all_cluster_list
        '''
        all_cluster_list = []
        
        for transaction in transactions_list:
            for i,inputs in enumerate(transaction):
                if i % 2 == 0:
                    trobat = False
                    for j in range(0, len(inputs)):
                        for z in range(0, len(all_cluster_list)):
                            if inputs[j][0] in all_cluster_list[z]:
                                trobat = True
                                break
                        if trobat:
                            break
                    if trobat == False:
                        l = self.multipleInputsForUser(inputs[0][0], transactions_list)
                        all_cluster_list.append(l)
        return all_cluster_list

    
    
    
    def adressTypeForTransaction(self, transaction):
        #mirem que tots els inputs siguin del mateix tipus
        if len(transaction) == 0:
            return "no"
        
        trobat = False
        primer = ""
        counter = 0
        for i,inputs in enumerate(transaction):
            if i % 2 == 0:
                for inputt in inputs:
                    if counter == 0:
                        counter += 1
                        if inputt[0][0] == 'b':
                            primer = str(inputt[0][:4])
                        else:
                            primer = str(inputt[0][0])
                    else:
                        if primer[0] == 'b':
                            if primer != inputt[0][:4]:
                                trobat = True
                        else:
                            if primer != str(inputt[0][0]):
                                trobat = True
        if trobat == True:
            return "no"
        else:
            #si tots els inputs son del mateix tipus, hem de mirar que només hi hagi un output del mateix tipus
            counter = 0
            last_same_type_output = ""
            for i,outputs in enumerate(transaction):
                if i%2 != 0:
                    for output in outputs:
                        if primer[0] == 'b':
                            if primer == output[0][:4]:
                                counter += 1
                                last_same_type_output = output[0]
                        else:
                            if primer == str(output[0][0]):
                                counter += 1
                                last_same_type_output = output[0]
        if counter == 1:
            return last_same_type_output
        else:
            return "no"

    def find_decimals(self,value):
        return (abs(decimal.Decimal(str(value)).as_tuple().exponent))
    
    def detectionUsingDecimalPlaces(self, transaction):
        #treshold => if an output has 2 decimals or less it's considered an option for being the user's output. Then the 
        #(treshold will be of 2 decimals more at least)?????.
        
        #1.Look if 1 output has 2 decimal or less, if the list is > 1 then return "no"
        temp = []
        for i,outputs in enumerate(transaction):
            if i%2 != 0:
                for outputt in outputs:
                    if self.find_decimals(outputt[1]) <= 2:
                        temp.append(outputt)
        if (len(temp) > 1 or len(temp) == 0):
            return "no"
        else:
            return temp[0][0]
        
    def exactPaymentAmmount(self, transaction):
        #if there is 1 output only, the output will be linked to the user
        for i,outputs in enumerate(transaction):
            if i%2 != 0:
                if len(outputs) != 1:
                    return "no"
                else:
                    return outputs[0][0]
    
    def addressReuse(self, transaction, transactions_list):
        #the idea is that if the outputs have been reused except 1, the 1 is the change, because wallets usually generates new addresses
        #for the change addresses
        
        reused_list = []
        total_outputs = 0
        #1.Look if there's only 1 address that is not reused
        for i,outputs in enumerate(transaction):
            if i%2 != 0:
                for output in outputs:
                    total_outputs += 1
                    counter = 0
                    trobat = False
                    while(trobat == False):
                        for transactions in transactions_list:
                            if transaction == transactions:
                                trobat = True
                                break
                            for i,outputts in enumerate(transactions):
                                if i%2 != 0:
                                    for outputt in outputts:
                                        if output[0] == outputt[0]:
                                            counter += 1
                    if counter >= 1:
                        reused_list.append(output[0])
        if (total_outputs - len(reused_list)) == 1:
            for i,outputs in enumerate(transaction):
                if i%2 != 0:
                    for output in outputs:
                        if output[0] not in reused_list:
                            return output[0]
        else:
            return "no"
        
    def optimalChange(self, transaction):
        #conditions
        # 2+ inputs
        # 1 output < 1 inputs
        total_inputs = 0
        for i,inputs in enumerate(transaction):
            if i % 2 == 0:
                for inputt in inputs:
                    total_inputs += 1
        if total_inputs < 2:
            return "no"
            
        candidates = []
        for i,outputs in enumerate(transaction):
            if i%2 != 0:
                for output in outputs:
                    trobat = False
                    for i,inputs in enumerate(transaction):
                        if i%2 == 0:
                            for inputt in inputs:
                                if trobat == False:
                                    if output[1] < inputt[1]:
                                        trobat = True
                                        candidates.append(output[0])
        if len(candidates) == 1:
            return candidates[0]
        else:
            return "no"
        
    def tresholdVote(self, transaction, transactions_list):
        treshold = 0.2
        dict_options = {}
        res = self.adressTypeForTransaction(transaction)
        if res != "no":
            if res not in dict_options:
                dict_options[res] = 0.25
            else:
                dict_options[res] += 0.25
        
        
        res = self.detectionUsingDecimalPlaces(transaction)
        if res != "no":
            if res not in dict_options:
                dict_options[res] = 0.25
            else:
                dict_options[res] += 0.25
        
        
        res = self.exactPaymentAmmount(transaction)
        if res == "no":
            res = self.optimalChange(transaction)
        if res != "no":
            if res not in dict_options:
                dict_options[res] = 0.25
            else:
                dict_options[res] += 0.25
                
        
        res = self.addressReuse(transaction, transactions_list)
        if res != "no":
            if res not in dict_options:
                dict_options[res] = 0.25
            else:
                dict_options[res] += 0.25
                
        res = []
        for x in dict_options.keys():
            if dict_options[x] > treshold:
                res.append(x)
        
        if (len(res) == 1):
            return res[0]
        else:
            return "no"
        
    def clusterizando(self, transactions_list):
        users_cluster_list = []
        for transaction in transactions_list:
            for i, inputs_outputs in enumerate(transaction):
                temp = ""
                if i % 2 == 0: # si el índice es divisible entre 2
                    for inputt in inputs_outputs:
                        #we look if inputt[0] is already in any cluster
                        trobat = False
                        for cluster in users_cluster_list:
                            if inputt[0] in cluster:
                                trobat = True
                                temp = cluster
                        if trobat == False:
                            users_cluster_list.append(self. multipleInputsForUserImproved(inputs_outputs[i][0], transactions_list))        
                            
                    res = self.tresholdVote(transaction, transactions_list)
                    if res != "no":
                        if temp != "":
                            for cluster in users_cluster_list:
                                if temp[0] == cluster[0]:
                                    cluster.append(res)
                        else:
                            users_cluster_list[len(users_cluster_list)-1].append(res)
                                    
        return users_cluster_list
                        
                    