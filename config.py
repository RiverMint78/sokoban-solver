import numpy as np
from re import compile
from typing import Callable

# base
STATE_TYPING = tuple[tuple[int, int], tuple[tuple[int, int], ...]]
DISTANCE_TYPING = Callable[[tuple[int, int], tuple[int, int]], int | float]

# actions
ACTIONS_LEN = 4
ACTIONS_DICT = {'u':0, 'd':1, 'l':2, 'r':3,
                'U':4, 'D':5, 'L':6, 'R':7,
                0:'u', 1:'d', 2:'l', 3:'r',
                4:'U', 5:'D', 6:'L', 7:'R'}
ACTIONS = np.array(
    ((-1, 0), # u U
    ( 1, 0),  # d D
    ( 0,-1),  # l L
    ( 0, 1),) # r R
    )
actions_idxes = [i for i in range(ACTIONS_LEN)]

# layout
LAYOUT_DICT = {
                ' ': 0, # space
                '-': 0, # space
                '_': 0, # space
                '@': 1, # player
                '&': 1,
                '.': 2, # goal
                '$': 3, # box
                'B': 3,
                '#': 4, # wall
                '+': 5, # player on goal
                '%': 5,
                '*': 6, # box on goal
                'X': 6,
                }
LAYOUT_PATTERN = compile(f"[^{''.join(LAYOUT_DICT.keys())}]*")

# 3x3 lose check
TRANS_PATTERNS = ([0,1,2,3,4,5,6,7,8],
                  [2,5,8,1,4,7,0,3,6],
                  [0,1,2,3,4,5,6,7,8][::-1],
                  [2,5,8,1,4,7,0,3,6][::-1],
                  [2,1,0,5,4,3,8,7,6],
                  [0,3,6,1,4,7,2,5,8],
                  [2,1,0,5,4,3,8,7,6][::-1],
                  [0,3,6,1,4,7,2,5,8][::-1])

# heuristic
HEURISTIC_DICT = {
    "mk": 0,
    "trivial": 1,
    "exp": 2
}

# graphic
XSB_PRINT_LST = ['-', '@', '.', '$', '#', '+', '*']
COLORFUL_PRINT_LST = ['⬜', '🟥', '🟦', '🟩', '🟫', '🟪', '❎']

# game
VALID_KEY_SET = {
    b'w', b'W', b'a', b'A', b's', b'S', b'd', b'D',
    b'q', b'Q', b'e', b'E', b'z', b'Z'
}
KEY_IDX_DICT = {
    'w': 0, 's': 1, 'a': 2, 'd': 3
}