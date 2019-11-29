import random
import layers

class NodeData():
    def __init__(self, id, network, nodes):
        self.id = id
        self.battery = 100
        self.battery_table = [-1]*15
        self.network = network
        self.nodes = nodes

class NodeManager():
    """
    Creates a random network of nodes
    """
    def __init__(self, num_nodes, sparcity, max_connections, router_ratio):
        """
        Arguments
            num_nodes - number of nodes in the network
            sparcity - number from [0, 1] which represents the density of connections in the network
            max_connections - maximum number of connections a node can have
        """
        self.num_nodes = num_nodes
        self.sparcity = sparcity
        self.router_ratio = router_ratio
        self.max_connections = max_connections
        self.adjacency_matrix = [[0 for i in range(num_nodes)] for j in range(num_nodes)]

    def CreateNetwork(self):
        """
        Creates a network from the parameters
        Returns a list of the created nodes and an adjacency matrix of their connections
        """
        nodes = []
        added_nodes = [[0, 0]]

        node_data = NodeData(0, self.adjacency_matrix, nodes)

        first_class_list = [layers.LinkLayer, layers.NetworkingLayer, layers.TransportLayer, layers.ApplicationLayer]
        first_args_list = [layers.LinkLayerArgs(), layers.NetworkingLayerArgs(), layers.TransportLayerArgs(), layers.ApplicationLayerArgs()]
        first_layer_stack = layers.create_layers(node_data, first_class_list, first_args_list)

        nodes.append(first_layer_stack)
        for toAdd in range(1, self.num_nodes):
            # Gauranteed to connect to at least one node
            if len(added_nodes) == 0:
                rand_index = random.randint(0, self.num_nodes - 1)
            rand_index = random.randint(0, len(added_nodes) - 1)
            added_nodes[rand_index][1] += 1
            neighbor = added_nodes[rand_index][0]
            if added_nodes[rand_index][1] >= self.max_connections:
                del added_nodes[rand_index]
            self.adjacency_matrix[toAdd][neighbor] = 1
            self.adjacency_matrix[neighbor][toAdd] = 1
            added_nodes.append([toAdd, 1])

            node_data = NodeData(toAdd, self.adjacency_matrix, nodes)

            # Chance to be a router or sensor application
            if random.random() < self.router_ratio:
                class_list = [layers.LinkLayer, layers.NetworkingLayer]
                args_list = [layers.LinkLayerArgs(), layers.NetworkingLayerArgs()]
                layer_stack = layers.create_layers(node_data, class_list, args_list)
                nodes.append(layer_stack)
            else:
                class_list = [layers.LinkLayer, layers.NetworkingLayer, layers.TransportLayer, layers.ApplicationLayer]
                args_list = [layers.LinkLayerArgs(), layers.NetworkingLayerArgs(), layers.TransportLayerArgs(), layers.ApplicationLayerArgs()]
                layer_stack = layers.create_layers(node_data, class_list, args_list)
                nodes.append(layer_stack)

            # Try to connect to other nodes with some probability
            toAdd_index = self.num_nodes
            for i in range(len(added_nodes)):
                if toAdd == added_nodes[i][0]:
                    toAdd_index = i
            otherNode_index = 0
            length = len(added_nodes)
            while otherNode_index < length:
                if random.random() < self.sparcity:
                    if otherNode_index == toAdd_index or self.adjacency_matrix[toAdd][added_nodes[otherNode_index][0]] != 0:
                        otherNode_index += 1
                        continue
                    added_nodes[otherNode_index][1] += 1
                    added_nodes[toAdd_index][1] += 1
                    neighbor = added_nodes[otherNode_index][0]
                    if added_nodes[otherNode_index][1] >= self.max_connections:
                        if added_nodes[toAdd_index][1] >= self.max_connections:
                            added_nodes[otherNode_index][1] -= 1
                            added_nodes[toAdd_index][1] -= 1
                            otherNode_index += 1
                            continue
                        del added_nodes[otherNode_index]
                        if otherNode_index < toAdd_index:
                            toAdd_index -= 1
                        otherNode_index -= 1
                    if added_nodes[toAdd_index][1] >= self.max_connections:
                        del added_nodes[toAdd_index]
                        otherNode_index = self.num_nodes
                    self.adjacency_matrix[toAdd][neighbor] = 1
                    self.adjacency_matrix[neighbor][toAdd] = 1
                otherNode_index += 1
                length = len(added_nodes)
        return nodes, self.adjacency_matrix