from utils import get_uniform_random
from node import Node
from blockchain import BlockChain
from ecdsa import SigningKey
from collections import Counter

import random

class Network:
    def __init__(self, num_nodes):
        node_list = []
        self.num_nodes = num_nodes
        self.blockchain = BlockChain()
        self.total_stake = 0
        def choose_random_except(n, except_list):
            random_numbers = []
            for i in range(n):
                num = get_uniform_random(0, num_nodes-1)
                while num in except_list:
                    num = get_uniform_random(0, num_nodes-1)
                
                random_numbers.append(num)
            
            return random_numbers[:]

        for n_id in range(num_nodes):
            _node = self._create_node(n_id)
            self.total_stake += _node.stake
            node_list.append(_node)
        
        for _node in node_list:
            _node.total_stake = self.total_stake
        # print("node_creation_done")

        for i in range(num_nodes): # ring formation
            node_list[i].add_neighbor(node_list[i-1])
            node_list[i].add_neighbor(node_list[(i+1)%num_nodes])
        
        # print("ring_creation_done")
        print("Adjacency list")
        for i in range(num_nodes):
            num_of_neighbors = get_uniform_random(2, 4) - 2
            for n_id in choose_random_except(num_of_neighbors, [i-1 if i>0 else num_nodes-1, i, i+1 if i < num_nodes else 0]):
                node_list[i].add_neighbor(node_list[n_id])
            print("Node {}: ".format(i), [n.id for n in node_list[i].neighbors])

        print("network_creation_done")

        self.node_list = node_list

    def get_node_by_id(self, n_id):
        assert n_id < len(self.node_list)
        return self.node_list[n_id]
        
    def _create_node(self, n_id):
        stake = get_uniform_random(1, 50)
        # print(n_id)
        private_key = SigningKey.generate() # uses NIST192p
        public_key = private_key.get_verifying_key()
        node = Node(n_id, stake, private_key, public_key, self.blockchain)
        node.reset(0)
        return node
    
    def print_stack_sortion_stats(self):
        fract_stats = Counter()
        num_stats = Counter()
        counts = Counter()
        for node in self.node_list:
            fract_stats[node.stake] += node.fraction_sub_user
            num_stats[node.stake] += node.num_sub_user
            counts[node.stake] += node.num_sub_user_count
        
        for i in range(1, 51):
            if counts[i] > 0:
                print("{} {} {}".format(i, fract_stats[i]/counts[i], num_stats[i]/counts[i]))
            else:
                print("{} {} {}".format(i, 0.0, 0.0))
    
    def print_highest_proposer(self):
        high_proposer_stats = Counter()
        for node in self.node_list:
            message = node.max_prio_msg
            if message is not None:
                pub_key = message.public_key.to_string()
                print("key: {}".format(node.public_key.to_string()))
                high_proposer_stats[pub_key] += 1

        for key, val in high_proposer_stats.items():
            print("Key: {}".format(key))
            print("Count: {}".format(val))
