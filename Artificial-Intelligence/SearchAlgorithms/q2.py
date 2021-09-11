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
        self.neighbors = None

    # compare nodes
    def __eq__(self, other):
        return self.name == other.name

    # sort nodes by f
    def __lt__(self, other):
        return self.f > other.f

    # get neighbors.
    # if b - get distance from node to b
    def getNeighbors(self, other=None):
        if not self.neighbors:
            df = pd.read_csv(path)
            listOfNeighbors = df.loc[df['countyname'] == self.name]['neighborname']
            neighbors = []
            for neighbor in listOfNeighbors:
                if neighbor != self.name:
                    neighbors.append(neighbor)
            self.neighbors = neighbors
        if other:
            if other.name in self.neighbors: return True
            else: return False

        return copy.deepcopy(self.neighbors)

    def getNeighborsNotVisited(self, visited):
        neighbors= self.getNeighbors()
        if not visited :
            return neighbors
        return [neig for neig in neighbors if (neig not in visited)]

    def update_h (self, heuristic):
        try:
            self.h = heuristic[self.country]
        except:                 # if there is not heuristic value
            self.h=100000


def bfs(start, goal, heuristic):
    ''' bfs to calculate len path from start to goal.
    helper function to genetic_algorithm'''
    explored = []
    queue = [[start]]
    if start == goal:
        return 0
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node.name not in explored:
            neighbours = node.getNeighbors()
            for neighbour in neighbours:
                new_path = list(path)
                neighbour_node=Node(neighbour, node)
                neighbour_node.update_h(heuristic)
                new_path.append(neighbour_node)
                queue.append(new_path)
                if neighbour_node == goal:
                    return len(new_path)
            explored.append(node.name)
    return None



def printFinalAnswer(paths):
    '''organized all paths we founded'''
    # all paths should be in same length
    lmax =max(len(path) for path in paths)
    for path in paths:
        while len(path) < lmax:
            # add last location until length = lmax
            path.append(path[-1])
    print ("\n", numpy.transpose(paths))


def find_best_neigbhors(list_of_nodes, heuristic, visited=[], size=0):
    ''' helper function to beam_search.
    for each node in list_of_nodes, it take node's neighbors,
    update h and adding to ls.
    finally ls sorted by h (and i make innner sorted by num of neighbors not visited)

    if size = 0 : the output it ls
     else, if size=k: the output will be the best k in list
     (or all the list if len(ls)<k)
      '''
    ls=[]
    for node in list_of_nodes:
        neighbors_not_visited = node.getNeighborsNotVisited(visited)
        if len(neighbors_not_visited) > 0:
            for neighbor in neighbors_not_visited:
                neighbor_node = Node(neighbor, node)
                if neighbor_node not in ls:
                    neighbor_node.update_h(heuristic)
                    ls.append(neighbor_node)
    if len(ls) > 0:
        list_sorted = sorted(ls, key=lambda n: (len(n.getNeighborsNotVisited(visited))))
        list_sorted2 = (sorted(list_sorted, key=lambda n: (-n.h)))
        if size == 0:
            return list_sorted2

        return list_sorted2[len(list_sorted2)-(min(size, len(list_sorted2))):]

    return ls



def hill_climbing(start, goal, detail_output):
    'we learned in call that hill climing is exaclly like beam search with k=1'
    return beam_search(start, goal, detail_output=False, k=1)

def simulated_annealing(start_node, goal_node, detail_output):
    ''' i added a list of visited although it is not necessarily required by the algorithm,
    but since the work task required a maximum of 100 iterations,
    I thought it would be smart that node not selected several times'''

    if detail_output:
        print("\n########### try to find path from '%s' to '%s' ########### "
              % (start_node.name, goal_node.name))
    t=1
    heuristic = clculateHeuristics(goal_node.country)
    visited=[]
    start_node.update_h(heuristic)
    current_node = start_node
    t_max= 100+1

    while (t):
        if current_node == goal_node:
            return recreate_path(current_node, start_node)
        visited.append(current_node.name)
        current_node.update_h(heuristic)

        T =1-(t/t_max)

        if T==0:
            break

        neighbors = current_node.getNeighborsNotVisited(visited)

        if not neighbors:
            break
        next_node = Node(neighbors.pop(random.randrange(len(neighbors))), current_node)
        next_node.update_h(heuristic)

        delta = current_node.h-next_node.h
        if delta > 0: # next node.h is better than current_node.h
            P=1
        else:
            P = math.exp((delta-1)/T)

        if detail_output:
            print ("step number %s. Consider action is '%s' with probability %s "
                   % (t, next_node.name, P))
        ran = numpy.random.random()

        if ran < P:
            current_node = next_node
        else:
            visited.append(current_node.name)
        t+=1
    return []



