# or nahshon agash
# ID- 311330500
import math
import random
import pandas as pd
import numpy
import copy

global path
path = "adjacency.csv"


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

    # get a neighbors.
    # if b - get distance from node to b
    def get(self, a, b=None):
        links = self.neighbors
        if b is None:
            return links
        else:
            return links.get(b)

    def getNeighbors(self):
        df = pd.read_csv(path)
        listOfNeighbors = df.loc[df['countyname'] == self.name]['neighborname']
        neighbors = []
        for neighbor in listOfNeighbors:
            if neighbor != self.name:
                neighbors.append(neighbor)
        return copy.deepcopy(neighbors)

    def getNeighborsNotChecked(self, checked):
        neighbors= self.getNeighbors()
        if len(checked) == 0 :
            return neighbors
        return [neig for neig in neighbors if (neig not in checked)]



# there is path. now need to organized the path
def print_answer(paths):
    # all paths should be in same length
    lmax =max(len(path) for path in paths)
    for path in paths:
        while len(path) < lmax:
            # add last location until length = lmax
            path.append(path[-1])
    print (numpy.transpose(paths))



# find path
def find_best_neigbhors(list_of_nodes, heuristic, checked=[], size=0):

    ls=[]
    for node in list_of_nodes:
        neighbors_not_checked = node.getNeighborsNotChecked(checked)
        if len(neighbors_not_checked) > 0:
            for neighbor in neighbors_not_checked:
                neighbor_node = Node(neighbor, node)
                neighbor_node.h = heuristic.get(neighbor_node.country)
                ls.append(neighbor_node)
    if len(ls) > 0:
        list_sorted = sorted(ls,key=lambda n: (len(n.getNeighborsNotChecked(checked)) ))
        list_sorted2 = (sorted(list_sorted, key=lambda n: (-n.h)))
        if size == 0:
            return list_sorted2

        return list_sorted2[len(list_sorted2)-(min(size, len(list_sorted2))):]

    return ls



def hill_climbing(start, goal):

    return beam_search(start, goal, k=1)

def simulated_annealing(start, goal):
    t_max=100

    goal_node = Node(goal,None)
    heuristic = clculateHeuristics(goal_node.country)
    start_node = Node(start, None)
    checked=[start]
    start_node.h = heuristic.get(start_node.country)
    current_node = start_node

    for t in range(t_max):
        if current_node == goal_node:
            return recreate_path(current_node, start_node)
        T =1-(t/t_max)

        neighbors = current_node.getNeighborsNotChecked(checked)
        if not len(neighbors):
            break
        current_node.h = heuristic.get(start_node.country)

        next = neighbors.pop(random.randrange(len(neighbors)))
        next_node = Node(next, current_node)
        try:
            next_node.h = heuristic.get(start_node.country)
        except:
            next_node.h = heuristic.get(start_node.country)

        delta= current_node.h-next_node.h

        if delta > 0:

            checked.append(next)
            current_node = next_node

        else:
            P= math.exp((delta-1)/T)+0.05
            ran=numpy.random.random()

            if ran < P:
                checked.append(next)
                current_node = next_node

    return None,None



def beam_search(start, goal, k=3):
    sideways_move=0
    max_sideways_move=50
    number_of_restart = 0
    checked = []
    start_node = Node(start, None)
    goal_node = Node(goal, None)
    heuristic = clculateHeuristics(goal_node.country)

    if start_node==goal_node:
        return recreate_path(start_node, start_node)
    checked.append(start_node.name)

    current_nodes = find_best_neigbhors([start_node], heuristic, checked, size=k)

    while number_of_restart <= 5 and current_nodes:

        if goal_node in current_nodes:
            for node in current_nodes:
                if node == goal_node:
                    return recreate_path(node, start_node)

        for node in current_nodes:
            checked.append(node.name)

        best_k_neighbhors = find_best_neigbhors(current_nodes, heuristic, checked, size=k)

        if not best_k_neighbhors:
            number_of_restart += 1
            sideways_move = 0
            current_nodes = find_best_neigbhors([start_node], heuristic, checked, size=k)

        else:
            current_nodes_temp=[]
            for node in best_k_neighbhors:

                if node.h<node.parent.h:
                    current_nodes_temp.append(node)

                elif node.h == node.parent.h:
                    sideways_move +=1
                    if sideways_move <= max_sideways_move:
                        current_nodes_temp.append(node)

            if current_nodes_temp:
                current_nodes = current_nodes_temp
            else:
                number_of_restart +=1
                sideways_move = 0
                current_nodes = find_best_neigbhors([start_node], heuristic, checked, size=k)

    return None, None


