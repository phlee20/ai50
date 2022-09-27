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
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


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
    # Get last player played
    if player(board) == X:
        last = O
    else:
        last = X

    # Check rows and columns
    for i in range(len(board)):
        if all(board[i][j] == last for j in range(len(board))):
            return last
        elif all(board[j][i] == last for j in range(len(board))):
            return last
    
    # Check diagonals
    if all(board[i][i] == last for i in range(len(board))):
        return last
    elif board[0][2] == board[1][1] == board[2][0] == last:
        return last


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Check if board is full or there is a winner
    spots = EMPTY in (square for row in board for square in row)

    if not spots or winner(board) in [X, O]:
        return True
    
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if not terminal(board):
        moves = []
        if player(board) == X:
            for action in actions(board):
                moves.append((min_value(result(board, action)), action))
            moves.sort(reverse=True)
        else:
            for action in actions(board):
                moves.append((max_value(result(board, action)), action))
            moves.sort()
        
        return moves[0][1]


def max_value(board):
    v = -2
    if terminal(board):
        return utility(board)
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    v = 2
    if terminal(board):
        return utility(board)
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v