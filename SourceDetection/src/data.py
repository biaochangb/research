"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/7.
"""

# coding=utf-8
import networkx as nx
import random


class Graph:
    """@type graph: nx.Graph"""

    def __init__(self, path='', comments='#', weighted=0):
        """Read a graph from a file.

          Parameters
          ----------
          path : file or string
             File or filename to read.
          comments : string, optional
             The character used to indicate the start of a comment..
        """
        if weighted == 0:
            if path.endswith('.gml'):
                self.graph = nx.read_gml(path)
            elif path.endswith('.txt'):
                self.graph = nx.read_edgelist(path, comments=comments)
            self.set_weight_random()
        elif weighted == 1:
            if path.endswith('.gml'):
                self.graph = nx.read_gml(path)
            elif path.endswith('.txt'):
                self.graph = nx.read_weighted_edgelist(path, comments=comments)
            self.set_weight_random()

    def set_weight_random(self):
        """  set edges with random weights
        """
        a = {e: random.random() for e in self.graph.edges_iter()}
        nx.set_edge_attributes(self.graph, 'weight', a)

    def set_weight_shunt(self):
        """  weight_i =  1/degree(i)
        """
