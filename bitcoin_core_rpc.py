#!/usr/bin/env python

import json
import requests
from heuristics import Heuristics
from anti_heuristics import AntiHeuristics

"""
How to set Bitcoin Core in regtest, explained here: 
https://bisq.network/blog/how-to-set-up-bitcoin-regtest/

Short description:
Include the following lines in the bitcoin.conf file.

regtest = 1
server=1
txindex=1
rpcuser=bitcoin
rpcpassword=bitcoin
rpcallowip=0.0.0.0/0
rpcconnect=127.0.0.1
# Options only for regtest
[regtest]
rpcport=3133

The bitcoin.conf file in a mac can be found in
/Users/user_name/Library/Application Support/Bitcoin

"""
rpc_user = 'bitcoin'
rpc_password = 'bitcoin'
rpc_port = '3133'  # testnet 18332   mainnet 8332  regtest 3133

def rpc_general_call(method, params):
    """
    rpc call to a bitcoin core wallet running as a localhost. This general call does not interact with a specific wallet
    of the bitcoin core so no need to inform the wallet label
    :param method: the rpc_call instruction (see bitcoin-cli help for detailed instructions and parameters)
    :param params: parameters of the rpc_call
    :return: data from the rpc_call
    """
    url = "http://127.0.0.1:%s/" % (rpc_port)
    payload = json.dumps({"method": method, "params": params})
    headers = {'content-type': "application/json", 'cache-control': "no-cache"}
    try:
        response = requests.request("POST", url, data=payload, headers=headers, auth=(rpc_user, rpc_password))
    except requests.exceptions.RequestException as e:
        print(e)
    except:
        print('No response from Wallet, check Bitcoin is running on this machine')

    response_json = json.loads(response.text)
    if 'error' in response_json and response_json['error'] != None:
        raise Exception('Error in RPC call: ' + str(response_json['error']))

    return json.loads(response.text)


def rpc_wallet_call(method, params, wallet_label):
    """
    rpc call to a bitcoin core wallet running as a localhost. This call is needed when the call interacts with a
    specific wallet of the bitcoin core so the rpc_call need to access information of that wallet
    :param method: the rpc_call instruction (see bitcoin-cli help for detailed instructions and parameters)
    :param params: parameters of the rpc_call
    :param wallet_label: wallet label
    :return: data from the rpc_call
    """
    url = "http://127.0.0.1:%s/wallet/%s" % (rpc_port, wallet_label)
    payload = json.dumps({"method": method, "params": params})
    headers = {'content-type': "application/json", 'cache-control': "no-cache"}
    try:
        response = requests.request("POST", url, data=payload, headers=headers, auth=(rpc_user, rpc_password))
    except requests.exceptions.RequestException as e:
        print(e)
    except:
        print('No response from Wallet, check Bitcoin is running on this machine')

    response_json = json.loads(response.text)
    if 'error' in response_json and response_json['error'] != None:
        raise Exception('Error in RPC call: ' + str(response_json['error']))

    return json.loads(response.text)


def create_new_wallet(wallet_label):
    rpc_general_call("createwallet", {"wallet_name": str(wallet_label)})
    return


def get_new_address(wallet_label, address_type, label=''):
    # address_type can be: 'legacy', p2sh-segwit, bech32, bech32m
    response = rpc_wallet_call("getnewaddress", {"address_type": str(address_type), "label": str(label)}, wallet_label)
    address = response['result']
    return address


def perform_simple_payment(origin_wallet_label, destination_wallet_label, destination_address_type, value,
                           fee_rate=None):
    """
    This function perform a simple payment from wallet origin_wallet_label to destination_address using Bitcoin core
    UTXO selection.
    :param origin_wallet_label:
    :param destination_address:
    :param value:
    :param fee_rate:
    :return:
    """

    destination_address = get_new_address(destination_wallet_label, destination_address_type, label='')

    if fee_rate == None:
        ## Use Bitcoin Core fee estimation
        response = rpc_wallet_call("sendtoaddress", {"address": str(destination_address), "amount": str(value)},
                                   origin_wallet_label)
    else:
        response = rpc_wallet_call("sendtoaddress",
                                   {"address": str(destination_address), "amount": str(value), "fee_rate": fee_rate},
                                   origin_wallet_label)

    transaction_id = response['result']
    # retrieve all tx_data and store in a file. Not needed if txindex=1 is set in the bitcoin.conf file.
    response_gettx = rpc_wallet_call("gettransaction", {"txid": transaction_id}, origin_wallet_label)
    return transaction_id


