#!/usr/bin/env python
import subprocess

import ubg_data_toolbox.dirtree as dirtree
import ubg_data_toolbox.dirtree_graph as dg

tree = dirtree.tree
dg.write_graph_to_file('dirtree.dot', tree)

subprocess.call('dot -Tpng -o dirtree.png dirtree.dot', shell=True)
