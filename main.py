import random

from config import get_config

from event_simulator import Event, EventSimulator
from node import Node
from message import Message
from network import Network


def simulation(des, net, config):
    t_proposer = 5
    t_step = 32
    t_final = 32
    _round = 0
    step = 0
    total_j = 0.0
    MAX_STEPS = 10
    s_dash = None
    final_block_count = 0
    calculate_flag = False

    ev = des.get_next_event()
    while ev:
        # print(ev)
        node = ev.node
        _type = ev.type
        current_time = ev.timestamp
        if _type == 'PRIORITY_MESSAGE':
            _t = current_time + 33000
            des.add_event(Event(_t, 'CAST_VOTE', node))
            _message = node.create_priority_message(
                node.round, node.step, t_proposer)
            _t = current_time + 3000
            des.add_event(Event(_t, 'CREATE_BLOCK_PROPOSAL', node))
            if _message is not None:
                
                if config.exp2 and calculate_flag != True:
                   calculate_flag = False
                   _t = current_time + 100
                   des.add_event(Event(_t, 'CALCULATE'))

                # _t = current_time + 3000
                # des.add_event(Event(_t, 'CREATE_BLOCK_PROPOSAL', node))
                for rcv_node in node.neighbors:
                    _t = current_time + node.non_block_msg_delay
                    des.add_event(
                        Event(_t, 'RECEIVE_PRIORITY_MESSAGE', rcv_node, _message))
        
        if _type == 'CALCULATE':
            net.print_highest_proposer()
            break

        elif _type == 'RECEIVE_PRIORITY_MESSAGE':
            _message = node.receive_prio_msg(ev.message)
            if _message is not None:
                for rcv_node in node.neighbors:
                    _t = current_time + node.non_block_msg_delay
                    des.add_event(
                        Event(_t, 'RECEIVE_PRIORITY_MESSAGE', rcv_node, _message))

        elif _type == 'CREATE_BLOCK_PROPOSAL':
            des.remove_event('RECEIVE_PRIORITY_MESSAGE', current_time)
            _message = node.propose_block()
            if _message is not None:
                for rcv_node in node.neighbors:
                    _t = current_time + node.block_msg_delay
                    des.add_event(
                        Event(_t, 'RECEIVE_BLOCK_PROPOSAL', rcv_node, _message))

        elif _type == 'RECEIVE_BLOCK_PROPOSAL':
            _message = node.receive_block_proposal(ev.message)
            if _message is not None:
                for rcv_node in node.neighbors:
                    _t = current_time + node.block_msg_delay
                    des.add_event(
                        Event(_t, 'RECEIVE_BLOCK_PROPOSAL', rcv_node, _message))

        elif _type == 'CAST_VOTE':
            des.remove_event('RECEIVE_BLOCK_PROPOSAL', current_time)
            node.step += 1
            _message = node.committee_vote(node.round, node.step, t_step)
            _t = current_time + 3000
            des.add_event(Event(_t, 'COUNT_VOTES', node))
            if _message is not None:
                for rcv_node in node.neighbors:
                    _t = current_time + node.non_block_msg_delay
                    des.add_event(
                        Event(_t, 'RECEIVE_VOTE_MESSAGE', rcv_node, _message))

        elif _type == 'RECEIVE_VOTE_MESSAGE':
            _message = node.receive_vote(ev.message)
            if _message is not None:
                for rcv_node in node.neighbors:
                    _t = current_time + node.non_block_msg_delay
                    des.add_event(
                        Event(_t, 'RECEIVE_VOTE_MESSAGE', rcv_node, _message))

        elif _type == 'COUNT_VOTES':
            des.remove_event('RECEIVE_VOTE_MESSAGE', current_time)
            node.r, TIMEOUT = node.count_vote(t_step)

            if node.step < 2:
                des.add_event(Event(current_time, 'CAST_VOTE', node))
            else:
                node.block_hash = node.r
                des.add_event(Event(current_time, 'BINARY_BA*', node))

        elif _type == 'BINARY_BA*':
            des.add_event(Event(current_time, 'CAST_VOTE_BA*', node))

        elif _type == 'CAST_VOTE_BA*':
            _t = current_time + 3000
            if node.s_dash is None:
                node.step += 1
                _message = node.committee_vote(node.round, node.step, t_step)
                des.add_event(Event(_t, 'COUNT_VOTES_BA*', node))

            elif node.s_dash > node.step + 3 and node.step == node.s_final:
                node.s_dash = None
                _message = node.committee_vote(
                    node.round, node.s_final, t_final)
                node.block_hash = node.r
                _t = current_time + 3000
                des.add_event(Event(_t, 'FINAL_COUNT_VOTES', node))
            else:
                des.add_event(Event(_t, 'BA*_LOOP', node))
                _message = node.committee_vote(node.round, node.s_dash, t_step)

            if _message is not None:
                for rcv_node in node.neighbors:
                    _t = current_time + node.non_block_msg_delay
                    des.add_event(
                        Event(_t, 'RECEIVE_VOTE_MESSAGE', rcv_node, _message))

        elif _type == 'COUNT_VOTES_BA*':
            node.r, TIMEOUT = node.count_vote(t_step)
            case = (node.step - 3) % 3
            if case == 0:
                des.remove_event('RECEIVE_VOTE_MESSAGE', current_time)
                if node.r != b'Empty' and not TIMEOUT:
                    des.add_event(Event(current_time, 'BA*_LOOP', node))
                else:
                    if TIMEOUT:
                        node.r = node.block_hash
                    des.add_event(Event(current_time, 'CAST_VOTE_BA*', node))

            if case == 1:
                des.remove_event('RECEIVE_VOTE_MESSAGE', current_time)
                if not TIMEOUT and node.r == b'Empty':
                    des.add_event(Event(current_time, 'BA*_LOOP', node))
                else:
                    if TIMEOUT:
                        node.r = b'Empty'
                    des.add_event(Event(current_time, 'CAST_VOTE_BA*', node))

            if case == 2:
                if TIMEOUT:
                    _t = current_time + 3000
                    des.add_event(Event(_t, 'COMMON_COIN', node))
                else:
                    des.remove_event('RECEIVE_VOTE_MESSAGE', current_time)
                    if node.step + 1 < MAX_STEPS:
                        des.add_event(Event(current_time, 'CAST_VOTE_BA*', node))

        elif _type == 'COMMON_COIN':
            des.remove_event('RECEIVE_VOTE_MESSAGE', current_time)
            if node.common_coin(node.round, node.step) == 0:
                node.r = node.block_hash
            else:
                node.r = b'Empty'
            des.add_event(Event(current_time, 'CAST_VOTE_BA*', node))

        elif _type == 'BA*_LOOP':
            des.remove_event('RECEIVE_VOTE_MESSAGE', current_time)
            if node.s_dash is None:
                node.s_dash = node.step + 1
            else:
                node.s_dash += 1

            if node.s_dash <= node.step + 3 or node.step == node.s_final:
                des.add_event(Event(current_time, 'CAST_VOTE_BA*', node))
            else:
                node.block_hash = node.r
                des.add_event(Event(current_time, 'FINAL_COUNT_VOTES', node))
                node.s_dash = None

        elif _type == 'FINAL_COUNT_VOTES':
            des.remove_event('RECEIVE_VOTE_MESSAGE', current_time)
            node.r, TIMEOUT = node.count_vote(t_final)
            if node.r == node.block_hash:
                final_block_count += 1
                print("Node: {} Final block found".format(node.id))
            else:
                print("Node: {} Tentative block found".format(node.id))
            
            if final_block_count >= net.num_nodes:
                message = node.proposed_block[0][0].payload
                message = b' || '.join([message.split(b' || ')[0], node.block_hash])
                des.add_event(
                    Event(current_time, 'ADD_BLOCK',message=message))

        elif _type == 'ADD_BLOCK':
            net.blockchain.add_block(ev.message)
            print("Consensus reached on block:")
            print(ev.message)
            _round += 1
            final_block_count = 0
            if _round >= config.blocks:
                break

            for _n in net.node_list:
                _n.reset(_round)
                des.add_event(Event(current_time, 'PRIORITY_MESSAGE', _n))

        ev = des.get_next_event()
    
    if config.exp1:
        net.print_stack_sortion_stats()
    
    print(net.blockchain)


def main(config):

    net = Network(config.node)
    des = EventSimulator()

    # Creating initial events
    # PRIORITY_MESSAGE event
    for node in net.node_list:
        des.add_event(Event(0, 'PRIORITY_MESSAGE', node))

    # Main simulation loop
    simulation(des, net, config)

    


if __name__ == "__main__":
    main(get_config())
    # Initialise all nodes and neighbors
