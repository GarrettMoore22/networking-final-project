import layers
import time
from node_manager import NodeManager
import numpy as np
import packet
import sys
import fileinput
import re

def main():
    """num_nodes = 50
    max_connections = 4
    sparcity = max_connections / num_nodes
    router_ratio = 0.8"""
	if len(sys.argv) < 2:
		print ("Improper running. (EX: python3 main.py config.txt)
		return
    num_nodes, max_connections, sparcity, router_ratio = netConfig(sys.argv[1])
    nodeManager = NodeManager(num_nodes, sparcity, max_connections, router_ratio)
    nodes, network = nodeManager.CreateNetwork()
    print(np.matrix(network))
    app_layer_nodes = [(i, node) for i, node in enumerate(nodes) if len(node) == 4]

    for i, node in enumerate(app_layer_nodes):
        dest = app_layer_nodes[len(app_layer_nodes) - i - 1][0]
        data = node[1][3].get_data(dest)
        print("App layer (id = %d) get request found data: %s" % (node[0], data))


def netConfig(path):
	with open(path, 'r') as fp:
		info = fp.readlines()
		for i in info:
			print(i)
			if "num_nodes" in i:
				d = re.findall("\d+", i)
				nodes = int(d[0])
			elif "max_connections" in i:
				d = re.findall("\d+", i)
				cons = int(d[0])
			elif "router_ratio" in i:
				d = re.findall("\d+\.\d+", i)
				ratio = float(d[0])
	spar = float(cons)/nodes
	return nodes, cons, spar, ratio
		

if __name__ == '__main__':
    main()