def beam_search(start_node, goal_node,detail_output, k=3):

    if detail_output:
        print("\n########### try to find path from '%s' to '%s' ########### "
              % (start_node.name, goal_node.name))

    sideways_move=0   # count sideways_move in case the algorithm rich to 'Katef'
    max_sideways_move=500  # max sideways move allowed (more then --> restart)
    number_of_restart = 0
    visited = []
    heuristic = clculateHeuristics(goal_node.country)

    current_nodes = [start_node]

    while number_of_restart <= 5 and current_nodes :

        if goal_node in current_nodes:
            for node in current_nodes:
                if node == goal_node:
                    return recreate_path(node, start_node)

        for node in current_nodes:
            visited.append(node.name)

        best_k_neighbhors = find_best_neigbhors(current_nodes, heuristic, visited, size=k)

        if not best_k_neighbhors:
            #make restart
            number_of_restart += 1
            sideways_move = 0
            current_nodes = [start_node]

        else:
            if detail_output:
                print("round %s. Actions considered: '%s' "
                      % (number_of_restart, [i.name for i in best_k_neighbhors]))
            current_nodes_new=[]
            for node in best_k_neighbhors:

                if node.h<node.parent.h:
                    current_nodes_new.append(node)

                elif node.h == node.parent.h:
                    # we founded 'Katef'.
                    sideways_move +=1
                    if sideways_move <= max_sideways_move:
                        current_nodes_new.append(node)

            if current_nodes_new:
                current_nodes = current_nodes_new
            else:
                number_of_restart +=1
                sideways_move = 0
                current_nodes = find_best_neigbhors([start_node], heuristic, visited, size=k)

    return []

def create_random_path(begin_node, size, heuristic):
    '''helper funct to create_population in genetic algorithm.
    create path from begin node with len(path)=size '''
    ls=[]
    visited=[]
    current_node = begin_node
    ls.append(current_node)
    visited.append(current_node.name)
    for location in range(size):
        neighbors = current_node.getNeighborsNotVisited(visited)
        next_node = Node(neighbors.pop(random.randrange(len(neighbors))), current_node)
        next_node.update_h(heuristic)
        ls.append(next_node)
        visited.append(next_node.name)
        current_node = next_node
    while len(ls)<size:
        random_location= ls[random.randrange(len(ls))].name
        next_node = Node( random_location, current_node)
        ls.append(next_node)
    return ls

def create_population(start_node,goal_node, DNA_size, heuristic):
    '''create 10 paths. each path made of two sub-path:
    one begin in start node, and second start at goal node (and then make revers).
    therefore the paths not necessarily represent possible paths '''
    ans=[]
    size1= math.ceil((DNA_size-2)/2)
    size2 = math.floor((DNA_size - 2)/2)
    for i in range(10):
        begin_path = create_random_path(start_node, size1, heuristic)
        end_path = create_random_path(goal_node, size2, heuristic)[::-1]
        ans.append(begin_path+end_path)
    return ans


def fitness(path):
    '''helfer func that calculate fitness to path.
    fitness=1 is the best score (it means it possible solution),
    the mode fitness is higher --> path is worser '''
    fitness = 1
    for i in range(1, len(path)):
        if not path[i].getNeighbors(path[i - 1]):
            fitness += 2
    size=math.ceil(len(path)/2)
    if not path[size].getNeighbors(path[size - 1]):
        # this is the point two sub-paths is connected
        # therefore we want "to punish" path that not connected in this point
        fitness+=2
    return fitness


def genetic_algorithm(start_node, goal_node, detail_output):

    if detail_output:
        print("\n########### try to find path from '%s' to '%s' ########### "
              % (start_node.name, goal_node.name))

    heuristic = clculateHeuristics(goal_node.country)
    start_node.update_h(heuristic)
    goal_node.update_h(heuristic)

    ans = bfs(start_node, goal_node, heuristic)
    if ans is None: # there is no way to rich fron start to goal
        return []
    if ans == 0: # goal=start
        if detail_output:
            print("\nGeneration 0")
            print("'%s'" % [start_node.name])
        return [start_node.name]
    DNA_size=ans

    generations = 7000
    population = create_population(start_node,goal_node, DNA_size, heuristic)

    for g in range(generations):

        if detail_output:
            print("\nGeneration %s" % (g))
            for j in range( len(population)):
                print("%s: '%s'" % (j+1, [i.name for i in population[j]]))

        population_wighted = []
        for individual in population:

            fitness_val = fitness(individual)
            if fitness_val==1: # we founded solution
                return [i.name for i in individual]
            population_wighted.append((individual, 1.0 / fitness_val))

        population = []

        for _ in range(5):
            # selection
            ind1 = weighted_choice(population_wighted)
            ind2 = weighted_choice(population_wighted)

            # crossover
            ind1, ind2 = crossover(ind1, ind2)

            # mutate and add back into the population.
            population.append(mutate(ind1))
            population.append(mutate(ind2))

    # find best result
    while population:
        res= population.pop()
        if fitness(res)==1: # feasible solution
            return [i.name for i in res]
    return []

