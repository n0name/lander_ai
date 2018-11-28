import random
from enum import Enum

class NodeType(Enum):
    INPUT = 0 
    OUTPUT = 1
    HIDDEN = 2

class Node:
    def __init__(self, tp):
        self.tp = tp
        self.value = 0
        self.connected_to = set()

class Connection:
    def __init__(self, in_node, out_node, weight, enabled, innovation):
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.enabled = enabled
        self.innovation = innovation

class Genome:
    def __init__(self, num_inputs, num_outputs):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.nodes = []
        for _ in range(num_inputs):
            self.nodes.append(Node(NodeType.INPUT))
        for _ in range(num_outputs):
            self.nodes.append(Node(NodeType.OUTPUT))
        
        self.connections = []
        self.cur_innovation = -1

    def save(self, file_name):
        pass
    def load(self, file_name):
        pass

    def get_innovation(self):
        self.cur_innovation += 1
        return self.cur_innovation

    def random_enabled_connection(self, max_tries):
        if len(self.connections) == 0:
            return None
        conn = random.choice(self.connections)
        tries = max_tries
        while not conn.enabled and tries >= 0:
            conn = random.choice(self.connections)
            tries -= 1

        if tries < 0:
            return None

        return conn

    def add_node(self, max_tries=4):
        conn = self.random_enabled_connection(max_tries)
        if conn is None:
            return False
        conn.enabled = False
        new_node = Node(NodeType.HIDDEN)
        self.nodes.append(new_node)
        new_node_id = len(self.nodes) - 1
        self.connections.append(Connection(conn.in_node, new_node_id, 1, True, self.get_innovation()))
        self.connections.append(Connection(new_node_id, conn.out_node, conn.weight, True, self.get_innovation()))
        new_node.connected_to.add(conn.out_node)
        self.nodes[conn.in_node].connected_to.add(new_node_id)

        return True

    def add_connection(self):
        possible_connections = []
        for i in range(len(self.nodes)):
            others = set(range(self.num_inputs, len(self.nodes)))
            for o in (others - self.nodes[i].connected_to):
                if o == i:
                    continue
                possible_connections.append((i, o))

        if len(possible_connections) == 0:
            return False
        (in_node, out_node) = random.choice(possible_connections)
        self.connections.append(Connection(in_node, out_node, random.random(), True, self.get_innovation()))
        self.nodes[in_node].connected_to.add(out_node)
        return True

    def modify_weight(self, max_tries=4):
        conn = self.random_enabled_connection(max_tries)
        if conn is None:
            return False

        new_weight = random.random()
        mix_param = random.random() / 2 # [0, 0.5)
        conn.weight = mix_param * conn.weight + (1 - mix_param) * new_weight
        return True

    def mutate(self):
        chance = random.random()
        if chance <= 0.05:                  # 5% chance
            if not self.add_node():
                self.add_connection()
        elif chance <= 0.2:                 # 15% chance 
            if not self.add_connection():
                self.modify_weight()
        else:
            if not self.modify_weight():
                self.add_connection()

    def eval(self, vals):
        if len(vals) != self.num_inputs:
            raise ValueError("Invalid number of parameters passed to genome")

        #TODO: Zero out all values ?

        for v, n in zip(vals, self.nodes[:self.num_inputs]):
            n.value = v

        for c in self.connections:
            if not c.enabled:
                continue
            self.nodes[c.out_node].value += self.nodes[c.in_node].value * c.weight

        return tuple([n.value for n in self.nodes[self.num_inputs: self.num_inputs + self.num_outputs]])