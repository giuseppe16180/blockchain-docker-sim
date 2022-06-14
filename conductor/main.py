# %%

from operator import le
from turtle import end_fill
from numpy import byte
from regex import F
import requests
import random
import json
from hashmoji import hashmoji
from typing import Optional
from termcolor import colored, cprint


url = 'http://localhost:5001'

def hex_to_emoji(hash):
    return ' '.join([c for c in hashmoji(hash) if c != ' '])

# fuction to get the chain
def get_chain() -> Optional[dict]:
    response = requests.get(f'{url}/chain')
    if response.status_code == 200:
        response_dict = response.json()
        return response_dict
    else:
        return None

def do_transaction(data) -> Optional[dict]:
    response = requests.post(f'{url}/transactions/new', json=data)
    if response.status_code == 201:
        response_dict = response.json()
        return response_dict
    else:
        return None

def do_mine() -> Optional[dict]:
    response = requests.get(f'{url}/mine')
    if response.status_code == 200:
        response_dict = response.json()
        return response_dict
    else:
        return None

get_chain()
do_transaction({'sender': 'pippo', 'recipient': 'pluto', 'amount': random.randint(1, 100)})
do_mine()
get_chain()

# %%

# %%
import hashlib

def hash(block):
    """
    Creates a SHA-256 hash of a Block

    :param block: Block
    """

    # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()


def proof_verification(last_proof, proof, last_hash):
    """
    Validates the Proof

    :param last_proof: <int> Previous Proof
    :param proof: <int> Current Proof
    :param last_hash: <str> The hash of the Previous Block
    :return: <bool> True if correct, False if not.

    """

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
        timestamp = time.strftime('%d-%m-%Y at %H:%M:%S', time.localtime(block['timestamp']))
        proof = block['proof']
        previous_hash = block['previous_hash'] #hex_to_emoji(block['previous_hash'])
    
        transactions = [visualize_transaction(transaction) for transaction in block['transactions']]

        if i >= len(chain['chain']) - blocks_to_print:

            cprint(f"{' ' * 10}Block number {index}{' ' * 10}", 'grey', 'on_red', attrs=['bold'])

            cprint(f"mined on", 'red', attrs=['bold'], end=' ')
            cprint(f"{timestamp}")
            cprint(f"with proof", 'red', attrs=['bold'], end=' ')
            cprint(f"{proof}", end=' ')

            cprint(f"to get", 'red', attrs=['bold'], end=' ')
            cprint(f"{proof_verification(last_proof, proof, previous_hash)}")

            cprint(f"the hash of the previous block is", 'red', attrs=['bold'], end=' ')
            cprint(f"{previous_hash}")
            cprint(f"the included transactions are: ", 'red', attrs=['bold'], end='\n')
            for i, transaction in enumerate(transactions):
                print(f"- {transaction}")
            cprint(f"the hash of this block is:", 'red', attrs=['bold'], end=' ')
            cprint(hash(block))
            
            print()

        last_proof = proof






c = get_chain()


if c:
    visualize_chain(c)


# %%

hashx = "8bfb0b039f6f320c1cb36a4a6d0932b8f35945288d1f94a9126150b4638c70d6"
hashx = bytes.fromhex(hashx)
print(hashx)
# %%
