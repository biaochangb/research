"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/2/22.
"""

# coding=utf-8
import data

if __name__ == '__main__':

    ratio_infected = 0.3
    input_file = "../data/small-world.ws.v100.e500.gml"
    output_file = "../data/simulation/small-world.ws.v100.e500.gml"

    ratio_infected = 0.03
    input_file = "../data/power-grid.gml"
    output_file = "../data/simulation/power-grid.gml"
    d = data.Graph(input_file, weighted=1)
    d.generate_random_graph(200)

    #d.generate_infected_subgraph(output_file, ratio_infected)