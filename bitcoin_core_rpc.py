#!/usr/bin/env python

import json
import requests

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
