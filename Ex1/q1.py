# or nahshon agash
# ID- 311330500

import pandas as pd

# class represents a graph
class Graph:

    # initialize
    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.graph = self.build_graph()
        self.size = len(self.graph)

    # build a graph
    def build_graph(self):
        graph = {}
        print("start build graph")
        for i in range(0, len(self.data)):
            if self.data.loc[i][0] == self.data.loc[i][1]:
                # location to itself
                distance = 0
            else:
                # location to neighbor
                distance = 1
            graph.setdefault(self.data.loc[i][0], {})[self.data.loc[i][1]] = distance
            # if the graph isnt directed so we need to add this line to add neigbhor for the other side
            #graph.setdefault(self.data.loc[i][1], {})[self.data.loc[i][0]] = distance

        print("finish build graph")
        return graph

    # get a neighbors.
    # if b - get distance from a to b
    def get(self, a, b=None):
        links = self.graph.setdefault(a, {})
        if b is None:
            return links
        else:
            return links.get(b)

# class represents a node
class Node:

    # initialize
    def __init__(self, name: str, parent):
        self.name = name
        self.parent = parent
        self.country = name.split(', ')[1]
        self.g = 0  # Distance from start node
        self.h = 0  # Distance to goal node
        self.f = 0  # Total cost

    # compare nodes
    def __eq__(self, other):
        return self.name == other.name

    # sort nodes by f
    def __lt__(self, other):
        return self.f > other.f

# there is path. now need to organized the path
def print_answer(ls, details):
    # all paths should be in same length
    lmax = 0
    sum = 0
    for key in ls.keys():
        lmax = max( lmax, len(ls[key]))
    for key in ls.keys():
        while len(ls[key]) < lmax:
            # add last location until length = lmax
            ls[key].append(ls[key][-1])
    df = pd.DataFrame(data=ls)
    # print heuristic value
    if details:
        print("the heuristic value after the first transformation is:", [df.loc[0][i] for i in range(len(ls.keys()))])
        for i in range(len(ls.keys())):
            sum += df.loc[0][i]
        print("In total:",sum)
        # remove auxiliary row
        df = df.drop(0)

    return df.values.tolist()

# find path
def find_path(starting_locations, goal_locations, search_method, detail_output):
    # create a graph based on data
    graph = Graph(path = "adjacency.csv")

    ans_final = {}

    # intertor to one selcted: start-goal
    for i in range(0, len(starting_locations)):
        start = starting_locations[i]
        goal = goal_locations[i]

        switcher = {
            1: A_star_search(graph, start, goal, detail_output),
            2: None,
            3: None}

        # run selected algorithm
        ans = switcher.get(search_method)

        if ans == False:
            # there isnt path
            return print("No path found")
        else:
            # there is path
            ans_final[i]= ans

    return print(starting_locations,*print_answer(ans_final, detail_output), sep="\n")

# A* search
def A_star_search(graph, start, end, detail_output ):

    open, closed = [], []

    # Create a start node and an goal node
    start_node = Node(start, None)
    goal_node = Node(end, None)
    # find heuristics values to goal
    heuristic = bfs(goal_node.country)

    # Add the start node to open list
    open.append(start_node)

    #loop until opn list is empty
    while len(open) > 0:
        # sort to get the node with the lowest cost first
        open.sort()
        current_node = open.pop()
        # add current node to closed list
        closed.append(current_node)

        # if we have reached the goal, recreate path
        if current_node == goal_node:
            return recreate_path(current_node, start_node, detail_output)

        neighbors = graph.get(current_node.name)
        for key, value in neighbors.items():
            neighbor = Node(key, current_node)

            # if we check the neighbor, pass
            if neighbor in closed:
                continue
            # calculate full path cost
            neighbor.g = current_node.g + value
            neighbor.h = heuristic.get(neighbor.country)
            try:
                neighbor.f = neighbor.g + neighbor.h
            except:
                # if there is not heuristic value
                neighbor.f = neighbor.g + 100000

            # Check if neighbor is in open list and if it has a lower value
            open = add_to_open(open, neighbor)

    return False

# follow nodes and recreate path
def recreate_path(current_node, start_node, detail_output):

    path = []
    # loop until reach to start-node
    while current_node != start_node:
        path.append(current_node.name)
        details_h = current_node.h
        current_node = current_node.parent
    if detail_output:
        path.append(details_h)
    # reverse path
    return path[::-1]

# Check if neighbor is in open list and if it has a lower value
def add_to_open(open, neighbor):

    for node in open:
        if neighbor == node:
            if neighbor.g < node.g:
                # replace node
                open.remove(node)
                open.append(neighbor)
            return open

    # neighbor is not in open list
    open.append(neighbor)

    return open

