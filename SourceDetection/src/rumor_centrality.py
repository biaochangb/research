"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/8.
"""

# coding=utf-8

import networkx as nx
from data import *
from decimal import *
import math


class RumorCentrality:
    """
        detect the source with Rumor Centrality.
        Refer to
        Shah D, Zaman T. Detecting sources of computer viruses in networks: theory and experiment[J].
        ACM SIGMETRICS Performance Evaluation Review, 2010, 38(1): 203-214.
    """

    visited = set()  # node set
    bfs_tree = nx.Graph()
    source = ''

    def detect(self, graph):
        """detect the source with Rumor Centrality.
        Args:
            @type graph: nx.Graph
        Returns:
            @rtype:int
            the detected source
        """
        if graph.number_of_nodes() == 0:
            print 'graph.number_of_nodes =0'
            return
        self.source = graph.nodes()[0]  # the initial node
        self.bfs_tree = nx.bfs_tree(graph, self.source)
        self.visited.clear()
        self.get_number_in_subtree(self.source)
        self.visited.clear()
        self.get_centrality(self.source)
        result = nx.get_node_attributes(self.bfs_tree, 'centrality')
        result = sorted(result.items(), key=lambda d: d[1], reverse=True)
        return result

    def get_centrality(self, u):
        """
        get centralities for all nodes by passing a message from the root to the children.
        Args:
            u:
        """
        self.visited.add(u)
        centrality = 0
        if u == self.source:
            """p is the root node in the bfs_tree."""
            centrality = math.factorial(self.bfs_tree.number_of_nodes()) \
                         / nx.get_node_attributes(self.bfs_tree, 'cumulativeProductOfSubtrees')[u]
        else:
            parent = nx.get_node_attributes(self.bfs_tree, 'parent')[u]
            numberOfNodesInSubtree = nx.get_node_attributes(self.bfs_tree, 'numberOfNodesInSubtree')[u]
            centrality = nx.get_node_attributes(self.bfs_tree, 'centrality')[parent] * numberOfNodesInSubtree / (
                self.bfs_tree.number_of_nodes() - numberOfNodesInSubtree)
        nx.set_node_attributes(self.bfs_tree, 'centrality', {u: centrality})

        children = nx.all_neighbors(self.bfs_tree, u)
        for c in children:
            if c not in self.visited:
                self.get_centrality(c)

    def get_number_in_subtree(self, p):
        """
        passing messages from children nodes to the parent, to get the number of nodes in the subtree rooted by p,
        and the cumulative product of the size of the subtrees of all nodes in p' subtree
        Args:
            p: parent node
        Returns:
            @rtype:Decimal()
        """
        self.visited.add(p)
        numberOfNodesInSubtree = 1  # for node p
        cumulativeProductOfSubtrees = Decimal(1)  # for node p

        children = nx.all_neighbors(self.bfs_tree, p)
        for u in children:
            if u not in self.visited:
                nx.set_node_attributes(self.bfs_tree, 'parent', {u: p})
                self.get_number_in_subtree(u)
                numberOfNodesInSubtree += nx.get_node_attributes(self.bfs_tree, 'numberOfNodesInSubtree')[u]
                cumulativeProductOfSubtrees *= nx.get_node_attributes(self.bfs_tree, 'cumulativeProductOfSubtrees')[u]
        cumulativeProductOfSubtrees *= numberOfNodesInSubtree
        nx.set_node_attributes(self.bfs_tree, 'numberOfNodesInSubtree', {p: numberOfNodesInSubtree})
        nx.set_node_attributes(self.bfs_tree, 'cumulativeProductOfSubtrees', {p: cumulativeProductOfSubtrees})
