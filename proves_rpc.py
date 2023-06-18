import bitcoin_core_rpc as rpc
import random
'''
rpc.perform_complex_payment('0001', '0002', 'legacy', 50, 10, 1)

# mine one block to confirm the payment in the blockchain
rpc.mine_to_address('0001', 'legacy', 1)
'''
wallet_names = []
type_of_directions = ["legacy", "p2sh-segwit", "bech32"]
llista_fees_per_simulacio = []

for reps in range(0,100):
    preu_a_baixar = 0
    if reps %10 == 0:
        preu_a_baixar = reps/10 
    

    pagaments = 0
    i = 0
    while(i < 7):
        wallet_label = str(random.randint(1000, 9999))
        type_of_direction = type_of_directions[random.randint(0,2)]

        if wallet_label not in wallet_names:
            rpc.create_new_wallet(wallet_label)
            wallet_names.append(wallet_label)
            if len(wallet_names) == 1:
                for j in range(201):
                    rpc.mine_to_address(wallet_label, type_of_direction, 1)
        
        rpc.perform_complex_payment(wallet_names[0], wallet_label,type_of_direction, 11-preu_a_baixar, 10, 1)
        pagaments +=1
        rpc.mine_to_address(wallet_label, type_of_direction, 1)

        
        num = 0
        if len(wallet_names) > 2:
            num = random.randint(0, len(wallet_names)-2)
        rpc.perform_complex_payment(wallet_label, wallet_names[num], type_of_direction, random.randint(1,10-preu_a_baixar), random.randint(5,20), random.randint(1,2))
        pagaments += 1
        rpc.mine_to_address(wallet_label, type_of_direction, 1)

        i += 1

    print(rpc.fees / pagaments)
    llista_fees_per_simulacio.append(rpc.fees / pagaments)
    print(llista_fees_per_simulacio)


print(llista_fees_per_simulacio)