def perform_complex_payment(origin_wallet_label, destination_wallet_label, destination_address_type, value, fee_rate=None, type_of_defense=1):
    """
    This function perform a simple payment from wallet origin_wallet_label to destination_address using Bitcoin core
    UTXO selection.
    :param origin_wallet_label:
    :param destination_address:
    :param value:
    :param fee_rate:
    :return:
    """
    HeuristicClass = Heuristics()
    AntiHeuristicClass = AntiHeuristics(origin_wallet_label)

    destination_address = get_new_address(destination_wallet_label, destination_address_type, label='')

    #Create automatic transaction
    automatic_transaction = rpc_wallet_call("createrawtransaction", {"inputs": [], "outputs":[{destination_address: str(value)}] }, origin_wallet_label)
    funded_transaction = rpc_wallet_call("fundrawtransaction", {"hexstring": str(automatic_transaction['result']), "options": {"add_inputs": True, "change_type": "legacy", "fee_rate": str(fee_rate)}}, origin_wallet_label)
    decoded_tx = rpc_wallet_call("decoderawtransaction", {"hexstring": str(funded_transaction['result']['hex'])}, origin_wallet_label)

    #catch txid
    transaction_formated = [str(decoded_tx['result']['txid']), list()]
    
    #catch inputs
    vin = decoded_tx['result']['vin']
    inputs = []

    for inputt in vin:
        trans = rpc_wallet_call("getrawtransaction", {"txid": inputt['txid']}, origin_wallet_label)
        trans_decoded = rpc_wallet_call("decoderawtransaction", {"hexstring": str(trans['result'])}, origin_wallet_label)
        inputs.append([trans_decoded['result']['vout'][inputt['vout']]['scriptPubKey']['address'], trans_decoded['result']['vout'][inputt['vout']]['value']])
    
    #catch outputs
    vout = decoded_tx['result']['vout']
    outputs = []

    for outputt in vout:
        outputs.append([outputt['scriptPubKey']['address'], outputt['value']])
    
    trans_final = [inputs, outputs]
    transaction_formated[1] = trans_final[:]
    
    #now that we have the formated transaction, this transaction can be analyzed by the heuristics
    #Defensa1
    print("Before anticlustering:")
    print(transaction_formated)

    if(type_of_defense == 1):
        
        l = HeuristicClass.adressTypeForTransaction(transaction_formated[1])
        if l != "no":
            if l != destination_address:
                print("Address Type 1 anticlustering...")
                transaction_formated = AntiHeuristicClass.defensa1AddressType(transaction_formated, destination_address)
        
        l = HeuristicClass.detectionUsingDecimalPlaces(transaction_formated[1])
        if l != "no":
            if l != destination_address:
                print("Detection Decimal 1 anticlustering...")
                transaction_formated = AntiHeuristicClass.defensa1DetectionUsingDecimalPlaces(transaction_formated, destination_address)
        
        l = HeuristicClass.exactPaymentAmmount(transaction_formated[1])
        if l != "no":
                print("Exact Payment 1 anticlustering...")
                transaction_formated = AntiHeuristicClass.defensa1ExactPaymentAmmount(transaction_formated, destination_address)
        
        l = HeuristicClass.optimalChange(transaction_formated[1])
        if l != "no":
            if l != destination_address:
                print("Optimal change 1 anticlustering...")
                transaction_formated = AntiHeuristicClass.defensa1OptimalChange(transaction_formated, destination_address)
                #aquesta defensa es curiosa ja que depenent de l'input que es posi, l'heurística detectarà una altra adreça com a canvi o cap
    else:
    #defensa 2
        l = HeuristicClass.adressTypeForTransaction(transaction_formated[1])
        if l != "no":
            if l != destination_address:
                print("Address Type 2 anticlustering...")
                transaction_formated = AntiHeuristicClass.defensa2AddressType(transaction_formated, destination_address, destination_wallet_label, destination_address_type)
        
        l = HeuristicClass.detectionUsingDecimalPlaces(transaction_formated[1])
        if l != "no":
            if l != destination_address:
                print("Detection Decimal 2 anticlustering...")
                transaction_formated = AntiHeuristicClass.defensa2DetectionUsingDecimalPlaces(transaction_formated, destination_address, destination_wallet_label, destination_address_type)
    
        l = HeuristicClass.exactPaymentAmmount(transaction_formated[1])
        if l != "no":
                print("Exact Payment 2 anticlustering...")
                transaction_formated = AntiHeuristicClass.defensa2ExactPaymentAmmount(transaction_formated, destination_address, destination_wallet_label, destination_address_type)
        
        l = HeuristicClass.optimalChange(transaction_formated[1])
        if l != "no":
            if l != destination_address:
                print("Optimal change 2 anticlustering...")
                transaction_formated = AntiHeuristicClass.defensa2OptimalChange(transaction_formated, destination_address, destination_wallet_label, destination_address_type)
        
    l = HeuristicClass.bip69(transaction_formated[1])
    if l != "bip69":
        print("Bip69 anticlustering...")
        transaction_formated = AntiHeuristicClass.defensaBip69(transaction_formated)
    
    print("After anticlustering:")
    print(transaction_formated)

    
    #in this moment we should have a transaction defended
    #we have to createrawtransaction again with the inputs and outputs of transaction_formated
    #1. Catch the txid and vout of input adresses
    inputs_arr = []
    for i,inputss in enumerate(transaction_formated[1]):
        if i%2 == 0:
            for inputt in inputss:
                inputs = rpc_wallet_call("listunspent", {"addresses": [str(inputt[0])]}, origin_wallet_label)
                inputs_arr.append({"txid": str(inputs['result'][0]['txid']), "vout": inputs['result'][0]['vout']})
    
    #2.Prepare the outputs
    outputs_dict = {}
    for i,outputss in enumerate(transaction_formated[1]):
        if i % 2 != 0:
            for outputt in outputss:
                outputs_dict[str(outputt[0])] = outputt[1]
    
    #Create the final transaction
    final_trans = rpc_wallet_call("createrawtransaction", {"inputs": inputs_arr, "outputs":outputs_dict }, origin_wallet_label)
    final_trans_decoded = rpc_wallet_call("decoderawtransaction", {"hexstring": str(final_trans['result'])}, origin_wallet_label)
    
    print(final_trans_decoded)

    #Firmar la transacción
    signed_trans = rpc_wallet_call("signrawtransactionwithwallet", {"hexstring": str(final_trans['result'])}, origin_wallet_label)
    signed_trans_decoded= rpc_wallet_call("decoderawtransaction", {"hexstring": str(signed_trans['result']['hex'])}, origin_wallet_label)

    print(signed_trans_decoded)


    #Enviar la transacción a la blockchain
    sended_trans = rpc_wallet_call("sendrawtransaction", {"hexstring": str(signed_trans['result']['hex'])}, origin_wallet_label)
    print(sended_trans)
    return sended_trans
    

def mine_to_address(origin_wallet_label, address_type, num_blocks=1):
    """
    This function mines blocks to a specific address

    :param origin_wallet_label:
    :param address_type:
    :param num_blocks: total number of blocks to generate
    :return:
    """
    # obtain a new address from the wallet
    address = get_new_address(origin_wallet_label, address_type, label='')

    # mine the block
    response = rpc_general_call("generatetoaddress", {"nblocks": num_blocks, "address": str(address)})
    blocks = response['result']
    return blocks
