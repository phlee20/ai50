"""
Tic Tac Toe Player
"""

from copy import deepcopy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[X, O, X],
            [O, O, O],
            [X, X, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    sum_X = sum([row.count(X) for row in board])
    sum_O = sum([row.count(O) for row in board])
    if sum_X == sum_O:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = set()
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == EMPTY:
                moves.add((i, j))
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception

    temp = deepcopy(board)
    temp[action[0]][action[1]] = player(board)
    return temp


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """



def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Check if board is full
    full = EMPTY in (square for row in board for square in row)

    # Get last player played
    if player(board) == X:
        last = O
    else:
        last = X

    # Check rows and columns
    for i in range(len(board)):
        if all(board[i][j] == last for j in range(len(board))):
            return True
        elif all(board[j][i] == last for j in range(len(board))):
            return True
    
    # Check diagonal
    if all(board[i][i] == last for i in range(len(board))):
        return True
    elif board[0][2] == board[1][1] == board[2][0] == last:
        return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    raise NotImplementedError
