import hashlib
import json
import random
import time
import requests
import os

from itertools import count
from typing import Optional, List
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


def w(text: str) -> str:
    return colored(text, 'grey', on_color='on_white', attrs=['bold'])


######### VERIFICATION #########

def hash(block):
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()


def proof_verification(last_proof, proof, last_hash):
    guess = f'{last_proof}{proof}{last_hash}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash

######### VISUALIZATION #########

def print_separator(char: str = ' ', fgc: str = 'grey', bgc: str = 'on_white', end: str = '\n\n'):
    print(colored(char * os.get_terminal_size().columns, fgc, bgc), end=end)



class BlockchainSimulator():

    def __init__(self, miners_addr_path: str, num_members: int):

        with open(miners_addr_path, 'r') as f:
            miners_addr = f.read().splitlines()

        self.members = {str(uuid4()).replace('-', '') for _ in range(num_members - len(miners_addr))}

        self.miners = {}

        for addr in miners_addr:
            response = requests.get(f'http://{addr}/identify')
            if response.status_code == 200:
                id = response.json()['identifier']
                self.members.add(id)
                self.miners[id] = f'http://{addr}'
        
        for miner in self.miners:
            self.do_register(miner)
    
    @staticmethod
    def log_error(message: str, code: int):
        cprint(f'{message} - http return code {code}', 'red')

    def random_transaction(self) -> dict:
        sender, recipient = random.sample(list(self.members), 2)
        return {
            'sender': sender,
            'recipient': recipient,
            'amount': random.randint(10, 99),
        }
    
    def random_miner(self) -> str:
        return random.choice(list(self.miners.keys()))
    

    def get_chain(self, miner: Optional[str] = None) -> Optional[dict]:

        if not miner:
            miner = self.random_miner()

        response = requests.get(f'{self.miners[miner]}/chain')
        if response.status_code == 200:
            response_dict = response.json()
            return response_dict
        else:
            self.log_error(f'Error retrieving chain from {miner}', response.status_code)
            return None
    
    def do_transaction(self, data: dict, miner: Optional[str] = None) -> Optional[dict]:

        if not miner:
            miner = self.random_miner()

        response = requests.post(f'{self.miners[miner]}/transactions/new', json=data)
        if response.status_code == 201:
            response_dict = response.json()
            return response_dict
        else:
            self.log_error(f'Error submitting transaction to {miner}', response.status_code)
            return None


    def do_mine(self, miner: Optional[str] = None) -> Optional[dict]:

        if not miner:
            miner = self.random_miner()

        response = requests.get(f'{self.miners[miner]}/mine')
        if response.status_code == 200:
            response_dict = response.json()
            return response_dict
        else:
            self.log_error(f'Error while trying to mine on {miner}', response.status_code)
            return None


    def do_resolve(self, miner: Optional[str] = None) -> Optional[dict]:

        if not miner:
            miner = self.random_miner()

        response = requests.get(f'{self.miners[miner]}/nodes/resolve')
        if response.status_code == 200:
            response_dict = response.json()
            return response_dict
        else:
            self.log_error(f'Error while trying to resolve the conflicts on {miner}', response.status_code)
            return None
    
    def do_register(self, miner: str, others: Optional[List[str]] = None) -> Optional[dict]:

        if not others:
            others = [self.miners[other] for other in set(self.miners.keys()) - {miner}]

        data = {'nodes': others}
        response = requests.post(f'{self.miners[miner]}/nodes/register', json=data)
        if response.status_code == 201:
            response_dict = response.json()
            return response_dict
        else:
            self.log_error(f'Error during the registration of {miner}', response.status_code)
            return None

    @staticmethod
    def visualize_resolve(miner: str, response_dict: Optional[dict]):
        if response_dict:
            if response_dict['status'] == 'authoritative':
                print(f"{g(miner)} says its chain is authoritative")
            elif response_dict['status'] == 'updated':
                print(f"{g(miner)} has updated its chain - {response_dict['length_diff']} blocks have been added")
            elif response_dict['status'] == 'conflict':
                print(f"{g(miner)} has replaced its chain - it was {response_dict['length_diff']} blocks ahead")

    @staticmethod
    def format_transaction(transaction: dict):
        sender = transaction['sender']
        amount = transaction['amount']
        recipient = g(transaction['recipient'])
        if sender == '0':
            return f'{recipient} got  {amount} coins as a reward'
        sender = g(sender)
        return f"{sender} sent {amount} coins to {recipient}"
    

    @staticmethod
    def visualize_chain(chain: dict, blocks_to_print: int = 1):
        last_proof = ''
        for i, block in enumerate(chain['chain']):
            index = block['index']
            timestamp = time.strftime('%d-%m-%Y at %H:%M:%S', time.localtime(block['timestamp']))
            proof = block['proof']
            previous_hash = block['previous_hash']
            transactions = [BlockchainSimulator.format_transaction(t) for t in block['transactions']]
            miner = block['miner']
            if i >= len(chain['chain']) - blocks_to_print:
                print_separator()
                print(r("This is the block number"), index, end='\n\n')
                print(r("mined on"), timestamp, r("by the miner"), g(miner), end='\n\n')
                print(r("with nonce"), proof, r("to get"), proof_verification(last_proof, proof, previous_hash), end='\n\n')
                print(r("the hash of the previous block is"), previous_hash, end='\n\n')
                print(r("the included transactions are:"), end='\n')
                for i, transaction in enumerate(transactions):
                    print(f"- {transaction}")
                print('')
                print(r("the hash of this block is:"), hash(block), end='\n\n')
                print_separator()
            last_proof = proof
        
    @staticmethod
    def visualize_mine(miner: str, response_dict: Optional[dict]):
        if response_dict:
            print(f"{g(miner)} has mined a block!")

    def simulate(self, epochs: Optional[int] = None, epoch_duration: float = 2, max_epoch_transcs: int = 10, resolve_prob: float = 0.2):
        
        for epoch in count(start=1):

            #os.system('cls' if os.name == 'nt' else 'clear -x')
            
            label = f"Running epoch {epoch}..."
            label = label + ' ' * (os.get_terminal_size().columns - len(label))
            label = w(label)

            print(label, end='\n\n')

            n = 8
            i = 0

            time.sleep((epoch_duration / n))
            i += 1

            print(f"The submitted transactions are:")

            for transc in [self.random_transaction() for _ in range(random.randint(1, max_epoch_transcs))]:
                miner = self.random_miner()
                print(self.format_transaction(transc), f"- submitted to {g(miner)}")
                self.do_transaction(transc, miner)

            print()
            time.sleep(epoch_duration / n)
            i += 1
        
            miner = self.random_miner()
            print(f"Mining in progress...", end='\n')
            if resp := self.do_mine(miner):
                self.visualize_mine(miner, resp)
                
            print()
            time.sleep(epoch_duration / n)
            i += 1

            print(f"Performing the consensus:")

            for miner in self.miners:
                if random.random() < resolve_prob:
                    resp = self.do_resolve(miner)
                    print("- ", end='')
                    self.visualize_resolve(miner, resp)

            time.sleep(epoch_duration / n)
            i += 1

            miner = self.random_miner()
            print(f"\nAsking {miner} to give us the last block...", end='\n\n')
            if chain := self.get_chain(miner=miner):
                self.visualize_chain(chain=chain, blocks_to_print=1)

            time.sleep((epoch_duration / n) * (n - i))

            if epochs and epoch > epochs:
                break


if __name__ == '__main__':
    sim = BlockchainSimulator(miners_addr_path='nodes.txt', num_members=10)
    sim.simulate(epochs=None, epoch_duration=6, max_epoch_transcs=10, resolve_prob=0.8)
