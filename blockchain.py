import hashlib
from itertools import chain
import json
from operator import length_hint
from pydoc import resolve
from time import sleep, time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request
from hashmoji import hashmoji

# debug purpose only
x_nodes = {}

class Blockchain:

    def __init__(self, node_identifier):

        self.pending_ownerships = []
        self.chain = []
        self.nodes = dict()
        self.node_identifier = node_identifier

        self.generate_new_block(previous_hash=1)
    

    def generate_new_block(self, previous_hash):

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'ownerships': self.pending_ownerships,
            'previous_hash': previous_hash, # NOTE: perché non vanno bene quelli letti dalla chain?
            'validator': self.node_identifier,
        }

        self.pending_ownerships = []
        self.chain.append(block)
        return block


    def new_ownership(self, owner, content):

        self.pending_ownerships.append({
            'owner': owner,
            'content': content,
        })

        return self.last_block['index'] + 1
    
    @property
    def last_block(self):
        return self.chain[-1]
    
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def get_stakes(self):
        stakes = []
        for block in self.chain:
            for ownership in block['ownerships']:
                stakes.append(ownership['owner'])
        return stakes
    
    def pick_validator(self):
        last_hash = self.hash(self.last_block)
        stakes = self.get_stakes()
        stake_index = int(last_hash, 16) % len(stakes)
        validator_identifier = stakes[stake_index]
        return validator_identifier
    
    def register_node(self, node_identifier, node_address):
        parsed_url = urlparse(node_address)
        if parsed_url.netloc:
            self.nodes[node_identifier] = parsed_url.netloc
        elif parsed_url.path:
            self.nodes[node_identifier] = parsed_url.path
        else:
            raise ValueError('Invalid URL')
    
    
    # def resolve_conficts(self):
    #     new_chain = None
    #     max_length = len(self.chain)
    #     for node_identifier, node_address in self.nodes.items():
    #         response = requests.get(f'http://{node_address}/chain')
    #         if response.status_code == 200:
    #             length = response.json()['length']
    #             chain = response.json()['chain']
    #             if length > max_length and self.is_valid_chain(chain):
    #                 max_length = length
    #                 new_chain = chain
    #     if new_chain:
    #         self.chain = new_chain
    #         return True
    #     return False

    def resolve_conflicts(self): # debug purpose only
        new_chain = None
        max_length = len(self.chain)
        for node_identifier, node_address in self.nodes.items():
            chain = x_nodes[node_identifier].chain()
            length = len(chain)
            if length > max_length and self.is_valid_chain(chain):
                max_length = length
                new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        return False


    @staticmethod
    def is_valid_chain(chain): # Per ora verifico solo l'integrità degli hash
        previous_block = chain[0]
        for block in chain[1:]:
            if block['previous_hash'] != Blockchain.hash(previous_block):
                return False
            previous_block = block
        return True

    def is_valid_block(self, block, previous_hash):
        if block['previous_hash'] != previous_hash:
            return False
        if block['validator'] != self.pick_validator():
            return False
        
    def confirm_validation(self, block) -> bool:
        if self.is_valid_block(block, self.last_block['previous_hash']):
            self.chain.append(block)
            for ownership in block['ownerships']:
                self.pending_ownerships.remove(ownership) # NOTE: verificare che abbia senso
            return True
        else:
            return False
    
    def proof_of_stake(self):
        self.resolve_conflicts()
        