# Neighborhood relations between countries
def Neighbors():
    return {      'OH': ['WV', 'IN', 'MI', 'PA', 'KY'],
                  'OK': ['NM', 'CO', 'KS', 'TX', 'AR', 'MO'],
                  'OR': ['WA', 'ID', 'CA', 'NV'],
                  'IA': ['SD', 'NE', 'MO', 'IL', 'WI', 'MN'],
                  'ID': ['WA', 'OR', 'NV', 'UT', 'MT', 'WY'],
                  'IL': ['KY', 'IN', 'MO', 'IA', 'WI'],
                  'IN': ['OH', 'MI', 'KY', 'IL'],
                  'AL': ['FL', 'GA', 'TN', 'MS'],
                  'AK': [],
                  'AZ': ['CA', 'NM', 'NV', 'UT', 'CO'],
                  'AR': ['OK', 'TX', 'LA', 'MS', 'TN', 'MO'],
                  'GA': ['NC', 'SC', 'FL', 'AL', 'TN'],
                  'DE': ['PA', 'MD', 'NJ'],
                  'SD': ['WY', 'MT', 'ND', 'MS', 'LA', 'NE'],
                  'ND': ['MT', 'SD', 'MS'],
                  'HI': [],
                  'WY': ['UT', 'CO', 'ID', 'NE', 'SD', 'MT'],
                  'WA': ['OR', 'ID'],
                  'WI': ['IL', 'IA', 'MN', 'MI'],
                  'VA': ['MD', 'WV', 'KY', 'NC', 'TN','DC'],
                  'WV': ['OH', 'PA', 'MD', 'VA', 'KY'],
                  'VT': ['NH', 'NY', 'MA'],
                  'TN': ['VA', 'NC', 'GA', 'AL', 'MS', 'AR', 'KY', 'MO'],
                  'TX': ['NM', 'OK', 'AR', 'LA'],
                  'UT': ['AZ', 'NV', 'CO', 'ID', 'WY', 'NM'],
                  'LA': ['TX', 'AR', 'MA'],
                  'MT': ['ID', 'WY', 'SD', 'ND'],
                  'MO': ['NE', 'KS', 'OK', 'TN', 'KY', 'AR', 'IL', 'IA'],
                  'ME': ['NH'],
                  'MN': ['ND', 'SD', 'IA', 'WI'],
                  'MS': ['LA', 'AL', 'TN', 'AR'],
                  'MI': ['OH', 'IN', 'WI'],
                  'MA': ['NH', 'VA', 'CT', 'NY', 'RI'],
                  'MD': ['PA', 'DE', 'VA', 'WV', 'DC'],
                  'NV': ['OR', 'CA', 'AZ', 'ID', 'UT'],
                  'NE': ['WY', 'SD', 'KS', 'MO', 'CO', 'IA'],
                  'NJ': ['NY', 'PA', 'DE'],
                  'NH': ['ME', 'VT', 'MA'],
                  'NY': ['VT', 'MA', 'CT', 'NJ', 'PA'],
                  'NM': ['AZ', 'CO', 'TX', 'OK', 'UT'],
                  'FL': ['GA', 'AL'],
                  'PA': ['OH', 'NY', 'WV', 'MD', 'DE', 'NJ'],
                  'CO': ['NM', 'UT', 'WY', 'KS', 'OK', 'NE', 'AZ'],
                  'CT': ['MA', 'NY', 'RI'],
                  'CA': ['OR', 'AZ', 'NV'],
                  'KS': ['CO', 'NE', 'MO', 'OK'],
                  'KY': ['OH', 'WV', 'VA', 'TN', 'IN', 'IL', 'MO'],
                  'SC': ['NC', 'GA'],
                  'NC': ['VA', 'TN', 'SC', 'GA'],
                  'RI': ['MA', 'CT'],
                  'VI': [],
                  'PR': [],
                  'MP': [],
                  'GU': [],
                  'AS': [],
                  'DC': ['MD', 'VA']   }

# bfs-search to find heuristics value
def bfs (root, graph_search=Neighbors()):

    ans, visited, queue, queue2 = {}, set(), [root], []
    visited.add(root)
    i = 0

    # i used two queues to know when layer ending and new layer begining
    while queue or queue2:
        while queue:
            var = queue.pop(0)
            ans[var] = i

            for neighbour in graph_search[var]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue2.append(neighbour)
        i += 1
        while queue2:
            var = queue2.pop(0)
            ans[var] = i

            for neighbour in graph_search[var]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

        i += 1

    return ans

if __name__ == "__main__":

    starting_locations = ["Chicot County, AR", "Chittenden County, VT", "Rensselaer County, NY"]
    goal_locations = ["Grant County, AR", "Rensselaer County, NY", "Grant County, AR"]

    search_method = 1
    detail_output = True

    find_path(starting_locations, goal_locations, search_method, detail_output)





