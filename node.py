from collections import Counter
from utils import get_normal_random, pseudo_random_generator
from message import Message
import hashlib
import math
from scipy.special import comb


class Node:
    def __init__(self, _id, stake, private_key, public_key, blockchain):
        self.s_final = 3
        self.stake = stake
        self.total_stake = 0
        self.id = _id
        self.neighbors = []
        self.blockchain = blockchain
        self.private_key = private_key
        self.public_key = public_key
        self.block_msg_delay = get_normal_random(200, 400)
        self.non_block_msg_delay = get_normal_random(40, 64)

        # All variables for experiments
        self.num_sub_user = 0
        self.fraction_sub_user = 0.0
        self.num_sub_user_count = 0
    
    def reset(self, r):
        self.round = r
        self.step = 0
        self.s_dash = None
        self.rcved_msgs = set()
        self.all_prio_messages = []
        self.votes = []
        self.is_member = False
        self.prio_message = None
        self.max_prio_msg = None
        self.proposed_block = []
        self.block_hash = b''
        self.r = b''
        self.hash_len = 0

    def _get_bin(self, j, p):
        res = 0.0
        for k in range(j+1):
            res += (comb(self.stake, k) * math.pow(p, k)
                    * math.pow(1-p, self.stake-k))
        return res

    def _sortition(self, t_proposer, _hash):
        p = float(t_proposer) / self.total_stake
        j = 0

        hash_int = int.from_bytes(_hash, byteorder='big', signed=False)
        self.hash_len = hash_int.bit_length()
        while True:
            lower = self._get_bin(j, p)
            upper = self._get_bin(j+1, p)
            _temp = hash_int / math.pow(2, self.hash_len)
            if _temp >= lower and _temp < upper:
                j += 1
            else:
                break

        return j

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def calculate_node_priority(self, _hash, j):
        max_prio = None
        sub_usr_id = 0
        for i in range(1, j+1):
            _temp = hashlib.sha256(_hash+bytes([i])).digest()
            if max_prio is None:
                max_prio = _temp
                sub_usr_id = i
            elif max_prio > _temp:
                max_prio = _temp
                sub_usr_id = i

        return max_prio, sub_usr_id

    def is_committee_member(self, r, s, _t):
        seed = hashlib.sha256(self.blockchain.get_last_block()
                              ).digest() + bytes([r]) + bytes([s])
        n = pseudo_random_generator(seed)
        n = str(n).encode()
        _hash = self.private_key.sign(n)
        j = self._sortition(_t, _hash)

        if j > 0:
            self.is_member = True
            if self.s_dash is None:
                print("Step: {} Node ID: {} is in committee".format(s, self.id))
            else:
                print("Node ID: {} is in committee".format(self.id))
        else:
            self.is_member = False
        
        self.num_sub_user += j
        self.fraction_sub_user += (j/50)
        self.num_sub_user_count += 1

        return _hash, j, n

    def create_priority_message(self, r, s, t_proposer):
        _hash, j, seed = self.is_committee_member(r, s, t_proposer)
        if j > 0:
            priority, sub_usr_index = self.calculate_node_priority(_hash, j)
            _message = b' || '.join(
                [bytes([r]), _hash, bytes([sub_usr_index]), priority])
            prio_msg = Message('NON_BLOCK', _message, self.public_key,
                               self.private_key.sign(_message), seed)
            self.prio_message = prio_msg
            self.max_prio_msg = prio_msg
            return prio_msg

    def receive_prio_msg(self, message):
        if message.id not in self.rcved_msgs:
            self.rcved_msgs.add(message.id)
            if message.verify():
                msg_prio = message.payload.split(b' || ')[-1]
                msg_prio = int.from_bytes(msg_prio, byteorder='big', signed=False)
                self.all_prio_messages.append((message, msg_prio)) 
                if self.is_member:
                    max_prio = self.max_prio_msg.payload.split(b' || ')[-1]
                    max_prio = int.from_bytes(max_prio, byteorder='big', signed=False) 
                    if max_prio > msg_prio:
                        self.max_prio_msg = message
                return message

    def print_prio_message(self):
        self.all_prio_messages = sorted(self.all_prio_messages, key= lambda k: k[1])
        print("Received messages: Node {}".format(self.id))
        for message, prio in self.all_prio_messages:
            print("M: {} \n Prio: {}".format(message.payload,prio))

    def propose_block(self):
        #self.print_prio_message()
        if self.is_member:
            max_prio = self.max_prio_msg.payload.split(b' || ')[-1]
            own_prio = self.prio_message.payload.split(b' || ')[-1]
            if max_prio == own_prio:
                print("Node: {} proposing the block".format(self.id))
                prev_hash = hashlib.sha256(
                    self.blockchain.get_last_block()).digest()
                random_str = str(pseudo_random_generator()).encode()
                prio_msg_payload = self.prio_message.payload.split(b' || ')[1]
                _message = b' || '.join([prev_hash, random_str, prio_msg_payload])
                print("Proposed Block: {}".format(_message))
                block_msg = Message('BLOCK', _message, self.public_key, self.private_key.sign(
                    _message), self.prio_message.seed, prio=own_prio)
                return block_msg

    def receive_block_proposal(self, message):
        if message.id not in self.rcved_msgs and message.verify() and self._verify_sortition(message):
            priority = message.payload.split(b' || ')[-1]
            priority = int.from_bytes(priority, byteorder='big', signed=False)
            self.proposed_block.append((message, priority))
            self.rcved_msgs.add(message.id)
            return message

    def print_proposal_message(self):
        self.proposed_block = sorted(self.proposed_block, key= lambda k: k[1])
        print("Received proposed_block: Node {}".format(self.id))
        for message, prio in self.proposed_block:
            print("M: {} \n Prio: {}".format(message.payload,prio))


    def _verify_sortition(self, block):
        #return True
        payload_split = block.payload.split(b' || ')
        _hash = payload_split[-1]
        seed = block.seed
        public_key = block.public_key
        return public_key.verify(_hash, seed)

    def committee_vote(self, r, s, t_step):
        self.votes = []
        _hash, j, seed = self.is_committee_member(r, s, t_step)

        if s == 1:
            if self.proposed_block:
                self.print_proposal_message()
                payload_split = self.proposed_block[0][0].payload.split(b' || ')
                prev_hash = payload_split[0]
                curr_hash = payload_split[1]
                _message = b' || '.join([prev_hash, curr_hash, bytes(
                    [r]), bytes([s]), bytes([j]), _hash])  # vote block
            else:
                prev_hash = hashlib.sha256(
                    self.blockchain.get_last_block()).digest()
                _message = b' || '.join(
                    [prev_hash, bytes([r]), bytes([s]), b'Empty', _hash])
        else:
            curr_hash = self.r
            prev_hash = hashlib.sha256(
                self.blockchain.get_last_block()).digest()
            if curr_hash == b'Empty':
                _message = b' || '.join(
                    [prev_hash, bytes([r]), bytes([s]), curr_hash, _hash])
            else:
                _message = b' || '.join([prev_hash, curr_hash, bytes(
                    [r]), bytes([s]), bytes([j]), _hash])  # vote block

        if self.is_member:
            vote_msg = Message('NON_BLOCK', _message, self.public_key,
                               self.private_key.sign(_message), seed)
            return vote_msg

    def receive_vote(self, message):
        if message.id not in self.rcved_msgs:
            self.rcved_msgs.add(message.id)
            if message.verify():
                self.votes.append(message)
                return message

    def get_votes_count(self, t_step):
        threshold_vote = (2/3)*t_step
        votes_count = Counter()
        for message in self.votes:
            if self._verify_sortition(message):
                payload_split = message.payload.split(b' || ')
                vote = payload_split[-2]
                _key = payload_split[1]
                if vote == b'Empty':
                    _key = b'Empty'
                    vote = 1
                else:
                    vote = int.from_bytes(vote, byteorder='big', signed=False)
                votes_count[_key] += vote

        for _key, vote in votes_count.items():
            print("Step: {}, Node: {}, Block: {}, Vote: {}".format(self.step, self.id,_key, vote))
        
        for _key, vote in votes_count.items():
            if vote > threshold_vote:
                return _key, False

        TIMEOUT = len(self.votes) == 0
        return (b'Empty', TIMEOUT)

    def count_vote(self, t_step):
        return self.get_votes_count(t_step)

    def common_coin(self, r, s):
        minhash = math.pow(2, self.hash_len)
        for message in self.votes:
            if self._verify_sortition(message):
                payload_split = message.payload.split(b' || ')
                _hash = payload_split[-1]
                vote = payload_split[-2]
                vote = int.from_bytes(vote, byteorder='big', signed=False)
                for j in range(1, vote):
                    _h = self.private_key.sign(_hash + bytes([j]))
                    _h = int.from_bytes(_h, byteorder='big', signed=False)
                    if _h < minhash:
                        minhash = _h
        return minhash % 2
