import heapq, sys
from config import *
from math import dist
from munkres import Munkres
from random import random, shuffle

MK = Munkres()
class PriorityQueue:
    def  __init__(self):
        self.heap = []
        self.count = 0
    def push(self, item, priority: int | float):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1
    def pop(self):
        return heapq.heappop(self.heap)
    def isempty(self):
        return len(self.heap) == 0
    def __len__(self):
        return len(self.heap)

def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
def euclidean(a: tuple[int, int], b: tuple[int, int]) -> float:
    return dist(a, b)
    
def get_pos_player(POS: list[list[tuple[int, int]]], LAYOUT: np.ndarray) -> tuple[int, int]:
    x, y = np.argwhere((LAYOUT == 1) | (LAYOUT == 5))[0]
    return POS[x][y]
def get_pos_boxes(POS: list[list[tuple[int, int]]], LAYOUT: np.ndarray) -> tuple[tuple[int, int], ...]:
    return tuple(POS[x][y] for x, y in np.argwhere((LAYOUT == 3) | (LAYOUT == 6)))
def is_win(HAS_GOALS: np.ndarray, pos_boxes: tuple[tuple[int, int], ...], last_action: int) -> bool:
    if last_action < ACTIONS_LEN:
        return False
    return all(HAS_GOALS[box] for box in pos_boxes)
def is_lose(POS: list[list[tuple[int, int]]], HAS_GOALS: np.ndarray, HAS_WALLS: np.ndarray, pos_boxes: tuple[tuple[int, int], ...], last_action: int) -> bool:
    if last_action < ACTIONS_LEN and last_action != -1:
        return False
    for box in pos_boxes:
        if HAS_GOALS[box]:
            continue
        board = (POS[box[0]-1][box[1]-1], POS[box[0]-1][box[1]], POS[box[0]-1][box[1]+1],
                    POS[box[0]][box[1]-1], POS[box[0]][box[1]], POS[box[0]][box[1]+1],
                    POS[box[0]+1][box[1]-1], POS[box[0]+1][box[1]], POS[box[0]+1][box[1]+1])
        for pattern in TRANS_PATTERNS:
            if HAS_WALLS[board[pattern[5]]]:
                if HAS_WALLS[board[pattern[1]]]:
                    return True
                if board[pattern[1]] in pos_boxes:
                    if HAS_WALLS[board[pattern[2]]]:
                        return True
                    if HAS_WALLS[board[pattern[0]]]:
                        return True
            elif board[pattern[5]] in pos_boxes:
                if board[pattern[1]] in pos_boxes:
                    if HAS_WALLS[board[pattern[2]]]:
                        return True
                    if board[pattern[2]] in pos_boxes:
                        return True
    return False

def expanse(POS: list[list[tuple[int, int]]], HAS_WALLS: np.ndarray, state: STATE_TYPING, action_idx: int) -> tuple[STATE_TYPING, int] | None:
    if action_idx < 0 or action_idx >= ACTIONS_LEN*2:
        return
    if action_idx >= ACTIONS_LEN:
        action_idx -= ACTIONS_LEN
    pos_player, pos_boxes = state
    new_pos_player = POS[pos_player[0] + ACTIONS[action_idx,0]][pos_player[1] + ACTIONS[action_idx,1]]
    if HAS_WALLS[new_pos_player]:
        return
    if new_pos_player in pos_boxes:
        new_pos_box = POS[pos_player[0] + ACTIONS[action_idx,0]*2][pos_player[1] + ACTIONS[action_idx,1]*2]
        if HAS_WALLS[new_pos_box]:
            return
        idx = -1
        for j in range(len(pos_boxes)):
            if pos_boxes[j] is new_pos_box:
                idx = -1
                break
            if pos_boxes[j] is new_pos_player:
                idx = j
        if idx == -1:
            return
        new_pos_boxes = pos_boxes[:idx] + (new_pos_box,) if idx == len(pos_boxes) - 1 \
            else pos_boxes[:idx] +(new_pos_box,) + pos_boxes[idx+1:]
        return ((new_pos_player, new_pos_boxes), action_idx + ACTIONS_LEN)
    return ((new_pos_player, pos_boxes), action_idx)
def get_expansions(POS: list[list[tuple[int, int]]], HAS_WALLS: np.ndarray, state: STATE_TYPING, randomize: bool) -> list[tuple[STATE_TYPING, int]]:
    expansions = []
    if randomize:
        shuffle(actions_idxes)
    for i in actions_idxes:
        expansion = expanse(POS, HAS_WALLS, state, i)
        if expansion is not None:
            expansions.append(expansion)
    return expansions

