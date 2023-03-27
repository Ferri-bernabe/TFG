import bitcoin_core_rpc as rpc

# create a wallet
wallet_label = '00010'
rpc.create_new_wallet(wallet_label)

# create another wallet
wallet_label = '00020'
rpc.create_new_wallet(wallet_label)

# mine more than 100 blocks to have spendable coins in the first wallet
rpc.mine_to_address('00010', 'legacy', 200)

# perform a payment from the first wallet to the second one
rpc.perform_simple_payment('00010', '00020', 'legacy', 50, 10)

# mine one block to confirm the payment in the blockchain
rpc.mine_to_address('00010', 'legacy', 1)
