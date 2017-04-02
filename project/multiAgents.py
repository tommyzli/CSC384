# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

import copy
import datetime
from util import manhattanDistance
from game import Directions
import random, util

from game import Agent


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        max_score = float("-inf")
        selected_action = None
        for action in gameState.getLegalActions(0):
            value = self.minimax(gameState.generateSuccessor(0, action), 1)
            if value > max_score:
                max_score = value
                selected_action = action
        return selected_action

    def minimax(self, state, depth):
        agentIndex = depth % state.getNumAgents()
        actions = state.getLegalActions(agentIndex)
        if not actions or depth == self.depth * state.getNumAgents():
            # terminal state
            return self.evaluationFunction(state)

        scores = [
            self.minimax(state.generateSuccessor(agentIndex, action), depth + 1)
            for action in actions
        ]
        if agentIndex == 0:
            return max(scores)
        else:
            return min(scores)


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """
    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        selected_action = None
        max_score = float("-inf")

        alpha = float("-inf")
        # one beta value for each ghost
        betas = [float("inf") for _ in range(1, gameState.getNumAgents())]

        for action in gameState.getLegalActions(0):
            value = self.prunedMinimax(
                gameState.generateSuccessor(0, action),
                1,
                alpha,
                betas,
            )
            if value > max_score:
                selected_action = action
                max_score = value
            alpha = max(alpha, max_score)
        return selected_action

    def prunedMinimax(self, state, depth, alpha, betas):
        agentIndex = depth % state.getNumAgents()

        actions = state.getLegalActions(agentIndex)
        if not actions or depth == self.depth * state.getNumAgents():
            # terminal state
            return self.evaluationFunction(state)

        if agentIndex == 0:
            return self.max(state, depth, agentIndex, alpha, betas, actions)
        else:
            return self.min(state, depth, agentIndex, alpha, betas, actions)

    def max(self, gameState, depth, agentIndex, alpha, betas, actions):
        betas = copy.deepcopy(betas)

        value = float("-inf")
        for action in actions:
            value = max(
                value,
                self.prunedMinimax(
                    gameState.generateSuccessor(agentIndex, action),
                    depth + 1,
                    alpha,
                    betas,
                ),
            )
            if value > min(betas):
                return value
            alpha = max(alpha, value)
        return value

    def min(self, gameState, depth, agentIndex, alpha, betas, actions):
        betas = copy.deepcopy(betas)

        value = float("inf")
        for action in actions:
            value = min(
                value,
                self.prunedMinimax(
                    gameState.generateSuccessor(agentIndex, action),
                    depth + 1,
                    alpha,
                    betas,
                ),
            )
            if value < alpha:
                return value

            # offset agentIndex
            betas[agentIndex - 1] = min(betas[agentIndex - 1], value)
        return value


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
    """
    return currentGameState.getScore()


class MonteCarloAgent(MultiAgentSearchAgent):
    """
        Your monte-carlo agent (question 5)
        ***UCT = MCTS + UBC1***
        TODO:
        1) Complete getAction to return the best action based on UCT.
        2) Complete runSimulation to simulate moves using UCT.
        3) Complete final, which updates the value of each of the states visited during a play of the game.

        * If you want to add more functions to further modularize your implementation, feel free to.
        * Make sure that your dictionaries are implemented in the following way:
            -> Keys are game states.
            -> Value are integers. When performing division (i.e. wins/plays) don't forget to convert to float.
      """

    def __init__(self, evalFn='mctsEvalFunction', depth='-1', timeout='40', numTraining=100, C='2', Q=None):
        # This is where you set C, the depth, and the evaluation function for the section "Enhancements for MCTS agent".
        if Q:
            if Q == 'minimaxClassic':
                pass
            elif Q == 'testClassic':
                pass
            elif Q == 'smallClassic':
                pass
            else:  # Q == 'contestClassic'
                assert(Q == 'contestClassic')
                pass
        # Otherwise, your agent will default to these values.
        else:
            self.C = int(C)
            # If using depth-limited UCT, need to set a heuristic evaluation function.
            if int(depth) > 0:
                evalFn = 'scoreEvaluationFunction'
        self.states = []
        self.plays = dict()
        self.wins = dict()
        self.calculation_time = datetime.timedelta(milliseconds=int(timeout))

        self.numTraining = numTraining

        "*** YOUR CODE HERE ***"

        MultiAgentSearchAgent.__init__(self, evalFn, depth)

    def update(self, state):
        """
        You do not need to modify this function. This function is called every time an agent makes a move.
        """
        self.states.append(state)

    def getAction(self, gameState):
        """
        Returns the best action using UCT. Calls runSimulation to update nodes
        in its wins and plays dictionary, and returns best successor of gameState.
        """
        "*** YOUR CODE HERE ***"
        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            games += 1

        util.raiseNotDefined()

    def run_simulation(self, state):
        """
        Simulates moves based on MCTS.
        1) (Selection) While not at a leaf node, traverse tree using UCB1.
        2) (Expansion) When reach a leaf node, expand.
        4) (Simulation) Select random moves until terminal state is reached.
        3) (Backpropapgation) Update all nodes visited in search tree with appropriate values.
        * Remember to limit the depth of the search only in the expansion phase!
        Updates values of appropriate states in search with with evaluation function.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

    def final(self, state):
        """
        Called by Pacman game at the terminal state.
        Updates search tree values of states that were visited during an actual game of pacman.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


def mctsEvalFunction(state):
    """
    Evaluates state reached at the end of the expansion phase.
    """
    return 1 if state.isWin() else 0


def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
