"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/7.
"""

# coding=utf-8
import pickle
import random

import networkx as nx


class Graph:
    graph = nx.Graph()
    node2index = {}  # index all nodes in graph, from 0 to n-1: node->index
    index2node = {}  # from index to node: index->node

    subgraph = ''  # the infected subgraph
    """@type subgraph: nx.Graph"""
    infected_nodes = set()
    weights = None

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
        self.subgraph = self.graph
        self.weights = nx.adjacency_matrix(self.graph, weight='weight').todense()
        i = 0
        for v in self.graph.nodes():
            self.node2index[v] = i
            self.index2node[i] = v
            i += 1

    def set_weight_random(self):
        """  set edges with random weights
        """
        a = {e: random.random() for e in self.graph.edges_iter()}
        # a = {e: 0.4 for e in self.graph.edges_iter()}
        nx.set_edge_attributes(self.graph, 'weight', a)

    def set_weight_shunt(self):
        """  weight_i =  1/degree(i)
        """

    def infect_from_source_IC(self, source, scheme='random'):
        """
        diffuse by the IC model.
        three most common propagation schemes: snowball, random walk and contact process
        Returns: the nodes being infected
        """
        max_infected_number = self.ratio_infected * self.graph.number_of_nodes()
        infected = set()
        activated_current = set()
        activated_next = set()
        infected.add(source)
        activated_current.add(source)
        stop = False
        if scheme == 'random':
            while stop == False and len(activated_current)>0:
                infected = infected.union(activated_current)
                for w in activated_current:
                    if stop:
                        break
                    neighbors = nx.all_neighbors(self.graph, w)
                    for u in neighbors:
                        if u not in infected:
                            weight = self.weights[self.node2index[w], self.node2index[u]]
                            if random.random() <= weight:
                                """u is infected successfully"""
                                infected.add(u)
                                activated_next.add(u)
                                if len(infected)>=max_infected_number or (len(infected)>= self.graph.number_of_nodes()):
                                    stop = True
                                    break
                activated_current = activated_next.copy()
                activated_next.clear()

        elif scheme == 'snowball':
            while (waiting.__len__() <= max_infected_number) and (waiting.__len__() <= self.graph.number_of_nodes()):
                for w in waiting:
                    neighbors = nx.all_neighbors(self.graph, w)
                    for u in neighbors:
                        if u not in infected:
                            infected.add(u)
                waiting = infected
        self.subgraph = self.graph.subgraph(infected)
        return infected

    def infect_from_source_SI(self, source, scheme='random'):
        """
        diffuse by the SI model.
        three most common propagation schemes: snowball, random walk and contact process
        Returns: the nodes being infected
        """
        max_infected_number = self.ratio_infected * self.graph.number_of_nodes()
        infected = set()
        waiting = set()
        infected.add(source)
        waiting.add(source)
        stop = False
        if scheme == 'random':
            while stop == False and (waiting.__len__() < max_infected_number) and (
                        waiting.__len__() < self.graph.number_of_nodes()):
                for w in waiting:
                    if stop:
                        break
                    neighbors = nx.all_neighbors(self.graph, w)
                    for u in neighbors:
                        if u not in infected:
                            weight = self.weights[self.node2index[w], self.node2index[u]]
                            if random.random() <= weight:
                                """u is infected successfully"""
                                infected.add(u)
                        if len(infected) >= max_infected_number:
                            stop = True
                            break
                waiting = infected.copy()
        elif scheme == 'snowball':
            while (waiting.__len__() <= max_infected_number) and (waiting.__len__() <= self.graph.number_of_nodes()):
                for w in waiting:
                    neighbors = nx.all_neighbors(self.graph, w)
                    for u in neighbors:
                        if u not in infected:
                            infected.add(u)
                waiting = infected
        self.subgraph = self.graph.subgraph(infected)
        return infected

    def generate_random_graph(self, size):
        """
        Graph parameters:
            small-world.ws.v500.e1000.gml: 5, 0.3
            small-world.ws.v500.e2500.gml: 10, 0.3
            small-world.ws.v200.e400.gml: 5 0.3
        """

        # file = "../data/karate_club.gml"
        # g = nx.karate_club_graph()

        g = nx.connected_watts_strogatz_graph(size, 5, 0.3)
        file = "../data/small-world.ws.v%s.e%s.gml" % (g.number_of_nodes(), g.number_of_edges())

        g = nx.barabasi_albert_graph(500, 2)
        file = "../data/scale-free.ba.v%s.e%s.gml" % (g.number_of_nodes(), g.number_of_edges())

        # g = nx.read_edgelist("../data/power.gml", comments='#')
        # file = "../data/power-grid.gml"

        a = {e: random.random() for e in g.edges_iter()}
        nx.set_edge_attributes(g, 'weight', a)
        print g.number_of_nodes(), g.number_of_edges(), file
        nx.write_gml(g, file)

        # nx.draw_circular(g)
        # plt.show()

    def generate_infected_subgraph(self, output_file_prefix, ratio_infected, scheme='random'):

        self.ratio_infected = ratio_infected
        i = 0
        for v in self.graph.nodes():
            self.infect_from_source_SI(v, scheme=scheme)
            """prefix+numberOfInfectedNodes+source"""
            output_file = "%s.i%s.s%s.subgraph" % (output_file_prefix, self.subgraph.number_of_nodes(), i)
            print output_file, self.subgraph.number_of_nodes()
            writer = open(output_file, "w")
            pickle.dump(self, writer)
            writer.close()
            i += 1


if __name__ == '__main__':
    ratio_infected = 0.3
    input_file = "../data/small-world.ws.v100.e500.gml"
    output_file = "../data/simulation/small-world.ws.v100.e500.gml"
    d = Graph(input_file, weighted=1)
    d.generate_random_graph(100)

    # d.generate_infected_subgraph(output_file, ratio_infected)
