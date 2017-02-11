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
        n = self.data.graph.number_of_nodes()
        a = nx.adjacency_matrix(self.data.graph, weight=None).todense()  # adjacent matrix
        weights = nx.adjacency_matrix(self.data.graph, weight='weight').todense()  # infection probability
        mu = np.zeros(n)  # recover probability
        diameter = 2*nx.diameter(self.subgraph)
        likelihoods = {}  # the likelihood, P(o|i), in Eq. 21.
        epsilon = 0
        ps = np.zeros([diameter + 1, n])  # the probability nodes i is susceptible at time t
        pr = np.zeros([diameter + 1, n])  # the probability nodes i is recovered
        pi = np.zeros([diameter + 1, n])  # the probability nodes i is infected
        theta = np.ones([n, n])  # theta[k][i] as the probability that the infection signal has not been passed
        # from node k to node i up to time t in the dynamics Di
        phi = np.zeros([n, n])
        pij_s = np.zeros([n, n])
        pij_s_previous = np.zeros([n, n])

        for s in self.subgraph.nodes():
            ps[:, :] = 0
            pr[:, :] = 0
            pi[:, :] = 0
            theta[:, :] = 1
            phi[:, :] = 0
            pij_s[:, :] = 0
            """initialize"""
            for i in self.data.graph.nodes():
                if i == s:
                    pi[0][self.data.node2index[i]] = 1
                    phi[self.data.node2index[i]][:] = 1
                    ps[0][self.data.node2index[i]] = epsilon
                else:
                    ps[0][self.data.node2index[i]] = 1
                pij_s[self.data.node2index[i]] = ps[0]

            likelihoods[s] = np.ones([diameter + 1])
            t = 0
            while t < diameter:
                """estimate the probabilities, P_s P_r P_I at time t"""
                t += 1
                theta -= np.multiply(weights, phi)
                # print theta
                # print '======'
                # print np.multiply(ps[0], np.exp((np.dot(a, np.log(theta))).diagonal()))
                for i in np.arange(n):
                    ps[t][i] = ps[0][i]
                    for k in np.arange(n):
                        if a[i,k]>0:
                            ps[t][i] *= theta[k,i]
                # print ps[t]

                # ps[t] = np.multiply(ps[0], np.exp((np.dot(a, np.log(theta))).diagonal()))
                # pr[t] = pr[t-1] + np.multiply(mu, pi[t-1])
                pr[t] = 0  # nodes only have two states: susceptible, infected
                pi[t] = 1 - ps[t] - pr[t]

                pij_s_previous[:, :] = pij_s[:, :]
                for i in np.arange(n):
                    denominator = np.multiply(theta[:, i], a[i, :])
                    denominator[np.where(denominator == 0)] = 1
                    pij_s[i] = np.divide(ps[t, i], denominator)

                """compute the likelihood by Eq. 21"""
                for v in self.data.graph.nodes():
                    if v in self.subgraph.nodes():
                        likelihoods[s][t] *= pi[t][self.data.node2index[v]]
                    else:
                        likelihoods[s][t] *= ps[t][self.data.node2index[v]]

                phi = np.multiply(np.multiply(1 - weights, 1 - mu), phi) - (pij_s - pij_s_previous)

        """select t0 to maximizes the partition function Z(t) = \sum_{node i}{P(o|i)}"""
        max_zt = -1
        t0 = 0
        # print likelihoods, diameter
        for t in np.arange(1, diameter + 1):
            zt = np.sum(np.asarray(likelihoods.values())[:, t])
            # print zt
            if zt > max_zt:
                max_zt = zt
                t0 = t

        centrality = {}
        for v in self.subgraph.nodes():
            centrality[v] = likelihoods[v][t0]
        nx.set_node_attributes(self.subgraph, 'centrality', centrality)
        return self.sort_nodes_by_centrality()
