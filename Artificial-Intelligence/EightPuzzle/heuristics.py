from Node import goalBoard_node
import copy
import eightPuzzle


def heuristicOne(problem):
    #1 unit for each tile that isnt correctly located
    totalHeuristic=0
    for i in range(len(problem)):
        for j in range(len(problem[i])):
            if (problem[i][j] != 0) and (problem[i][j] != goalBoard_node.problem[i][j]):
                totalHeuristic += 1

    return totalHeuristic


def heuristicTwo(problem):
    #for each tile out of place, calc abs distance to goal location
    h=0
    for i in range(len(problem)):
        for j in range(len(problem[0])):
            if (problem[i][j] != 0) and (problem[i][j] != goalBoard_node.problem[i][j]):
                locationInGoalrow, locationInGoalcol = findTile(problem[i][j])
                h += abs(i-locationInGoalrow) + abs(j-locationInGoalcol)
    return h


def heuristicThree(problem): #1 unit for each tile out of place in row and 1 for each tile out of place in col
    totalHeuristic = 0

    #first the rows
    for i in range(len(problem)):
        for j in range(len(problem[i])):
            if (problem[i][j] != 0) and (problem[i][j] not in goalBoard_node.problem[i]):
                totalHeuristic += 1
    #now the cols
    for j in range(len(problem[0])):
        for i in range(len(problem)):
            if (problem[i][j] != 0) and (problem[i][j] not in getProblemColumn(goalBoard_node.problem, j)):
                totalHeuristic += 1

    return totalHeuristic



def heuristicFour(problem):
    #Solve the board with the ability to swap between any tile with the “0” tile only.
    h = 0
    tempProblem = copy.deepcopy(problem)
    while tempProblem != goalBoard_node.problem:
        rowZero, colZero = eightPuzzle.findZeroTile(tempProblem)
        if rowZero == 2 and colZero == 2: #empty tile in goal place [2,2]
            rowCorrectTile, colCorrectTile = findRandomTileNotInPlace(tempProblem)
        else:
            correctTile = goalBoard_node.problem[rowZero][colZero]
            rowCorrectTile, colCorrectTile = findTile(correctTile, problem=tempProblem)
        eightPuzzle.swap(tempProblem, rowZero, colZero, rowCorrectTile, colCorrectTile)
        h += 1
    return h



####### helper functions #######

def findTile(tile, problem=goalBoard_node.problem):
    #finds the location of a specific tile in a problem
    for i in range(len(problem)):
        for j in range(len(problem[0])):
            if problem[i][j] == tile:
                return i, j


def findRandomTileNotInPlace(problem):
    #helper function for heuristics 4 - finds tiles that arent in their place
    for i in range(len(problem)):
        for j in range(len(problem[i])):
            if problem[i][j] != goalBoard_node.problem[i][j]:
                return i, j
    return None

