#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn

# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # Top-down construction of behavior tree
    provided_strategy = Selector(name='High Level Ordering of Strategies')

    spread_action = Action(spread_to_optimal_neutral_planet)

    attack_sequence = Sequence(name='Rush Enemy')
    attack_check = Check(have_largest_fleet)
    attack_action = Action(attack_weakest_enemy_planet)
    attack_sequence.child_nodes = [attack_check, attack_action]

    defend_sequence = Sequence(name='Defend While Low')
    defend_check = Check(under_threat)
    defend_action = Action(defend)
    defend_sequence.child_nodes = [defend_check, defend_action]


    provided_strategy.child_nodes = [defend_sequence, spread_action, attack_sequence, Action(spread_to_optimal_enemy_planet), defend_action]
    
    logging.info('\n' + provided_strategy.tree_to_string())

    return provided_strategy

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
