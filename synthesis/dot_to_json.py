# dot_to_json_graph.py
# http://stackoverflow.com/questions/40262441/how-to-transform-a-dot-graph-to-json-graph

# Packages needed  :
# sudo aptitude install python-networkx python-pygraphviz python-pydot
#
# Syntax :
# python dot_to_json_graph.py graph.dot

import networkx as nx
import sys
import csv
import os
import re

if len(sys.argv) < 2:
    sys.stderr.write("Syntax : python %s graph.dot\n" % sys.argv[0])
    sys.exit(1)

dot_file = sys.argv[1]

G = nx.drawing.nx_pydot.read_dot(dot_file)

# Write nodes.csv
with open("nodes.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Node ID", "Label", "Gate Type"])
    for node_id, attrs in G.nodes(data=True):
        label = attrs.get("label", "").strip('"')
        if "\\n" in label:
            gate_type, inst_name = label.split("\\n", 1)
        else:
            gate_type = label
            inst_name = ""
        writer.writerow([node_id, inst_name, gate_type])

# Write edges.csv
with open("edges.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["From", "To"])
    for src, dst in G.edges():
        writer.writerow([src, dst])