def genetic_algorithm(start, goal):
    print("hi gen")
    pass


def find_path(starting_locations, goal_locations, search_method, detail_output):

    allPathes = []
    detailOutputs= []

    # intertor to one selcted: start-goal
    for i in range(0, len(starting_locations)):

        start = starting_locations[i]
        goal = goal_locations[i]

        switcher = {
            1: A_star_search,
            2: hill_climbing,
            3: simulated_annealing,
            4: beam_search,
            5: genetic_algorithm}

        path, detailOutputAns = switcher[search_method](start, goal)

        if path is None:
            # there isnt path
            return print("No path found")
        else:
            # there is path
            allPathes.append(path)
            detailOutputs.append(detailOutputAns)

    if detail_output:
        printdetailOutputs(detailOutputs, search_method)

    return print_answer(allPathes)

def printdetailOutputs(details, search_method):
    if search_method == 1:
        print("\nthe heuristic value after the first transformation is:", details)
        sum = 0
        for d in details:
            sum += d
        print("Total for all pathes:", sum)

    if search_method == 2:
        print("")

    if search_method == 3:
        print("")

    if search_method == 4:
        print("")

    if search_method == 5:
        print("")


# A* search
def A_star_search(start, goal):

    open, closed = [], []

    # Create a start node and an goal node
    start_node = Node(start, None)
    goal_node = Node(goal, None)
    # find heuristics values to goal
    heuristic = clculateHeuristics(goal_node.country)

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
            return recreate_path(current_node, start_node)

        neighbors = current_node.getNeighbors()
        for neighbor in neighbors:
            neighbor = Node(neighbor, current_node)

            # if we check the neighbor, pass
            if neighbor in closed:
                continue
            # calculate full path cost
            neighbor.g = current_node.g + 1
            neighbor.h = heuristic.get(neighbor.country)
            try:
                neighbor.f = neighbor.g + neighbor.h
            except:
                # if there is not heuristic value
                neighbor.f = neighbor.g + 100000

            # Check if neighbor is in open list and if it has a lower value
            open = add_to_open(open, neighbor)

    return None, None


# follow nodes and recreate path
def recreate_path(current_node, start_node):

    path = []
    # loop until reach to start-node
    while current_node != start_node:
        path.append(current_node.name)
        details_h = current_node.h
        current_node = current_node.parent
    try:
        h = details_h
    except:
        h= None
    path.append(start_node.name)
    # reverse path
    return path[::-1], h

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
def NeighborsByContries():
    return {      'OH': ['WV', 'IN', 'MI', 'PA', 'KY'],
                  'OK': ['NM', 'CO', 'KS', 'TX', 'AR', 'MO'],
                  'OR': ['WA', 'ID', 'CA', 'NV'],
                  'IA': ['SD', 'NE', 'MO', 'IL', 'WI', 'MN'],
                  'ID': ['WA', 'OR', 'NV', 'UT', 'MT', 'WY'],
                  'IL': ['KY', 'IN', 'MO', 'IA', 'WI'],
                  'IN': ['OH', 'MI', 'KY', 'IL'],
                  'AL': ['FL', 'GA', 'TN', 'MS'],
                  'AZ': ['CA', 'NM', 'NV', 'UT', 'CO'],
                  'AR': ['OK', 'TX', 'LA', 'MS', 'TN', 'MO'],
                  'GA': ['NC', 'SC', 'FL', 'AL', 'TN'],
                  'DE': ['PA', 'MD', 'NJ'],
                  'SD': ['WY', 'MT', 'ND', 'MS', 'LA', 'NE'],
                  'ND': ['MT', 'SD', 'MS'],
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
                  'VI': [], 'PR': [], 'MP': [], 'GU': [], 'AS': [], 'AK': [], 'HI': [],
                  'DC': ['MD', 'VA']   }

# bfs-search to find heuristics value
def clculateHeuristics (root, graph_search=NeighborsByContries()):
    # bfs tree when root is goal-node
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

    starting_locations = ["Washington County, UT", "Chicot County, AR", "Fairfield County, CT"]
    goal_locations = ["San Diego County, CA", "Bienville Parish, LA", "Rensselaer County, NY"]

    search_method = 2
    detail_output = True

    find_path(starting_locations, goal_locations, search_method, detail_output)





