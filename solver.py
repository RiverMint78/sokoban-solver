from util import (
    euclidean,
    manhattan,
    layout_parser,
    get_pos_player,
    get_pos_boxes,
    print_layout_dynamic,
    print_layout_static,
    action_parser,
    get_actions_cost,
    is_win,
    is_lose,
    get_expansions,
    mk_heuristic,
    trival_heuristic,
    exp_heuristic,
    HEURISTIC_DICT,
    PriorityQueue,
)
import sys
import numpy as np

from collections import deque


class SokobanSolver:
    def __init__(
        self,
        path: str,
        distance_type: str,
        pushes_only: bool,
        randomize: bool,
        verbose: bool,
        verbose2: bool,
        graphcycle: int,
        colorful: bool,
    ):
        self.distance = euclidean if distance_type == "euclidean" else manhattan
        self.pushes_only = pushes_only
        self.randomize = randomize
        self.verbose = verbose or verbose2
        self.verbose2 = verbose2
        self.graphcycle = graphcycle
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
        if self.verbose:
            print(f'\033[33mLevel loaded from "{path}":')
            print_layout_static(self.LAYOUT, False)
            print("\033[0m\n", end="")
            print("Solving...")
        if self.graphcycle > 0:
            if not self.verbose:
                print("Solving...")
            print("\n" * (row_len - 1))

    def blind_search(self, search_type: str) -> bool:
        closed_lst = set()
        open_lst = deque([(self.START_STATE, [-1])])
        get_next = open_lst.popleft if search_type == "bfs" else open_lst.pop
        loop_cnt = 0
        while len(open_lst) > 0:
            state, actions = get_next()
            if self.graphcycle > 0 and loop_cnt % self.graphcycle == 0:
                print_layout_dynamic(
                    self.HAS_WALLS, self.HAS_GOALS, state[0], state[1], self.colorful
                )
            if self.verbose2:
                if (
                    loop_cnt % 99 == 0
                    or self.graphcycle > 0
                    and loop_cnt % self.graphcycle == 0
                ):
                    print("\033[34m", end="")
                    print(
                        "Close Length: %10d\tClose Size (KB): %16.2f"
                        % (len(closed_lst), sys.getsizeof(closed_lst, 0) / 1024.0)
                    )
                    print(
                        "Open  Length: %10d\tOpen  Size (KB): %16.2f"
                        % (len(open_lst), sys.getsizeof(open_lst, 0) / 1024.0)
                    )
                    print("Loop   Count: %10d" % loop_cnt)
                    print("\033[0m", end="")
                    sys.stdout.write("\x1b[3A")
            if is_win(self.HAS_GOALS, state[1], actions[-1]):
                if self.verbose2:
                    print("\n" * 2)
                if self.graphcycle > 0:
                    print("\n" * self.LAYOUT.shape[0])
                    print("\033[35m", end="")
                    print_layout_dynamic(
                        self.HAS_WALLS,
                        self.HAS_GOALS,
                        state[0],
                        state[1],
                        self.colorful,
                    )
                print("\033[32mSolution: " + action_parser(actions))
                print(
                    f"#Moves/#Pushes: {get_actions_cost(actions, False)}/{get_actions_cost(actions, True)}\033[0m"
                )
                if self.verbose:
                    print("\033[33m", end="")
                    print(
                        "Close Length: %10d\tClose Size (KB): %16.2f"
                        % (len(closed_lst), sys.getsizeof(closed_lst, 0) / 1024.0)
                    )
                    print(
                        "Open  Length: %10d\tOpen  Size (KB): %16.2f"
                        % (len(open_lst), sys.getsizeof(open_lst, 0) / 1024.0)
                    )
                    print("Loop   Count: %10d" % loop_cnt)
                    print("\033[0m", end="")
                return True
            if state not in closed_lst:
                closed_lst.add(state)
                for new_state, new_action in get_expansions(
                    self.POS, self.HAS_WALLS, state, self.randomize
                ):
                    if not is_lose(
                        self.POS,
                        self.HAS_GOALS,
                        self.HAS_WALLS,
                        new_state[1],
                        new_action,
                    ):
                        open_lst.append((new_state, actions + [new_action]))
            loop_cnt += 1
        return False

    def heuristic_search(self, heuristic: str, greedy: bool = False) -> bool:
        h = (mk_heuristic, trival_heuristic, exp_heuristic)[HEURISTIC_DICT[heuristic]]
        g = (lambda x, y: 0) if greedy else get_actions_cost
        closed_lst = set()
        open_lst = PriorityQueue()
        open_lst.push(
            (self.START_STATE, [-1]),
            priority=h(
                self.distance,
                self.POS_GOALS,
                self.HAS_GOALS,
                self.START_STATE[0],
                self.START_STATE[1],
                self.randomize,
            ),
        )
        loop_cnt = 0
        while not open_lst.isempty():
            priority, _, item = open_lst.pop()
            state, actions = item
            if self.graphcycle > 0 and loop_cnt % self.graphcycle == 0:
                print_layout_dynamic(
                    self.HAS_WALLS, self.HAS_GOALS, state[0], state[1], self.colorful
                )
            if self.verbose2:
                if (
                    loop_cnt % 99 == 0
                    or self.graphcycle > 0
                    and loop_cnt % self.graphcycle == 0
                ):
                    print("\033[34m", end="")
                    print(
                        "Close Length: %9d  Close Size (KB): %10.2f"
                        % (len(closed_lst), sys.getsizeof(closed_lst, 0) / 1024.0)
                    )
                    print(
                        "Open  Length: %9d  Open  Size (KB): %10.2f"
                        % (len(open_lst), sys.getsizeof(open_lst.heap, 0) / 1024.0)
                    )
                    print(
                        "Loop   Count: %9d  State  Priority: %10.2f"
                        % (loop_cnt, priority)
                    )
                    print("\033[0m", end="")
                    sys.stdout.write("\x1b[3A")
            if is_win(self.HAS_GOALS, state[1], actions[-1]):
                if self.verbose2:
                    print("\n" * 2)
                if self.graphcycle > 0:
                    print("\n" * self.LAYOUT.shape[0])
                    print("\033[35m", end="")
                    print_layout_dynamic(
                        self.HAS_WALLS,
                        self.HAS_GOALS,
                        state[0],
                        state[1],
                        self.colorful,
                    )
                print("\033[32mSolution: " + action_parser(actions))
                print(
                    f"#Moves/#Pushes: {get_actions_cost(actions, False)}/{get_actions_cost(actions, True)}\033[0m"
                )
                if self.verbose:
                    print("\033[33m", end="")
                    print(
                        "Close Length: %9d  Close Size (KB): %10.2f"
                        % (len(closed_lst), sys.getsizeof(closed_lst, 0) / 1024.0)
                    )
                    print(
                        "Open  Length: %9d  Open  Size (KB): %10.2f"
                        % (len(open_lst), sys.getsizeof(open_lst.heap, 0) / 1024.0)
                    )
                    print(
                        "Loop   Count: %9d  State  Priority: %10.2f"
                        % (loop_cnt, priority)
                    )
                    print("\033[0m", end="")
                return True
            if state not in closed_lst:
                closed_lst.add(state)
                for new_state, new_action in get_expansions(
                    self.POS, self.HAS_WALLS, state, False
                ):
                    if not is_lose(
                        self.POS,
                        self.HAS_GOALS,
                        self.HAS_WALLS,
                        new_state[1],
                        new_action,
                    ):
                        new_actions = actions + [new_action]
                        open_lst.push(
                            (new_state, new_actions),
                            priority=g(new_actions, self.pushes_only)
                            + h(
                                self.distance,
                                self.POS_GOALS,
                                self.HAS_GOALS,
                                new_state[0],
                                new_state[1],
                                self.randomize,
                            ),
                        )
            loop_cnt += 1
        return False
