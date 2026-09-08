import sys
import numpy as np
from util import (
    layout_parser,
    get_pos_player,
    get_pos_boxes,
    print_layout_dynamic,
    print_layout_static,
    print_moves_pushes,
    action_complier,
    expanse,
    is_win,
    ACTIONS_LEN,
    VALID_KEY_SET,
    KEY_IDX_DICT,
)

from time import sleep
from msvcrt import getch


class SokobanGame:
    def __init__(self, path: str, verbose: bool, colorful: bool):
        self.path = path
        self.verbose = verbose
        self.colorful = colorful
        self.LAYOUT = layout_parser(path)
        row_len, col_len = self.LAYOUT.shape
        self.POS = [[(j, i) for i in range(col_len)] for j in range(row_len)]
        self.POS_GOALS = tuple(
            self.POS[x][y]
            for x, y in np.argwhere(
                (self.LAYOUT == 2) | (self.LAYOUT == 5) | (self.LAYOUT == 6)
            )
        )
        self.HAS_WALLS = self.LAYOUT == 4
        self.HAS_GOALS = (self.LAYOUT == 2) | (self.LAYOUT == 5) | (self.LAYOUT == 6)
        self.START_STATE = (
            get_pos_player(self.POS, self.LAYOUT),
            get_pos_boxes(self.POS, self.LAYOUT),
        )
        self.moves = self.pushes = 0
        print_layout_static(self.LAYOUT, self.colorful)
        print_moves_pushes(self.moves, self.pushes)

    def sequence_play(self):
        pos_player, pos_boxes = self.START_STATE
        last_action = -1
        while True:
            sys.stdout.write("\n")
            actions = input()
            if len(actions) == 0:
                sys.stdout.write("\x1b[2A")
                continue
            if actions[0].lower() == "q":
                print("\x1b[1A\033[K\033[31mQuit!\033[0m")
                break
            sys.stdout.write("\x1b[1A\033[K\x1b[1A")
            if actions[0].lower() == "e":
                pos_player, pos_boxes = self.START_STATE
                print_layout_dynamic(
                    self.HAS_WALLS, self.HAS_GOALS, pos_player, pos_boxes, self.colorful
                )
                self.moves = self.pushes = 0
                print_moves_pushes(self.moves, self.pushes)
                continue
            action_idxes = action_complier(actions)
            print_layout_dynamic(
                self.HAS_WALLS, self.HAS_GOALS, pos_player, pos_boxes, self.colorful
            )
            for idx in action_idxes:
                expansion = expanse(
                    self.POS, self.HAS_WALLS, (pos_player, pos_boxes), idx
                )
                if expansion is None:
                    continue
                (pos_player, pos_boxes), last_action = expansion
                print_layout_dynamic(
                    self.HAS_WALLS, self.HAS_GOALS, pos_player, pos_boxes, self.colorful
                )
                self.moves += 1
                self.pushes += last_action >= ACTIONS_LEN
                print_moves_pushes(self.moves, self.pushes)
                sleep(min(0.03, 3 / len(action_idxes)))
            if is_win(self.HAS_GOALS, pos_boxes, last_action):
                print("\033[35m\nYOU WON!\033[0m")
                break

    def step_play(self):
        states = [(self.START_STATE, -1)]
        (pos_player, pos_boxes), last_action = states[-1]
        while True:
            sys.stdout.write("\n")
            sys.stdout.write("\x1b[1A")
            if (key := getch()) not in VALID_KEY_SET:
                continue
            key = key.decode().lower()
            if key == "q":
                print_moves_pushes(self.moves, self.pushes)
                print("\033[31m\nQuit!\033[0m")
                break
            if key == "e":
                states = [(self.START_STATE, -1)]
                (pos_player, pos_boxes), last_action = states[-1]
                print_layout_dynamic(
                    self.HAS_WALLS, self.HAS_GOALS, pos_player, pos_boxes, self.colorful
                )
                self.moves = self.pushes = 0
                print_moves_pushes(self.moves, self.pushes)
                continue
            elif key == "z":
                if len(states) > 1:
                    last_action = states.pop()[1]
                else:
                    continue
                pos_player, pos_boxes = states[-1][0]
                print_layout_dynamic(
                    self.HAS_WALLS, self.HAS_GOALS, pos_player, pos_boxes, self.colorful
                )
                self.moves -= 1
                self.pushes -= last_action >= ACTIONS_LEN
                print_moves_pushes(self.moves, self.pushes)
                continue
            idx = KEY_IDX_DICT[key]
            expansion = expanse(self.POS, self.HAS_WALLS, (pos_player, pos_boxes), idx)
            if expansion is None:
                continue
            (pos_player, pos_boxes), last_action = expansion
            self.moves += 1
            self.pushes += last_action >= ACTIONS_LEN
            print_layout_dynamic(
                self.HAS_WALLS, self.HAS_GOALS, pos_player, pos_boxes, self.colorful
            )
            states.append(expansion)
            print_moves_pushes(self.moves, self.pushes)
            if is_win(self.HAS_GOALS, pos_boxes, last_action):
                print("\033[35m\nYOU WON!\033[0m")
                break
