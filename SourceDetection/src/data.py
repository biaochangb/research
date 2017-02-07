"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/7.
"""

# coding=utf-8
import random

import networkx as nx


class Graph:
    graph = nx.Graph()
    subgraph = ''   # the infected subgraph
    infected_nodes = set()
    """@type subgraph: nx.Graph"""

    ratio_infected = 0.1  # the ratio of the number of nodes being infected
    propagation_schemes = ['snowball', 'random', 'contact']
    debug = True

    def __init__(self, path='', comments='#', weighted=0):
        """Read a subgraph from a file.

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
        self.subgraph = self.graph
    def set_weight_random(self):
        """  set edges with random weights
        """
        a = {e: random.random() for e in self.graph.edges_iter()}
        nx.set_edge_attributes(self.graph, 'weight', a)

    def set_weight_shunt(self):
        """  weight_i =  1/degree(i)
        """

    def infect_from_source_SI(self, source, scheme= 'random'):
        """
        three most common propagation schemes: snowball, random walk and contact process
        Returns: the nodes being infected
        """
        max_infected_number = self.ratio_infected * self.graph.number_of_nodes()
        infected = set()
        waiting = set()
        infected.add(source)
        waiting.add(source)
        weights = nx.get_edge_attributes(self.graph, 'weight')
        if scheme == 'random':
            while (waiting.__len__() < max_infected_number) and (waiting.__len__() < self.graph.number_of_nodes()):
                for w in waiting:
                    neighbors = nx.all_neighbors(self.graph, w)
                    for u in neighbors:
                        if u not in infected:
                            weight = 0
                            if (w, u) in weights.keys():
                                weight = weights[(w, u)]
                            else:
                                weight = weights[(u, w)]
                            if random.random() > weight:
                                """u is infected successfully"""
                                infected.add(u)
                                if self.debug:
                                    print u
                waiting = infected.copy()
        elif scheme=='snowball':
            while (waiting.__len__() <= max_infected_number) and (waiting.__len__() <= self.graph.number_of_nodes()):
                for w in waiting:
                    neighbors = nx.all_neighbors(self.graph, w)
                    for u in neighbors:
                        if u not in infected:
                            infected.add(u)
                waiting = infected
        self.subgraph = self.graph.subgraph(infected)
        return infected
