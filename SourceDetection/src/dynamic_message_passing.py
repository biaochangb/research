"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/10.
"""

# coding=utf-8
import method
import networkx as nx


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
        return []
