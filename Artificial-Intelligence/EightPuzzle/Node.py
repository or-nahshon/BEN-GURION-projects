node_counter = 0

class Node:
    #in our case the nodes rep.
    # the counties (only used during Astar algorithm for keeping the scores of f,g,h)
    def __init__(self, problem):
        global node_counter
        node_counter += 1
        self.id = node_counter
        self.problem = problem
        self.parent = None
        self.neighbors = None
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.problem == other.problem

    def __hash__(self):
        return self.id

    def __str__(self):
        return str(self.problem)



    def __lt__(self, other):
        return self.id < other.id

    def updateNodeInfo(self, other):#updates parent, f,g
        self.g = other.g + 1
        self.f = self.g + self.h
        self.parent = other

    def getPath(self):
        path = []
        node = self
        while node:
            path.append(node)
            node = node.parent
        return path[::-1]

global goalBoard_node
goalBoard_node = Node(problem = [[1, 2, 3], [4, 5, 6], [7, 8, 0]])