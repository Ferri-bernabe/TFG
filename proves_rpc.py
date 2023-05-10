import bitcoin_core_rpc as rpc
rpc.perform_complex_payment('0001', '0002', 'legacy', 50, 10, 1)

# mine one block to confirm the payment in the blockchain
rpc.mine_to_address('0001', 'legacy', 1)