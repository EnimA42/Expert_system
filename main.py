import functools as ftool
import operator as op

class Node:
    """Classe that defines a node. Could be a fact or an operation"""

    operations = {
        '+' : op.and_,
        '|' : op.or_,
        '^' : op.xor,
        '!' : op.not_
    }

    def __init__(self, symbol, isOps):
        """
        """
        self.symbol = symbol
        self.isOps = isOps
        self.state = None
        self.links = []

    def add_node(self, node):
        if node.__class__.__name__ == self.__class__.__name__ and node not in self.links:
            self.links.append(node)
            node.links.append(self)
        else:
            print("Linking error. {} could not be linked with {}".format(self, node))

    def change_state(self, state):
        if state.__class__.__name__ == 'bool': 
            self.state = state
        else:
            print("State assignment error")
    
    def resolve(self, caller):
        if self.isOps:
            toResolve = [node for node in self.links if node is not caller]
            # for node in toResolve : node.resolve(node)
            self.state = ftool.reduce(Node.operations[self.symbol], [n.state for n in toResolve if True])
        elif self.state == None:
            for node in [node for node in self.links if node is not caller]:
                self.state = node.resolve(self)
        return self.state
    

A = Node('A', False)
B = Node('B', False)
C = Node('C', False)
D = Node('D', False)

EQ1 = Node('=>', False)
OR1 = Node('|', True)
AND1 = Node('+', True)
XOR1 = Node('^', True)

A.add_node(AND1)
B.add_node(AND1)
C.add_node(AND1)

EQ1.add_node(AND1)

D.add_node(EQ1)

for node in D.links:
    print(node.symbol)

D.resolve(D)