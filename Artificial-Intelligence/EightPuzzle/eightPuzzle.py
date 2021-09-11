import copy,random, math
import matplotlib.pyplot as plt

import heuristics
from Node import Node
from Node import goalBoard_node

global li1, li2
li1 =[]
li2=[]

def findPath(node):
    #replays path by looking at parent nodes and returns a list that represents the path
    full_path = []
    while node is not None:
        full_path.insert(0, node)
        node = node.parent

    return full_path


def getProblemColumn(problem, col):
    #returns a full column from the given problem
    problemColumn = []
    for i in range(len(problem)):
        for j in range(len(problem[i])):
            if j == col:
                problemColumn.append(problem[i][j])
    return problemColumn

def swap(problem, rowIndexOfZeroTile, colIndexOfZeroTile, nextMoveRow, nextMoveCol):
    #swaps between two tiles on board
    problem[rowIndexOfZeroTile][colIndexOfZeroTile] = problem[nextMoveRow][nextMoveCol] #put number over empty tile
    problem[nextMoveRow][nextMoveCol] = 0 #put empty tile on number tile

    return problem

def findZeroTile(problem): #finds where the zero tile is
    for i in range(0,len(problem)):
        for j in range(0,len(problem[i])):
            if problem[i][j] == 0:
                return i, j


def getBoardNodeNeighbors(board_node):
    #finds all neighbors of specific node (problem)
    i, j = findZeroTile(board_node.problem) #indices of zero tile

    neighborsNodesList = []

    if i+1 < len(board_node.problem):
        next_problem = swap(problem=copy.deepcopy(board_node.problem), rowIndexOfZeroTile=i,
                            colIndexOfZeroTile=j, nextMoveRow=i+1, nextMoveCol=j)
        neighborsNodesList.append(Node(next_problem))
    if i-1 >= 0:
        next_problem = swap(problem=copy.deepcopy(board_node.problem), rowIndexOfZeroTile=i,
                            colIndexOfZeroTile=j, nextMoveRow=i-1, nextMoveCol=j)
        neighborsNodesList.append(Node(next_problem))
    if j+1 < len(board_node.problem):
        next_problem = swap(problem=copy.deepcopy(board_node.problem), rowIndexOfZeroTile=i,
                            colIndexOfZeroTile=j, nextMoveRow=i, nextMoveCol=j+1)
        neighborsNodesList.append(Node(next_problem))
    if j-1 >= 0:
        next_problem = swap(problem=copy.deepcopy(board_node.problem), rowIndexOfZeroTile=i,
                            colIndexOfZeroTile=j, nextMoveRow=i, nextMoveCol=j-1)
        neighborsNodesList.append(Node(next_problem))

    return neighborsNodesList


def AStar(problem, heuristic):
    #ASTAR algorithm

    initialBoard_node = Node(problem)
    initialBoard_node.h = heuristic(initialBoard_node.problem)
    initialBoard_node.f = initialBoard_node.h + initialBoard_node.g

    solution_path = None #initially there is no solution
    frontier = [initialBoard_node] #initial frontier
    explored = [] #all nodes that have been explored

    while len(frontier) > 0:

        frontier = sorted(frontier, key=lambda node: (-(node.g + node.h))) #sort frontier by lowest g+h and inner sort by id
        currentBoard_node = frontier.pop() #get lowest g+h node and remove from frontier

        if currentBoard_node == goalBoard_node: #arrived at goal
            solution_path = findPath(currentBoard_node) #find the opt path and return it
            break

        explored.append(currentBoard_node) #visited this node
        availableNeighbors = getBoardNodeNeighbors(currentBoard_node)

        for neighbor in availableNeighbors:
            for exp in explored:
                li2.append(currentBoard_node.g + currentBoard_node.h)

                if neighbor != exp and neighbor not in frontier:
                    frontier.append(neighbor)
                    neighbor.h = heuristic(neighbor.problem)
                    neighbor.updateNodeInfo(currentBoard_node)

            if neighbor in frontier and neighbor.g > currentBoard_node.g + 1: #neighbor is in frontier but from a longer g
                neighbor.h = heuristic(neighbor.problem)
                neighbor.updateNodeInfo(currentBoard_node)

    return solution_path


def calculateNodeInfoForList(frontier, parent, heuristic):
    #calculates heuristic and updates parents of list
    for neighbor in frontier:
        neighbor.h = heuristic(neighbor.problem)
        neighbor.updateNodeInfo(parent)


