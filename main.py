import sys
import os
import functools as ftool
import operator as op
import re
from regex import *

class Node:
    """Classe that defines a node. Could be a fact or an operation"""

    operations = {
        '+' : op.and_,
        '|' : op.or_,
        '^' : op.xor,
        '!' : op.not_
    }

    def __init__(self, symbol, type):
        """
        type :  0 = fact
                1 = operator
                2 = implies
        """
        self.symbol = symbol
        self.type = type
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
        if self.type == 1:
            for node in self.links:
                if node.type == 1 and node.state == None and node is not caller:                  
                    node.resolve(self)
                print(node.symbol)
            toResolve = [node for node in self.links if node is not caller]
            # print([n.symbol for n in toResolve if True])
            self.state = ftool.reduce(Node.operations[self.symbol], [n.state for n in toResolve if True])
        elif self.type == 2 and self.state == None:
            toResolve = [node for node in self.links if node is not caller]
            # print([n.symbol for n in toResolve if True])
            for ops in toResolve : ops.resolve(self)
            if len(toResolve) == 1 :
                self.state = toResolve[0].state
        elif self.state == None:
            for node in [node for node in self.links if node is not caller]:
                self.state = node.resolve(self)
        return self.state
    
def parenthese_match(process):
    return process.count('(') == process.count(')')

def build_from_op(facts, expr, op, regex):
    naming_ref = {
        '+' : 'AND',
        '|' : 'OR',
        '^' : 'XOR',
        '!' : 'NOT'
    }
    matches = re.finditer(regex, expr)
    for matchNum, match in enumerate(matches):
        split = match.group().split(op)
        left = split[0]
        right = split[1]
        if left != '' :
            if left not in facts :
                facts[left] = Node(left, 0)
        if right not in facts :
            facts[right] = Node(right, 0)
        op_name = naming_ref[op] + left + right
        if op_name not in facts:
            facts[op_name] = Node(op,1)
        if left != '' : facts[op_name].add_node(facts[left])
        facts[op_name].add_node(facts[right])
        # print(op_name, facts[op_name].symbol)
        # for n in facts[op_name].links:
        #     print(n.symbol)
        expr = expr.replace(match.group(), op_name)
    return expr
    
    
A = Node('A', 0)
B = Node('B', 0)
C = Node('C', 0)
D = Node('D', 0)

EQ1 = Node('=>', 2)
OR1 = Node('|', 1)
AND1 = Node('+', 1)
XOR1 = Node('^', 1)

A.add_node(OR1)
OR1.add_node(AND1)
B.add_node(AND1)
C.add_node(AND1)

EQ1.add_node(OR1)

D.add_node(EQ1)

A.change_state(False)
B.change_state(False)
C.change_state(True)

facts = {}
with open(sys.argv[1]) as f :
    for line in f :
        com = line.find('#')
        if com > 0 :
            process = line[:com]
        elif com < 0 :
            process = line.rstrip()
        if com and process != '':
            rule_match = re.match(rule_regex, process)
            fact_match = re.match(fact_regex, process)
            query_match = re.match(query_regex, process)
            if not rule_match and not fact_match and not query_match or not parenthese_match(process): 
                print("Wrong format :", process)
            else:
                 process = re.sub('[\s+]', '', process)


expr = "A+!B|D^F+C"


expr = build_from_op(facts, expr,'+', and_regex)
expr = build_from_op(facts, expr,'^', xor_regex)
expr = build_from_op(facts, expr,'|', or_regex)



for key,val in facts.items():
    print(key, val.symbol)
    for l in val.links:
        print('\t', l.symbol)
print('*************************')
