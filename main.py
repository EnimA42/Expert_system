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

    def add_node(self, node, is_on_right = False):
        if node.__class__.__name__ == self.__class__.__name__ and node not in self.links:
            self.links.append(node)
            if is_on_right == True :
                print("Double add between ",self.symbol, node.symbol)
                node.links.append(self)
        else:
            print("Linking error. {} could not be linked with {}".format(self, node))

    def change_state(self, state):
        if state.__class__.__name__ == 'bool': 
            self.state = state
        else:
            print("State assignment error")
    
    def resolve(self, caller):
        print("in", self.symbol)
        for n in self.links:
            print(n.symbol)
        if self.state != None : return self.state

        if self.type == 0:
            toResolve = [node for node in self.links if node is not caller]
            if len(toResolve) == 0 : 
                self.state = False
            else:
                state = None
                for node in toResolve:
                    state = node.resolve(self)
                    if self.state != None and state != self.state:
                        print (self.symbol, ": Error !")
                        exit(0)
                    self.state = state

        if self.type == 1:
            toResolve = [node for node in self.links if node is not caller]
            if self.symbol != '!':
                for node in toResolve : node.resolve(self)
                self.state = ftool.reduce(Node.operations[self.symbol], [n.state for n in toResolve if True])
            else:
                state = None
                for node in toResolve:
                    state = node.resolve(self)
                    if self.state != None and state != self.state:
                        print (self.symbol, ": Error !")                        
                        exit(0)
                    self.state = state
                    return not self.state
                
        if self.type == 2:
            toResolve = [node for node in self.links if node is not caller]
            state = None
            for node in toResolve:
                state = node.resolve(self)
                if self.state != None and state != self.state:
                    print (self.symbol, ": Error !")
                    exit(0)
                self.state = state       
        return self.state

    def old(self,caller):
        if self.type == 1:
            for node in self.links:
                if node.type != 0 and node.state == None and node is not caller:                  
                    node.resolve(self)                                                                                                                      
            toResolve = [node for node in self.links if node is not caller]
            if self.symbol == '!':
                self.state = not toResolve[0].state
            else:
                self.state = ftool.reduce(Node.operations[self.symbol], [n.state for n in toResolve if True])
        elif self.type == 2 and self.state == None:
            toResolve = [node for node in self.links if node is not caller]
            for ops in toResolve : ops.resolve(self)
            if len(toResolve) == 1 :
                self.state = toResolve[0].state
        elif self.state == None:
            for node in [node for node in self.links if node is not caller]:
                self.state = node.resolve(self)
#######################################################################


def parenthese_match(process):
    return process.count('(') == process.count(')')

def build_from_op(facts, expr, op, regex, is_on_right):
    naming_ref = {
        '+' : 'And',
        '|' : 'Or',
        '^' : 'Xor',
        '!' : 'Not'
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
            facts[op_name] = Node(op, 1)
        if left != '' : facts[op_name].add_node(facts[left], is_on_right)
        facts[op_name].add_node(facts[right], is_on_right)
        expr = expr.replace(match.group(), op_name)
    return expr

def build(to_process, facts, is_on_right):
    if len(to_process) == 1 and to_process not in facts:
        facts[to_process] = Node(to_process, 0)
    to_process = build_from_op(facts, to_process,'!', not_regex, is_on_right)
    while '+' in to_process:
        to_process = build_from_op(facts, to_process,'+', and_regex, is_on_right)
    to_process = build_from_op(facts, to_process,'^', xor_regex, is_on_right)
    to_process = build_from_op(facts, to_process,'|', or_regex, is_on_right)
    return to_process

def rec(s, is_on_right):
    m = re.search(r'\((\S+)\)', s)
    if m:
        expr = rec(m.group(1), is_on_right)
        s = s.replace(m.group(), expr)
    s = build(s, facts, is_on_right)
    return s

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
            if not rule_match and not fact_match and not query_match or not parenthese_match(process) or not parenthese_match(rule_match.group(1)) or not parenthese_match(rule_match.group(6)) or not parenthese_match(rule_match.group(5)): 
                print("Wrong format :", process)
            else:
                left_fact = rule_match.group(1)
                left_fact = re.sub(r'[\s]', '', left_fact)
                left_fact = rec(left_fact, False)

                right_fact = rule_match.group(6)
                right_fact = re.sub(r'[\s]', '', right_fact)
                right_fact = rec(right_fact, True)
                
                implie = rule_match.group(5)
                implie_name = "IMP" + left_fact + right_fact
                if implie_name not in facts:
                    facts[implie_name] = Node('=>', 2)

                facts[implie_name].add_node(facts[left_fact])
                facts[implie_name].add_node(facts[right_fact], True)


# expr = build(expr, facts)

print('*************************')
for key,val in facts.items():
    print(key, val.symbol)
    for l in val.links:
        print('\t', l.symbol)
print('*************************')

facts['A'].change_state(True)
facts['B'].change_state(True) 
facts['C'].change_state(False)
# facts['D'].change_state(False)
# facts['E'].change_state(True)
# facts['F'].change_state(True)
# facts['G'].change_state(True)

print("Looking for", facts['X'].symbol," :",facts['X'].resolve(facts['X']))
print("Looking for", facts['Z'].symbol," :",facts['Z'].resolve(facts['Z']))
#print(facts['Y'].resolve(facts['Y']))
print("++++++++++++++++++++")

for key,val in facts.items():print(key, val.state)
for l in facts["NotZ"].links: print (l.symbol)