def get_actions_cost(actions: list[int], pushes_only: bool) -> int:
    return len([0 for action in actions if action >= ACTIONS_LEN]) if pushes_only else len(actions) - 1
def get_cost_matrix(distance: DISTANCE_TYPING, POS_GOALS: tuple[tuple[int, int], ...], pos_boxes: tuple[tuple[int, int], ...]) -> list[list[int|float]]:
    return [[distance(a, b) for a in POS_GOALS] for b in pos_boxes]
def mk_heuristic(distance: DISTANCE_TYPING, POS_GOALS: tuple[tuple[int, int], ...], HAS_GOALS: np.ndarray, \
                 pos_player: tuple[int, int], pos_boxes: tuple[tuple[int, int], ...], randomize: bool) -> int | float:
    cost_matrix = get_cost_matrix(distance, POS_GOALS, pos_boxes)
    total_cost = 0
    for row, column in MK.compute(cost_matrix):
        total_cost += cost_matrix[row][column]
    dis_of_box = 0
    for box in pos_boxes:
        if not HAS_GOALS[box]:
            dis_of_box = max(dis_of_box, distance(pos_player, box))
    total_cost += max(dis_of_box - 1, 0)
    return total_cost + random() if randomize else total_cost
def trival_heuristic(distance: DISTANCE_TYPING, POS_GOALS: tuple[tuple[int, int], ...], HAS_GOALS: np.ndarray, \
                 pos_player: tuple[int, int], pos_boxes: tuple[tuple[int, int], ...], randomize: bool) -> int | float:
    return random() if randomize else 0
def exp_heuristic(distance: DISTANCE_TYPING, POS_GOALS: tuple[tuple[int, int], ...], HAS_GOALS: np.ndarray, \
                 pos_player: tuple[int, int], pos_boxes: tuple[tuple[int, int], ...], randomize: bool) -> int | float:
    dis_of_box = 0
    for box in pos_boxes:
        if not HAS_GOALS[box]:
            dis_of_box = max(dis_of_box, distance(pos_player, box))
    total_cost = max(dis_of_box - 1, 0)
    return total_cost + random() if randomize else total_cost

def layout_parser(path: str) -> np.ndarray:
    with open(path, 'r', encoding="utf-8") as file:
        layout = file.readlines()
    layout = [list(LAYOUT_PATTERN.sub('', row)) for row in layout]
    row_len = max(len(row) for row in layout)
    for row in layout:
        if len_df := row_len - len(row):
            row.extend(['-'] * len_df)
        for i in range(row_len):
            row[i] = LAYOUT_DICT[row[i]]
    return np.array(layout, dtype=np.uint8)

def print_layout_static(layout: np.ndarray, colorful: bool=False) -> None:
    print_lst = COLORFUL_PRINT_LST if colorful else XSB_PRINT_LST
    for row in layout:
        for x in row:
            print(print_lst[x], end='')
        sys.stdout.write('\n')
def print_layout_dynamic(HAS_WALLS: np.ndarray, HAS_GOALS: np.ndarray, pos_player: tuple[int, int], pos_boxes: tuple[tuple[int, int], ...], colorful: bool=False) -> None:
    print_lst = COLORFUL_PRINT_LST if colorful else XSB_PRINT_LST
    n, m = HAS_WALLS.shape
    sys.stdout.write(f"\x1B[{n}A")
    for i in range(n):
        for j in range(m):
            x = (i,j)
            if HAS_WALLS[x]:
                sys.stdout.write(print_lst[4])
            elif x == pos_player:
                if HAS_GOALS[x]:
                    sys.stdout.write(print_lst[5])
                else:
                    sys.stdout.write(print_lst[1])
            elif x in pos_boxes:
                if HAS_GOALS[x]:
                    sys.stdout.write(print_lst[6])
                else:
                    sys.stdout.write(print_lst[3])
            elif HAS_GOALS[x]:
                sys.stdout.write(print_lst[2])
            else:
                sys.stdout.write(print_lst[0])
        sys.stdout.write('\n')
def print_moves_pushes(moves: int, pushes: int):
    print("\033[33m#Moves:%5d  #Pushes:%5d\033[0m\x1B[1A" % (moves, pushes))
def action_parser(action_idxes: list[int]) -> str:
    parsed_actions = ""
    for idx in action_idxes:
        if idx < 0:
            continue
        name = ACTIONS_DICT[idx  % ACTIONS_LEN]
        parsed_actions += name if idx < ACTIONS_LEN else name.upper()
    return parsed_actions
def action_complier(actions: str) -> list[int]:
    complied_actions = []
    for action in actions:
        idx = ACTIONS_DICT.get(action)
        if isinstance(idx, int):
            complied_actions.append(idx)
    return complied_actions