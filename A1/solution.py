# Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented to complete the Sokoban warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

# import os for time functions
import os
import math
from search import *  # for search engines
from sokoban import SokobanState, Direction, PROBLEMS, sokoban_goal_state  # for Sokoban specific classes and problems

# SOKOBAN HEURISTICS


def heur_displaced(state):
    '''trivial admissible sokoban heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    count = 0
    for box in state.boxes:
        if box not in state.storage:
            count += 1
    return count


def heur_manhattan_distance(state):
    '''admissible sokoban heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must always underestimate the cost to get from the current state to the goal.
    # The sum Manhattan distance of the boxes to their closest storage spaces is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid and that several boxes can fit in one storage bin.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.
    total_cost = 0
    for box in state.boxes:
        if state.restrictions:
            possible_storages = state.restrictions[state.boxes[box]]
        else:
            possible_storages = list(state.storage.keys())

        storage_distances = [
            abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            for storage in possible_storages
        ]
        total_cost += min(storage_distances)
    return total_cost


obstacles = None
walls = None


def heur_alternate(state):
    # IMPLEMENT
    '''a better sokoban heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    global obstacles
    global walls

    if not obstacles or not state.obstacles.issubset(obstacles):
        walls = {tup for y in range(-1, state.height) for tup in ((state.width, y), (-1, y))}
        walls.update({tup for x in range(-1, state.width) for tup in ((x, -1), (x, state.height))})
        obstacles = walls.union(state.obstacles)

    total_cost = 0
    for box in state.boxes:
        multiplier = 1
        if state.restrictions:
            possible_storages = state.restrictions[state.boxes[box]]
        else:
            possible_storages = list(state.storage.keys())

        if box in possible_storages:
            continue
        else:
            around_box = {
                (box[0] - 1, box[1]),
                (box[0] + 1, box[1]),
                (box[0], box[1] + 1),
                (box[0], box[1] - 1),
            }
            number_of_intersections = len(around_box.intersection(obstacles))
            if number_of_intersections >= 2:
                # if box is surrounded by 2 or more obstacles
                multiplier += number_of_intersections * 9999

            # if box is along a wall and no possible storages are on that same wall
            if box[0] in {-1, state.width}:
                storages_along_wall = {
                    storage for storage in possible_storages if storage[0] == box[0]
                }
                if not storages_along_wall:
                    multiplier += 9999
            if box[1] in {-1, state.height}:
                storages_along_wall = {
                    storage for storage in possible_storages if storage[1] == box[1]
                }
                if not storages_along_wall:
                    multiplier += 9999

        storage_distances = [
            math.sqrt((box[0] - storage[0]) ** 2 + (box[1] - storage[1]) ** 2)
            for storage in possible_storages
        ]
        total_cost += min(storage_distances) * multiplier

    return total_cost


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """

    # Many searches will explore nodes (or states) that are ordered by their f-value.
    # For UCS, the fvalue is the same as the gval of the state. For best-first search, the fvalue is the hval of the state.
    # You can use this function to create an alternate f-value for states; this must be a function of the state and the weight.
    # The function must return a numeric f-value.
    # The value will determine your state's position on the Frontier list during a 'custom' search.
    # You must initialize your search engine object as a 'custom' search engine if you supply a custom fval function.
    return sN.gval + (weight * sN.hval)


def anytime_gbfs(initial_state, heur_fn, timebound=10):
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    optimal_solution = False

    search_engine = SearchEngine(strategy="best_first")
    search_engine.init_search(initial_state, sokoban_goal_state)
    min_gval = float("inf")
    remaining_time = timebound

    while remaining_time > 0:
        if min_gval == float("inf"):
            costbound = None
        else:
            costbound = (min_gval, float("inf"), float("inf"))
        start_time = os.times()[0]
        solution = search_engine.search(costbound=costbound, timebound=remaining_time)
        end_time = os.times()[0]

        if not solution:
            return optimal_solution
        elif solution.gval < min_gval:
            min_gval = solution.gval
            optimal_solution = solution

        remaining_time = remaining_time - (end_time - start_time)

    return optimal_solution


def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound=10):
    # IMPLEMENT
    '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    min_gval = float("inf")
    min_hval = float("inf")
    optimal_solution = False

    wrapped_fval = (lambda sN: fval_function(sN, weight))
    search_engine = SearchEngine(strategy="custom")
    search_engine.init_search(initial_state, sokoban_goal_state, fval_function=wrapped_fval)
    remaining_time = timebound

    while remaining_time > 0:
        if min_gval == float("inf"):
            costbound = None
        else:
            costbound = (float("inf"), float("inf"), min_gval + min_hval)

        start_time = os.times()[0]
        solution = search_engine.search(costbound=costbound, timebound=remaining_time)
        end_time = os.times()[0]

        if not solution:
            return optimal_solution
        elif solution.gval < min_gval:
            min_gval = solution.gval
            min_hval = heur_fn(solution)
            optimal_solution = solution

        remaining_time = remaining_time - (end_time - start_time)

    return optimal_solution


if __name__ == "__main__":
    # TEST CODE
    solved = 0
    unsolved = []
    counter = 0
    percent = 0
    timebound = 2  # 2 second time limit for each problem
    print("*************************************")
    print("Running A-star")

    for i in range(0, 10):  # note that there are 40 problems in the set that has been provided.  We just run through 10 here for illustration.

        print("*************************************")
        print("PROBLEM {}".format(i))

        s0 = PROBLEMS[i]  # Problems will get harder as i gets bigger

        se = SearchEngine('astar', 'full')
        se.init_search(s0, goal_fn=sokoban_goal_state, heur_fn=heur_displaced)
        final = se.search(timebound)

        if final:
            final.print_path()
            solved += 1
        else:
            unsolved.append(i)
        counter += 1

    if counter > 0:
        percent = (solved / counter) * 100

    print("*************************************")
    print("{} of {} problems ({} %) solved in less than {} seconds.".format(solved, counter, percent, timebound))
    print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))
    print("*************************************")

    solved = 0
    unsolved = []
    counter = 0
    percent = 0
    timebound = 8  # 8 second time limit
    print("Running Anytime Weighted A-star")

    for i in range(0, 10):
        print("*************************************")
        print("PROBLEM {}".format(i))

        s0 = PROBLEMS[i]  # Problems get harder as i gets bigger
        weight = 10
        final = anytime_weighted_astar(s0, heur_fn=heur_displaced, weight=weight, timebound=timebound)

        if final:
            final.print_path()
            solved += 1
        else:
            unsolved.append(i)
        counter += 1

    if counter > 0:
        percent = (solved / counter) * 100

    print("*************************************")
    print("{} of {} problems ({} %) solved in less than {} seconds.".format(solved, counter, percent, timebound))
    print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))
    print("*************************************")
