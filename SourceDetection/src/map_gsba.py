"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/18.
"""

# coding=utf-8

import method
import rumor_center
import networkx as nx


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
        if self.data.debug: self.prior
        self.rc.reset_centrality()

        p_sigma_upper = {}  # upper bound of the probability of a permitted permutation

        for v in self.subgraph.nodes():
            """find the approximate upper bound by greedy searching"""
            upper = 0
            included = set()
            waiting = set()
            waiting.add(v)
            # while len(waiting)>=1:
            #     for v in waiting:
            #         v


        return []