def weighted_choice(population_wighted):
    ''' chose path from population_wighted according to wight
    (more wight --> more probability to chose'''
    weight_total = sum((individual[1] for individual in population_wighted))
    n = random.uniform(0, weight_total)
    for individual, weight in population_wighted:
        if n < weight:
            return individual
        n = n - weight
    return individual

def crossover(dna1, dna2):
    ''' switches sections between dna1, dna2'''
    pos = int(random.random() * len(dna1))
    return (dna1[:pos] + dna2[pos:], dna2[:pos] + dna1[pos:])

def mutate(dna):
    ''' make a mutation in dna with a certain probability'''
    mutation_chance = 100
    for c in range(1,len(dna)-1):
        if int(random.random() * mutation_chance) == 1:
            visited = [i.name for i in dna]
            neighbors = dna[c-1].getNeighborsNotVisited(visited)
            if neighbors:
                dna[c] = Node(neighbors.pop(random.randrange(len(neighbors))), dna[c-1])

    return dna



def find_path(starting_locations, goal_locations, search_method, detail_output):

    allPathes = []

    # intertor to one selcted: start-goal
    for i in range(0, len(starting_locations)):

        start = Node(starting_locations[i], None)
        goal = Node(goal_locations[i], None)

        switcher = {
            1: A_star_search,
            2: hill_climbing,
            3: simulated_annealing,
            4: beam_search,
            5: genetic_algorithm}

        path = switcher[search_method](start, goal, detail_output)
        if not path:   # there isnt path
            return print("No path found")
        allPathes.append(path)

    printFinalAnswer(allPathes)


def A_star_search(start_node, goal_node, detail_output):
    '''A* search '''
    if detail_output:
        print("\n########### try to find path from '%s' to '%s' ########### "
              % (start_node.name, goal_node.name))

    open, closed = [], []

    # find heuristics values to goal
    heuristic = clculateHeuristics(goal_node.country)
    start_node.update_h(heuristic)
    goal_node.update_h(heuristic)
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

            if detail_output:
                if current_node==start_node:
                    node=start_node
                else:
                    node= current_node.parent
                    while node.parent != start_node:
                        node = node.parent
                print("the heuristic value of '%s' is %s"
                      % (node.name, node.h))
            return recreate_path(current_node, start_node)

        neighbors = current_node.getNeighbors()
        for neighbor in neighbors:
            neighbor = Node(neighbor, current_node)

            # if we check the neighbor, pass
            if neighbor in closed:
                continue
            # calculate full path cost
            neighbor.g = current_node.g + 1
            neighbor.update_h(heuristic)
            neighbor.f = neighbor.g + neighbor.h

            # Check if neighbor is in open list and if it has a lower value
            open = add_to_open(open, neighbor)

    return []



def recreate_path(current_node, start_node, AsNodes = False):
    ''' the function follow nodes and recreate path'''
    path_as_node=[]
    path = []
    # loop until reach to start-node
    while current_node != start_node:
        path_as_node.append(current_node)
        path.append(current_node.name)
        current_node = current_node.parent

    path_as_node.append(start_node)
    path.append(start_node.name)
    # reverse path
    if AsNodes:
        return path_as_node[::-1]
    return path[::-1]

# Check if neighbor is in open list and if it has a lower value
def add_to_open(open, neighbor):
    ''' helper funct to a-star algorithm.
    check if need to add node to list according to
    shorted node.g  '''
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



def clculateHeuristics (goal_country, graph_search=NeighborsByContries()):
    ''' bfs-search to find heuristics value.
    the function return dictionary when countries codes are he keys
      and the values is the distance to goal-country from each key'''
    ans, visited, queue, queue2 = {}, set(), [goal_country], []
    visited.add(goal_country)
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



if __name__ == '__main__':

# The code you want to run before find_path() #

    #find_path(['Essex County, VT', 'Coos County, NH'], ['Pasquotank County, NC', 'Grayson County, VA'], 1, True)

    #find_path(['Essex County, VT', 'Coos County, NH'], ['Penobscot County, ME', 'Sagadahoc County, ME'], 3, True)

    #find_path(['Essex County, VT', 'Coos County, NH'], ['Wilson County, NC', 'Grayson County, VA'], 4, True)

    find_path(['Essex County, VT', 'Coos County, NH'], ['Penobscot County, ME', 'Sagadahoc County, ME'], 5, True)



