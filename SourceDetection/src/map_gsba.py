"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/18.
"""

# coding=utf-8

import networkx as nx

import method
import rumor_center
import decimal

class GSBA(method.Method):
    """detect the source with Greedy Search Bound Approximation.
        Please refer to the my paper for more details.
    """

    rc = ''
    prior = ''

    def detect(self):
        """detect the source with GSBA.

        Returns:
            @rtype:int
            the detected source
        """
        self.reset_centrality()
        self.rc = rumor_center.RumorCenter(self.data)
        self.rc.detect()
        self.prior = nx.get_node_attributes(self.subgraph, 'centrality')
        if self.data.debug:
            print self.prior
            print self.data.subgraph.edges()
            print self.data.weights
        self.rc.reset_centrality()

        p_sigma_upper = {}  # upper bound of the probability of a permitted permutation
        infected_nodes = self.subgraph.nodes()
        n = len(infected_nodes)
        for v in infected_nodes:
            """find the approximate upper bound by greedy searching"""
            upper = 0
            included = set()
            neighbours = set()
            included.add(v)
            neighbours.add(v)
            likelihood = 1
            w = {} # effective propagation probabilities: node->w
            w_key_sorted = []
            w[v] = 1
            w_key_sorted.append(v)
            while len(included)<n:
                w_sum = sum([w[j] for j in neighbours])
                u = w_key_sorted.pop()  # pop out the last element from w_key_sorted with the largest w
                likelihood *= w[u]/w_sum
                included.add(u)
                neighbours.remove(u)
                new = nx.neighbors(self.data.graph, u)
                for h in new:
                    if h in included:
                        continue
                    # compute w for h
                    h_neighbor = nx.neighbors(self.data.graph, h)
                    w_h = 1
                    for be in included.intersection(h_neighbor):
                        w_h *= 1-self.data.get_weight(h, be)
                    w[h] = 1 - w_h
                    """insert h into w_key_sorted, ranking by w from small to large"""
                    if h in infected_nodes:
                        k = 0
                        while k<len(w_key_sorted):
                            if w[w_key_sorted[k]]>w[h]:
                                break
                            k += 1
                        if h in w_key_sorted:
                            w_key_sorted.remove(h)
                        w_key_sorted[k:k] = [h]
                neighbours = neighbours.union(new)
            self.prior[v] = self.prior[v]*decimal.Decimal(likelihood)*self.prior[v]
            #self.prior[v] = self.prior[v]*decimal.Decimal(1)*self.prior[v]
        nx.set_node_attributes(self.subgraph, 'centrality', self.prior)
        return self.sort_nodes_by_centrality()

