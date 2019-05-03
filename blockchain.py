class BlockChain:
    def __init__(self):
        self.chain = [
            b'We are building the best Algorand Discrete Event Simulator']

    def __repr__(self):
        s = ''
        for _m in self.chain:
            s += str(_m) + '\n'
        return s
        
    def add_block(self, block):
        self.chain.append(block)
        
    def get_last_block(self):
        return self.chain[-1]
    
