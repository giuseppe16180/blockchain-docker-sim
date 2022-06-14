# %%

import asyncio
import hashlib
import json
import random
import time
from operator import le
from turtle import end_fill
from typing import Optional
from urllib import response
from uuid import uuid4

import requests
from hashmoji import hashmoji
from numpy import byte
from regex import F
from sklearn.utils import resample
from termcolor import colored, cprint






def hash(block):
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()


def proof_verification(last_proof, proof, last_hash):
    guess = f'{last_proof}{proof}{last_hash}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash


def visualize_transaction(transaction: dict):
    if transaction['sender'] == '0':
        amount = transaction['amount']
        recipient = transaction['recipient']
        amount = colored(amount, 'red', attrs=['bold'])
        recipient = colored(recipient, 'green', attrs=['bold'])
        return f'{recipient} got {amount} coins as a reward'
    amount = transaction['amount']
    sender = transaction['sender']
    recipient = transaction['recipient']
    amount = colored(f"{amount}", 'red', attrs=['bold'])
    sender = colored(f"{sender}", 'blue', attrs=['bold'])
    recipient = colored(f"{recipient}", 'green', attrs=['bold'])
    return f"{sender} sent {amount} coins to {recipient}"


def visualize_chain(chain: dict, blocks_to_print: int = 1):

    last_proof = ''

    for i, block in enumerate(chain['chain']):

        index = block['index']
        timestamp = time.strftime(
            '%d-%m-%Y at %H:%M:%S', time.localtime(block['timestamp']))
        proof = block['proof']
        # hex_to_emoji(block['previous_hash'])
        previous_hash = block['previous_hash']

        transactions = [visualize_transaction(
            transaction) for transaction in block['transactions']]
        
        miner = block['miner']

        if i >= len(chain['chain']) - blocks_to_print:

            cprint(f"{' ' * 10}Block number {index}{' ' * 10}",
                   'grey', 'on_red', attrs=['bold'])

            cprint(f"mined on", 'red', attrs=['bold'], end=' ')
            cprint(f"{timestamp}")

            cprint("by the miner: ", 'red', attrs=['bold'], end=' ')
            cprint(f"{miner}", 'blue', attrs=['bold'])

            cprint(f"with proof", 'red', attrs=['bold'], end=' ')
            cprint(f"{proof}", end=' ')

            cprint(f"to get", 'red', attrs=['bold'], end=' ')
            cprint(f"{proof_verification(last_proof, proof, previous_hash)}")

            cprint(f"the hash of the previous block is",
                   'red', attrs=['bold'], end=' ')
            cprint(f"{previous_hash}")
            cprint(f"the included transactions are: ",
                   'red', attrs=['bold'], end='\n')
            for i, transaction in enumerate(transactions):
                print(f"- {transaction}")
            cprint(f"the hash of this block is:",
                   'red', attrs=['bold'], end=' ')
            cprint(hash(block))

            print()

        last_proof = proof






with open('nodes.txt', 'r') as f:
    nodes = f.read().splitlines()

members = {str(uuid4()).replace('-', '') for _ in range(5)}
miners = {}

for node in nodes:
    response = requests.get(f'http://{node}/identify')
    if response.status_code == 200:
        id = response.json()['identifier']
        members.add(id)
        miners[id] = f'http://{node}'

print(members, miners)


def random_transaction():
    sender, recipient = random.sample(members, 2)
    return {
        'sender': sender,
        'recipient': recipient,
        'amount': random.randint(1, 100),
    }

# %%

import sys

def log_error(function, code):
    cprint(f"\nError! http code {code} as response to {function}\n", 'red', attrs=['bold'], file=sys.stderr)


def get_chain(miner) -> Optional[dict]:
    response = requests.get(f'{miners[miner]}/chain')
    if response.status_code == 200:
        response_dict = response.json()
        return response_dict
    else:
        log_error('chain', response.status_code)
        return None

def do_transaction(data, miner) -> Optional[dict]:
    response = requests.post(f'{miners[miner]}/transactions/new', json=data)
    if response.status_code == 201:
        response_dict = response.json()
        return response_dict
    else:
        log_error('transaction', response.status_code)
        return None

def do_mine(miner) -> Optional[dict]:
    response = requests.get(f'{miners[miner]}/mine')
    if response.status_code == 200:
        response_dict = response.json()
        return response_dict
    else:
        log_error('mine', response.status_code)
        return None


def do_resolve(miner) -> Optional[dict]:
    response = requests.get(f'{miners[miner]}/nodes/resolve')
    if response.status_code == 200:
        response_dict = response.json()
        print(response_dict['message'])
        return response_dict
    else:
        log_error('resolve', response.status_code)
        return None

def do_register():
    for miner in miners:
        others = set(miners.keys()) - {miner}
        nodes = [miners[other] for other in others]
        data = {'nodes': nodes}
        response = requests.post(f'{miners[miner]}/nodes/register', json=data)
        if response.status_code == 201:
            response_dict = response.json()
        else:
            log_error('register', response.status_code)
            return None

def random_miner():
    return random.choice(list(miners.keys()))

do_register()

while True:
    new_transactions = [random_transaction() for _ in range(random.randint(1, 10))]
    for transaction in new_transactions:
        do_transaction(transaction, random_miner())
   
    do_mine(random_miner())
    
    for miner in miners.keys():
        do_resolve(miner)
    chain = get_chain(random_miner())
    if chain: visualize_chain(chain=chain, blocks_to_print=1)
    time.sleep(2)
    #visualize_chain(get_chain(random_miner()), 1)

    


# %%

res = requests.get('http://localhost:5002/mine')
if res.status_code == 200:
    print(res.json())
else:
    print(res.status_code)







    # do mine for all the nodes







#def hex_to_emoji(hash):
#    return ' '.join([c for c in hashmoji(hash) if c != ' '])