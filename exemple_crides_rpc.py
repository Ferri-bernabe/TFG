import bitcoin_core_rpc as rpc

# create a wallet
wallet_label = '0001'
rpc.create_new_wallet(wallet_label)

# create another wallet
wallet_label = '0002'
rpc.create_new_wallet(wallet_label)

# mine more than 100 blocks to have spendable coins in the first wallet
rpc.mine_to_address('0001', 'legacy', 200)

# perform a payment from the first wallet to the second one
rpc.perform_simple_payment('0001', '0002', 'legacy', 50, 10)

# mine one block to confirm the payment in the blockchain
rpc.mine_to_address('0001', 'legacy', 1)

# mine more than 100 blocks to have spendable coins in the first wallet
rpc.mine_to_address('0002', 'legacy', 200)