# %%

import hashlib
import json
import random
import time
import requests
import os

from typing import Optional, List, Dict, Set
from urllib import response
from uuid import uuid4
from termcolor import colored, cprint

######### TEXT STYLING #########

def r(text: str) -> str:
    return colored(text, 'red', attrs=['bold'])


def g(text: str) -> str:
    return colored(text, 'green', attrs=['bold'])


def b(text: str) -> str:
    return colored(text, 'blue', attrs=['bold'])


def h(text: str) -> str:
    return colored(text, 'grey', on_color='on_red', attrs=['bold'])


######### VERIFICATION #########

def hash(block):
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()


def proof_verification(last_proof, proof, last_hash):
    guess = f'{last_proof}{proof}{last_hash}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash

######### VISUALIZATION #########

def visualize_transaction(transaction: dict):
    sender = transaction['sender']
    amount = r(transaction['amount'])
    recipient = g(transaction['recipient'])
    
    if sender == '0':
        return f'{recipient} got {amount} coins as a reward'
    
    sender = b(sender)
    return f"{sender} sent {amount} coins to {recipient}"



def visualize_chain(chain: dict, blocks_to_print: int = 1):

    last_proof = ''

    for i, block in enumerate(chain['chain']):

        index = block['index']

        timestamp = time.strftime('%d-%m-%Y at %H:%M:%S', time.localtime(block['timestamp']))

        proof = block['proof']

        previous_hash = block['previous_hash']

        transactions = [visualize_transaction(t) for t in block['transactions']]

        miner = block['miner']

        if i >= len(chain['chain']) - blocks_to_print:

            print(h(f"Block number {index} {' ' * 80}"), end='\n\n')
            print(r("mined on"), timestamp, r("by the miner"), b(miner), end='\n\n')
            print(r("with nonce"), proof, r("to get"), proof_verification(last_proof, proof, previous_hash), end='\n\n')
            print(r("the hash of the previous block is"), previous_hash, end='\n\n')
            print(r("the included transactions are:"), end='\n')
            for i, transaction in enumerate(transactions):
                print(f"- {transaction}")
            print('')
            print(r("the hash of this block is:"), hash(block), end='\n\n')
            print(h(' ' * 80))

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


def log_error(message, code):
    cprint(f'{message} - http return code {code}', 'red')


def get_chain(miner) -> Optional[dict]:
    response = requests.get(f'{miners[miner]}/chain')
    if response.status_code == 200:
        response_dict = response.json()
        return response_dict
    else:
        log_error(f'Error retrieving chain from {miner}', response.status_code)
        return None


def do_transaction(data, miner) -> Optional[dict]:
    response = requests.post(f'{miners[miner]}/transactions/new', json=data)
    if response.status_code == 201:
        response_dict = response.json()
        return response_dict
    else:
        log_error(f'Error submitting transaction to {miner}', response.status_code)
        return None


def do_mine(miner) -> Optional[dict]:
    response = requests.get(f'{miners[miner]}/mine')
    if response.status_code == 200:
        response_dict = response.json()
        return response_dict
    else:
        log_error(f'Error while trying to mine on {miner}', response.status_code)
        return None


def do_resolve(miner) -> Optional[dict]:
    response = requests.get(f'{miners[miner]}/nodes/resolve')
    if response.status_code == 200:
        response_dict = response.json()
        return response_dict
    else:
        log_error('resolve', response.status_code)
        return None

def visualize_resolve(miner: str, response_dict: Optional[dict]):
    if response_dict:
        if response_dict['status'] == 'authoritative':
            print(f"The chain of {miner} is authoritative")
        elif response_dict['status'] == 'replaced':
            print(f"The chain of {miner} has been replaced - {response_dict['length_diff']} blocks have been added")


def do_register(miner: str, others: List[str]):
    data = {'nodes': others}
    response = requests.post(f'{miners[miner]}/nodes/register', json=data)
    if response.status_code == 201:
        response_dict = response.json()
        return response_dict
    else:
        log_error(f'Error during the registration of {miner}', response.status_code)
        return None


def random_miner():
    return random.choice(list(miners.keys()))

# MAIN

for miner in miners:
    others = set(miners.keys()) - {miner}
    nodes = [miners[other] for other in others]
    data = {'nodes': nodes}
    do_register(miner, nodes)

while True:
    
    for transaction in [random_transaction() for _ in range(random.randint(1, 10))]: 
        do_transaction(transaction, random_miner())

    to_resolve = random_miner()
    if resp := do_resolve(to_resolve):  # TODO: add more miners
        visualize_resolve(to_resolve, resp)

    to_mine = random_miner()
    if resp := do_mine(to_mine):
        pass

    if chain := get_chain(random_miner()):
        visualize_chain(chain=chain, blocks_to_print=1)

    time.sleep(2)

