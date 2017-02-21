# Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented to complete the warehouse domain.

'''
Construct and return Tenner Grid CSP models.
'''

from cspbase import *
import itertools


def tenner_csp_model_1(initial_tenner_board):
    '''Return a CSP object representing a Tenner Grid CSP problem along
       with an array of variables for the problem. That is return

       tenner_csp, variable_array

       where tenner_csp is a csp representing tenner grid using model_1
       and variable_array is a list of lists

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

       such that variable_array[i][j] is the Variable (object) that
       you built to represent the value to be placed in cell i,j of
       the Tenner Grid (only including the first n rows, indexed from
       (0,0) to (n,9)) where n can be 3 to 8.


       The input board is specified as a pair (n_grid, last_row).
       The first element in the pair is a list of n length-10 lists.
       Each of the n lists represents a row of the grid.
       If a -1 is in the list it represents an empty cell.
       Otherwise if a number between 0--9 is in the list then this represents a
       pre-set board position. E.g., the board

       ---------------------
       |6| |1|5|7| | | |3| |
       | |9|7| | |2|1| | | |
       | | | | | |0| | | |1|
       | |9| |0|7| |3|5|4| |
       |6| | |5| |0| | | | |
       ---------------------
       would be represented by the list of lists

       [[6, -1, 1, 5, 7, -1, -1, -1, 3, -1],
        [-1, 9, 7, -1, -1, 2, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, 0, -1, -1, -1, 1],
        [-1, 9, -1, 0, 7, -1, 3, 5, 4, -1],
        [6, -1, -1, 5, -1, 0, -1, -1, -1,-1]]


       This routine returns model_1 which consists of a variable for
       each cell of the board, with domain equal to {0-9} if the board
       has a 0 at that position, and domain equal {i} if the board has
       a fixed number i at that cell.

       model_1 contains BINARY CONSTRAINTS OF NOT-EQUAL between
       all relevant variables (e.g., all pairs of variables in the
       same row, etc.).
       model_1 also constains n-nary constraints of sum constraints for each
       column.
    '''
    # IMPLEMENT
    domain = list(range(0, 10))
    grid = initial_tenner_board[0]
    last_row = initial_tenner_board[1]
    variables = create_variables(grid)

    constraints = create_model_1_constraints(grid, last_row)

    csp = CSP("TennerCSP", vars=variables)

    for constraint in constraints:
        csp.add_constraint(constraint)

    return csp, variables

##############################


def tenner_csp_model_2(initial_tenner_board):
    '''Return a CSP object representing a Tenner Grid CSP problem along
       with an array of variables for the problem. That is return

       tenner_csp, variable_array

       where tenner_csp is a csp representing tenner using model_1
       and variable_array is a list of lists

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

       such that variable_array[i][j] is the Variable (object) that
       you built to represent the value to be placed in cell i,j of
       the Tenner Grid (only including the first n rows, indexed from
       (0,0) to (n,9)) where n can be 3 to 8.

       The input board takes the same input format (a list of n length-10 lists
       specifying the board as tenner_csp_model_1.

       The variables of model_2 are the same as for model_1: a variable
       for each cell of the board, with domain equal to {0-9} if the
       board has a -1 at that position, and domain equal {i} if the board
       has a fixed number i at that cell.

       However, model_2 has different constraints. In particular, instead
       of binary non-equals constaints model_2 has a combination of n-nary
       all-different constraints: all-different constraints for the variables in
       each row, contiguous cells (including diagonally contiguous cells), and
       sum constraints for each column. Each of these constraints is over more
       than two variables (some of these variables will have
       a single value in their domain). model_2 should create these
       all-different constraints between the relevant variables.
    '''
    # IMPLEMENT
    return None, []


def create_variables(grid):
    variables = []
    x = 0
    for row in grid:
        y = 0
        row = []
        for value in row:
            # variables are named by their xy coordinates
            if value != -1:
                var = Variable("{}{}".format(x, y), domain=[value])
                var.assign(value)
            else:
                var = Variable("{}{}".format(x, y), domain=domain)

            row.append(var)
            y = y + 1
        variables.append(row)
        x = x + 1

    return variables


def create_model_1_constraints(variable_matrix, sum_row):
    constraints = []
    for x, row in enumerate(variable_matrix):

        for y, variable in enumerate(row):
            # create row constraints
            rest = row[:y] + row[(y + 1):]
            constraints.extend(create_binary_constraint(variable, rest))

            # create contiguous cell constraints
            surrounding_variables = get_surrounding_variables(variable_matrix, x, y)
            constraints.extend(create_binary_constraint(variable, surrounding_variables))

        # create column sum constraints
        expected_sum = sum_row[x]
        constraints.extend(create_column_sum_constraint(variable_matrix, x, expected_sum))

    return constraints


def create_column_sum_constraint(variable_matrix, x, expected_sum):
    constraints = []
    column_variables = [row[x] for row in variable_matrix]

    return constraints


def get_surrounding_variables(variable_matrix, x, y):
    surrounding_variables = []
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            # skip out of range indexes
            if i < 0 or j < 0:
                continue
            if i >= len(variable_matrix):
                continue
            if j >= len(variable_matrix[i]):
                continue

            surrounding_variables.append(variable_matrix[i][j])

    return surrounding_variables


def create_binary_constraint(variable, rest):
    '''
    creates constraints between variable and all the variables in rest
    '''
    constraints = []
    for var in rest:
        constraint = Constraint("Cons_{}:{}".format(variable.name, var.name), [variable, var])

        satisfying_tuples = list(itertools.product(variable.domain(), var.domain()))
        satisfying_tuples = [
            tup 
            for tup in satisfying_tuples
            if tup[0] != tup[1]
        ]

        constraint.add_satisfying_tuples(satisfying_tuples)

        constraints.append(constraint)

    return constraints
