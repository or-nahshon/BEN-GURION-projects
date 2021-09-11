import networkx as nx
import matplotlib.pyplot as plt

# Defining a Class
class GraphVisualization:

    def __init__(self):
        # visual is a list which stores all
        # the set of edges that constitutes a
        # graph
        self.visual = []

        # addEdge function inputs the vertices of an

    # edge and appends it to the visual list
    def addEdge(self, a, b):
        temp = [a, b]
        self.visual.append(temp)

        # In visualize function G is an object of

    # class Graph given by networkx G.add_edges_from(visual)
    # creates a graph with a given list
    # nx.draw_networkx(G) - plots the graph
    # plt.show() - displays the graph
    def visualize(self):
        G = nx.Graph()
        G.add_edges_from(self.visual)
        nx.draw_networkx(G, node_size=800, )
        plt.show()

    # Driver code


G = GraphVisualization()
for i in range(1,5):
    for j in range(1, 5):
        for k in range(1,5):
            if k != j:
                G.addEdge((i,j), (i,k))
            if k !=i:
                G.addEdge((i, j), (k,j))
            for m in range(1,5):
                if abs(i-j)==abs(k-m):
                    G.addEdge((i, j), (k, m))
                if abs(i+j)==abs(k+m):
                    G.addEdge((i, j), (k, m))
G.visualize()