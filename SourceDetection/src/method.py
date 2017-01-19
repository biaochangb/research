"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/9.
"""

# coding=utf-8

import networkx as nx


class Method:
    """the parent class (or interface) for all detection methods, such as rumor center, jordan center.
    It defines some common functions.
    """
    graph = nx.Graph()
    source = ''  # the detected source node
    method_name = ''

    def __init__(self, graph):
        """
        Args:
            @type graph: nx.Graph
        """
        self.graph = graph
        self.method_name = self.__class__
        self.reset_centrality()

    def reset_centrality(self):
        """reset the centrality for every node."""
        centrality = {u: 0 for u in nx.nodes(self.graph)}
        nx.set_node_attributes(self.graph, 'centrality', centrality)

    def detect(self):
        """detect the source.
        Returns:
            @rtype:int
            the detected source
        """
        return self.sort_nodes_by_centrality()

    def sort_nodes_by_centrality(self):
        result = nx.get_node_attributes(self.graph, 'centrality')
        result = sorted(result.items(), key=lambda d: d[1], reverse=True)
        return result