def randomizeProblem(seed = 0 ,rows=3):
    #randomizes problem and returns a solvable problem

    newProblemAllowed = False
    randNumber = random.Random(seed)
    while not newProblemAllowed:
        newProblem=[]
        arsenal = [0, 1, 2, 3, 4, 5, 6, 7, 8]

        while len(arsenal) > 0:
            randNum = randNumber.randint(0,len(arsenal)-1)
            newProblem.append(arsenal[randNum])
            del arsenal[randNum]

        newProblemAllowed = checkIfSolvableBoard(newProblem)

    newProblem = [newProblem[x:x+rows] for x in range(0, len(newProblem), rows)]
    return newProblem


def checkIfSolvableBoard(newProblem):
    #number of inversions must be even in order to solve the board.
    # inversions=num of larger numbers before me
    sumOfInversions = 0
    for i in range(len(newProblem)):
        if newProblem[i] == 0:
            continue
        for j in range(i):
            if newProblem[j]>newProblem[i]:
                sumOfInversions += 1
    return (sumOfInversions % 2 == 0)


def printAlgorithm(path):
    #print path
    for i in range(len(path)):
        print("iteration", i)
        for j in range(len(path[i].problem)):
            print(path[i].problem[j])


def getFrontier(currentBoard_node, iteration):
    #gets  neigbors of node that arent its' parents and also dont appear in the branch (his path)

    if currentBoard_node.neighbors is None:
        currentBoard_node.neighbors = getBoardNodeNeighbors(currentBoard_node) #all neighbors
        current_path_to_node = currentBoard_node.getPath() #current branch
        remove=[] #
        for i in range(len(currentBoard_node.neighbors)):
            for j in range(len(current_path_to_node)):
                li1.append(currentBoard_node.g + currentBoard_node.h)

                iteration += 1

                if currentBoard_node.neighbors[i] == current_path_to_node[j]:
                    remove.append(currentBoard_node.neighbors[i])#want to remove if weve been there already

        currentBoard_node.neighbors = [x for x in currentBoard_node.neighbors if x not in remove]

    return currentBoard_node.neighbors, iteration


def BranchAndBound(problem, heuristic):
    global runTimeIterationBnB
    iteration = 0

    initialBoard_node = Node(problem)
    initialBoard_node.h = heuristic(initialBoard_node.problem)
    initialBoard_node.f = initialBoard_node.h + initialBoard_node.g

    UB = math.inf
    LB = initialBoard_node.h
    currentBoard_node = initialBoard_node


    #will be none if we were at root and tried to backtrack from root
    while currentBoard_node is not None and UB != LB:

        if currentBoard_node.f >= UB: # we already have a better solution - pruning
            if currentBoard_node.parent is not None:
                currentBoard_node.parent.neighbors.remove(currentBoard_node)
            currentBoard_node = currentBoard_node.parent
            continue

        if currentBoard_node == goalBoard_node:#arrived at the goal state (if we reached this then we def improved UB)
            if currentBoard_node.g < UB: #not really necessary but in case
                bestPath = currentBoard_node.getPath()
                UB = currentBoard_node.g
                currentBoard_node.parent.neighbors.remove(currentBoard_node) #visited
            currentBoard_node = currentBoard_node.parent
            continue

        frontier, iteration = getFrontier(currentBoard_node, iteration)#get neighbors of current board that arent his parent or in the branch

        if len(frontier) == 0: #no more neighbors to visit - backtrack
            try:
                currentBoard_node.parent.neighbors.remove(currentBoard_node) #remove current from parent's neighbors (visited)
            except: pass
            currentBoard_node = currentBoard_node.parent #backtrack

        else: #neighbors to visit
            calculateNodeInfoForList(frontier, currentBoard_node, heuristic) #update heuristic and parent of frontier
            frontier = sorted(frontier, key=lambda node: (-(node.h)))  # sort frontier by lowest h
            currentBoard_node = frontier.pop() #get lowest h node and remove from frontier


    return bestPath

def printGraph():

    plt.plot(li1, label='BnB')
    plt.plot(li2, label='A-star')

    plt.xlabel('iterations')
    plt.ylabel('score')
    plt.title('Runtime')
    plt.legend()
    plt.show()

def findSolution(problem, heuristic):
    print('Running A*..')
    path = AStar(problem=copy.deepcopy(problem), heuristic=heuristic)
    printAlgorithm(path)
    print('\n\n')
    print('Running BnB..')
    path = BranchAndBound(problem=copy.deepcopy(problem),heuristic=heuristic)
    printAlgorithm(path)

if __name__ == "__main__":

    problem = randomizeProblem(seed=1)
    findSolution(problem=problem, heuristic=heuristics.heuristicTwo)
    printGraph()
