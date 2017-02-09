"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/10.
"""

# coding=utf-8
import networkx as nx
import numpy as np

import method


class DynamicMessagePassing(method.Method):
    """detect the source with DynamicMessagePassing.
        Please refer to the following paper for more details.
        Lokhov, Andrey Y., et al. "Inferring the origin of an epidemic with a dynamic message-passing algorithm."
        Physical Review E 90.1 (2014): 012801.
    """

    def detect(self):
        """detect the source with DynamicMessagePassing.

        Returns:
            @rtype:int
            the detected source
        """
        self.reset_centrality()
        nodes = self.data.node2index.values()
        n = len(nodes)
        n_i = self.subgraph.number_of_nodes()
        a = nx.adjacency_matrix(self.data.graph, weight=None).todense()  # adjacent matrix
        weights = nx.adjacency_matrix(self.data.graph, weight='weight').todense()  # infection probability
        mu = np.zeros(n)  # recover probability\
        diameter = nx.diameter(self.subgraph)
        likelihoods = {}    # the likelihood, P(o|i), in Eq. 21.

        for s in self.subgraph.nodes():
            """estimate the probabilities, P_s P_r P_I at time t"""
            ps = np.zeros([diameter+1, n])  # the probability nodes i is susceptible at time t
            pr = np.zeros([diameter+1, n])  # the probability nodes i is recovered
            pi = np.zeros([diameter+1, n])  # the probability nodes i is infected
            theta = np.ones([n, n])  # theta[k][i] as the probability that the infection signal has not been passed
            # from node k to node i up to time t in the dynamics Di
            phi = np.zeros([n, n])
            pij_s = np.zeros([n, n])
            pij_s_previous = np.zeros([n, n])

            """initialize"""
            for i in self.data.graph.nodes():
                if i == s:
                    pi[0][self.data.node2index[i]] = 1
                    phi[self.data.node2index[i]][:] = 1
                    ps[0][self.data.node2index[i]] = 0.000000000001
                else:
                    ps[0][self.data.node2index[i]] = 1
                pij_s[self.data.node2index[i]] = ps[0]

            likelihoods[s]=np.ones([diameter+1])
            t = 1
            while t <= diameter:
                theta -= np.multiply(weights, phi)
                pij_s_previous = pij_s
                pij_s = np.log(ps[0]) + (np.multiply(a, np.log(theta))).diagonal()
                pij_s = np.exp(
                    np.tile(pij_s, n).reshape(n, n).T - np.log(theta.T))  # compute according to Eq.15 in the paper
                temp = np.multiply(1 - weights, 1 - mu)
                phi = np.multiply(temp, phi) - (pij_s - pij_s_previous)

                ps[t] = np.exp(np.log(ps[0]) + (np.multiply(a, np.log(theta))).diagonal())
                #pr[t] = pr[t-1] + np.multiply(mu, pi[t-1])
                pr[t] = 0
                pi[t] = 1 - ps[t] - pr[t]

                """compute the likelihood by Eq. 21"""
                for v in self.data.graph.nodes():
                    if v in self.subgraph.nodes():
                        likelihoods[s][t] *= pi[t][self.data.node2index[v]]
                    else:
                        likelihoods[s][t] *= ps[t][self.data.node2index[v]]
        """select t0 to maximizes the partition function Z(t) = \sum_{node i}{P(o|i)}"""
        max_zt = -1
        t0 = 0
        for t in np.arange(1,diameter+1):
            zt = np.sum(np.asarray(likelihoods.values())[:,t])
            if zt > max_zt:
                max_zt = zt
                t0 = t

        centrality = {}
        for v in self.subgraph.nodes():
            centrality[v] = likelihoods[v][t0]
        nx.set_node_attributes(self.subgraph, 'centrality', centrality)
        return self.sort_nodes_by_centrality()
