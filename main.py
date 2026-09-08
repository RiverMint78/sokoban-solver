import time
import argparse
from solver import SokobanSolver
from game import SokobanGame

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="\033[35mA Sokoban Game and Solver Based on Traditional Search Algorithms\033[0m")
    parser.add_argument('-l', '--level', type=str, required=True, \
                        help="path to your level file (XSB format is recommended), \033[33meg. --level=\"levels/test1.txt\"\033[0m")
    parser.add_argument('-a', '--algorithm', type=str, choices=["dfs", "bfs", "ucs", "greedy", "astar"], default="dfs", \
                        help="search algorithm to be performed (dfs by default)")
    parser.add_argument('-r', '--random', action="store_true", \
                        help="randomize your search")
    parser.add_argument('-p', '--push', action="store_true",\
                        help="use #pushes as cost, instead of #moves")
    parser.add_argument('-d', '--distance', type=str, choices=["manhattan", "euclidean"], default="manhattan", \
                        help="global distance definition (manhattan by default)")
    parser.add_argument('-f', '--function', type=str, choices=["mk", "trivial", "exp"], default="mk", \
                        help="heuristic function used in heuristic search algorithms (mk by default) \
                        \033[33mMK heuristic based on Munkres Assignment Algorithm \033[31m(can be very slow)\033[33m; \
                        Trivial heuristic returns 0; EXP heuristic uses max distance between player and box not on goal, which is always worse than MK heuristic but faster \
                        \033[34mAll heuristic functions are admissible\033[0m")
    parser.add_argument('-g', '--graphcycle', type=int, default=0,\
                        help="show a dynamic graph of your search \033[33mneeds a positive loop-pre-print number \033[31m(small numbers may slowdown your search extremely)\033[0m")
    parser.add_argument('-c', '--colorful', action="store_true",\
                        help="use colorful graph instead of XSB (will not affect texts)")
    parser.add_argument('-v', '--verbose', action="store_true", \
                        help="\033[33mshow more information\033[0m")
    parser.add_argument('-v2', '--verbose2', action="store_true", \
                        help="\033[34mshow even more information, updates synchronized with graph if both enabled \033[31m(slowdown your search hugely)\033[0m")
    parser.add_argument('-m', '--manual', action="store_true", \
                        help="play your level manual with WASD \033[33mpress 'z' to revert a vaild step, 'e' to revert your level, 'q' to quit\033[0m")
    parser.add_argument('-s', '--sequence', action="store_true", \
                        help="play your level by LURD sequence \033[33m'e' to revert your level, 'q' to quit\033[0m")
    args = parser.parse_args()

    if args.manual:
        game = SokobanGame(path=args.level, verbose=args.verbose, colorful=args.colorful)
        game.step_play()
    elif args.sequence:
        game = SokobanGame(path=args.level, verbose=args.verbose, colorful=args.colorful)
        game.sequence_play()
    else:
        success = False
        solver = SokobanSolver(path=args.level, distance_type=args.distance, pushes_only=args.push, randomize=args.random, \
                               verbose=args.verbose or args.verbose2, verbose2=args.verbose2, graphcycle=args.graphcycle, colorful=args.colorful)
        start_time = time.time()
        try:
            if args.algorithm == "dfs" or args.algorithm == "bfs":
                success = solver.blind_search(args.algorithm)
            elif args.algorithm == "ucs":
                success = solver.heuristic_search(heuristic="trivial", greedy=False)
            elif args.algorithm == "greedy":
                success = solver.heuristic_search(heuristic=args.function, greedy=True)
            elif args.algorithm == "astar":
                success = solver.heuristic_search(heuristic=args.function, greedy=False)
            end_time = time.time()
            print("\033[32mRuntime of %s: %.4f sec\033[0m" % (args.algorithm.upper(), end_time-start_time))
            if not success:
                print("\033[31mNo solution found!\033[0m")
        except KeyboardInterrupt:
            end_time = time.time()
            if args.graphcycle > 0:
                print('\n' * solver.LAYOUT.shape[0])
            if args.verbose2:
                print('\n' * 2)
            print("\033[31mInterrupted!\nRuntime of %s: %.4f sec\033[0m" % (args.algorithm.upper(), end_time-start_time))