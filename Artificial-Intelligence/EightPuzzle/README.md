# 8-Puzzle Problem Solver
Implementation of A* and Branch & Bound algorithms to solve 8-puzzle.
The implementation of the B&B algorithm can also get an search type.

## Project Structure
1. [Node.py](Artificial-Intelligence/EightPuzzle/Node.py.md) - Class for representing a node in the search tree.
2. eightPuzzle.py - Main. Script with an random example for solve. Additionally, a comparison between the algorithms and heuristics and couple of plots for the comparison. 
3. heuristics.py - Script which contains all the heuristics as functions Each function in heuristics.py script most get the current state and the goal state as numpy arrays, and return the heuristic value. Currently, the script contains 4 heuristics.
