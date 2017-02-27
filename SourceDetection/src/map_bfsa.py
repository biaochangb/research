"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/2/27.
"""

# coding=utf-8

import networkx as nx
import numpy as np

import method


class BFSA(method.Method):
    """detect the source with Greedy Search Bound Approximation.
        Please refer to the my paper for more details.
    """
    prior = ''
    prior_detector = None
    visited = set()  # node set

    def __init__(self, prior_detector):
        method.Method.__init__(self)
        self.method_name = self.__class__, prior_detector.method_name
        self.prior_detector = prior_detector
        self.bfs_trees = {}
        self.likelihoods = {}
        self.depths = {}
        self.descendants = {}

    def detect(self):
        """detect the source with GSBA.

        Returns:
            @rtype:int
            the detected source
        """
        self.reset_centrality()
        self.prior_detector.set_data(self.data)
        self.prior_detector.detect()
        self.prior = nx.get_node_attributes(self.subgraph, 'centrality')
        print self.prior

        self.reset_centrality()
        nodes = self.subgraph.nodes()
        for v in nodes:
            self.bfs_trees[v] = nx.bfs_tree(self.subgraph, v)
            print v, self.bfs_trees[v].edges()
            self.likelihoods[v] = 0
            self.descendants[v] = {}
            self.depths[v] = {}
            self.visited.clear()
            self.find_descendants_bfs(v, v)
            #self.depths[v] = nx.single_source_dijkstra_path_length(self.bfs_trees[v], v, weight=None)
        print self.depths
        self.get_likelihood_by_BFSA(nodes, 0, len(nodes) - 1)
        posterior = {v: self.prior[v] * self.likelihoods[v] for v in nodes}
        nx.set_node_attributes(self.subgraph, 'centrality', posterior)

        return self.sort_nodes_by_centrality()

    def find_descendants_bfs(self, root, u,depth=0):
        """Find the descendants and depth for a node in self.bfs_trees[root]"""
        self.depths[root][u] = depth
        self.descendants[root][u] = set()
        self.visited.add(u)
        children = nx.all_neighbors(self.bfs_trees[root], u)
        for c in children:
            if c not in self.visited:
                self.find_descendants_bfs(root, c, depth+1)
                self.descendants[root][u].update(self.descendants[root][c])
        self.descendants[root][u].add(u)

    def get_likelihood_by_BFSA(self, nodes, p, q):
        """extends Heap's permutation generating algorithm.
        Permitted permutation: each node has a certain depth at which it will be found.

        Args:
            nodes: a list of all nodes
            p: the starting index
            q: the end index

        Returns:
        """
        if p == q:
            self.likelihoods[nodes[0]] += self.compute_likelihood(nodes)
            print nodes
        else:
            for i in np.arange(p, q + 1):
                if nodes[p] not in self.descendants[nodes[0]][nodes[i]]:
                    # Nodes[p] is not a descendant of nodes[i], so we can exchange them.
                    nodes[p], nodes[i] = nodes[i], nodes[p]
                    self.get_likelihood_by_BFSA(nodes, p + 1, q)
                    nodes[p], nodes[i] = nodes[i], nodes[p]

    def compute_likelihood(self, nodes):
        """get P(jv = v) by Equation (11);
        Args:
            nodes:

        Returns:

        """
        return 0