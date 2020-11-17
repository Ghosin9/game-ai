import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
import math

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        """
        for item in rule['Consumes']
            if state does not have item
                return false
        for item in rule["Requires"]
            if state does not have item(s)
                return false
        """
        if "Consumes" in rule:
            for item in rule["Consumes"]:
                if  state[item] < rule["Consumes"][item]:
                    return False

        if "Requires" in rule:
            for item in rule["Requires"]:
                if state[item] == 0:
                    return False

        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].

        # consume the amount of items needed
        # produce the given items
        next_state = state.copy()

        # producing items
        for item in rule["Produces"]:
            next_state[item] = next_state[item] + rule["Produces"][item]

        # consuming Items
        if "Consumes" in rule:
            for item in rule["Consumes"]:
                next_state[item] = next_state[item] - rule["Consumes"][item]

        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for item in goal:

            if state[item] < goal[item]:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    """need_cobble = True
    need_coal = True
    cobble_acquired = 0
    coal_acquired = 0
    cobble_acquired = cobble_acquired + state["cobble"]
    cobble_acquired = cobble_acquired + state["stone_pickaxe"]*3
    cobble_acquired = cobble_acquired + state["furnace"]*8
    cobble_acquired = cobble_acquired + state["stone_axe"]*3
    cobble_to_go = total_cobble - cobble_acquired


    coal_acquired = coal_acquired + state["coal"]
    coal_acquired = coal_acquired + state["ingot"]
    coal_acquired = coal_acquired + state["cart"]*5
    coal_acquired = coal_acquired + state["iron_axe"]*3
    coal_acquired = coal_acquired + state["iron_pickaxe"]*3
    coal_acquired = coal_acquired + math.ceil(state["rail"]/16)*6
    coal_to_go = total_coal - coal_acquired

    if cobble_to_go < 1:
        need_cobble = False

    if coal_to_go < 1:
        need_coal = False"""

    for r in all_recipes:
        if r.check(state):
            """if need_cobble == False and (r.name == "wooden_pickaxe for cobble" or r.name == "stone_pickaxe for cobble" or r.name == "iron_pickaxe for cobble"):
                continue

            if need_coal == False and (r.name == "wooden_pickaxe for coal" or r.name == "stone_pickaxe for coal" or r.name == "iron_pickaxe for coal"):
                continue"""
            # don't remake tools
            if state["bench"] > 0 and r.name == "craft bench":
                continue

            if state["furnace"] > 0 and r.name == "craft furnace at bench":
                continue

            if state["wooden_pickaxe"] > 0 and r.name == "craft wooden_pickaxe at bench":
                continue

            if state["stone_pickaxe"] > 0:
                if r.name == "craft stone_pickaxe at bench":
                    continue
                if r.name == "wooden_pickaxe for cobble":
                    continue
                if r.name == "wooden_pickaxe for coal":
                    continue

            if state["iron_pickaxe"] > 0:
                if r.name == "craft iron_pickaxe at bench":
                    continue
                if r.name == "wooden_pickaxe for cobble":
                    continue
                if r.name == "wooden_pickaxe for coal":
                    continue
                if r.name == "stone_pickaxe for cobble":
                    continue
                if r.name == "stone_pickaxe for coal":
                    continue
                if r.name == "stone_pickaxe for ore":
                    continue

            if state["wooden_axe"] > 0:
                if r.name == "craft wooden_axe at bench":
                    continue
                if r.name == "punch for wood":
                    continue

            if state["stone_axe"] > 0:
                if r.name == "craft stone_axe at bench":
                    continue
                if r.name == "punch for wood":
                    continue
                if r.name == "wooden_axe for wood":
                    continue

            if state["iron_axe"] > 0:
                if r.name == "craft stone_axe at bench":
                    continue
                if r.name == "punch for wood":
                    continue
                if r.name == "wooden_axe for wood":
                    continue
                if r.name == "stone_axe for wood":
                    continue

            yield (r.name, r.effect(state), r.cost)


def heuristic(state, next_state, recipe_name):
    # Implement your heuristic here!
    total_ingots_needed = 0;
    total_ingots_acquired = 0;
    ingots_to_go = 0;

    sticks_needed_for_rails = 0
    current_sticks = 0;

    """if "ingot" in Crafting['Goal']:
        total_ingots_needed = total_ingots_needed + Crafting['Goal']["ingot"]
    if "iron_pickaxe" in Crafting['Goal']:
        total_ingots_needed = total_ingots_needed + Crafting['Goal']["iron_pickaxe"] * 3
    if "iron_axe" in Crafting['Goal']:
        total_ingots_needed = total_ingots_needed + Crafting['Goal']["iron_axe"] * 3
    if "cart" in Crafting['Goal']:
        total_ingots_needed = total_ingots_needed + Crafting['Goal']["cart"] * 5
    if "rail" in Crafting['Goal']:
        total_ingots_needed = total_ingots_needed + math.ceil(Crafting['Goal']["rail"]/16) * 6"""


    """if "rail" in Crafting['Goal']:
        sticks_needed_for_rails = math.ceil(Crafting['Goal']["rail"]/16)

    current_sticks = state["stick"]

    if current_sticks < sticks_needed_for_rails:
        if recipe_name == "craft stick":
            return -9000
        if recipe_name == "punch for wood" or recipe_name == "wood_axe for wood" or recipe_name == "stone_axe for wood" or recipe_name == "iron_axe for wood":
            return -8000"""

    if "iron_pickaxe" in Crafting['Goal']:
        if state["iron_pickaxe"] < Crafting['Goal']["iron_pickaxe"] and recipe_name == "craft iron_pickaxe at bench":
            return -200000
    if "cart" in Crafting['Goal']:
        if state["cart"] < Crafting['Goal']["cart"] and recipe_name == "craft cart at bench":
            return -200000

    if "rail" in Crafting['Goal']:
        if state["rail"] < Crafting['Goal']["rail"] and recipe_name == "craft rail at bench":
            return -200000

    if "cart" in Crafting['Goal'] and "rail" in Crafting['Goal'] and state["iron_pickaxe"] < 1:
        if recipe_name == "craft iron_pickaxe at bench":
            return -200000
    #print(total_ingots_needed)

    total_ingots_acquired = state["ore"] + state["ingot"] + state["iron_pickaxe"]*3 + state["iron_axe"]*3 + state["cart"]*5 + math.ceil(state["rail"]/16)*6
    total_coal_acquired = state["coal"] + state["ingot"] + state["iron_pickaxe"]*3 + state["iron_axe"]*3 + state["cart"]*5 + math.ceil(state["rail"]/16)*6
    ingots_to_go = total_ingots - total_ingots_acquired
    coal_to_go = total_coal - total_coal_acquired

    if ingots_to_go > 0 and (recipe_name == "stone_pickaxe for ore" or recipe_name == "iron_pickaxe for ore"):
        return -100000
    if coal_to_go > 0 and (recipe_name == "stone_pickaxe for coal" or recipe_name == "iron_pickaxe for coal"):
        return -100000

    # prioritize smelting
    if state["ore"] > total_ore and recipe_name == "smelt ore in furnace" and \
    ("ingot" in Crafting['Goal'] or "iron_axe" in Crafting['Goal'] or "iron_pickaxe" in Crafting['Goal'] or "cart" in Crafting['Goal'] or "rail" in Crafting['Goal']):
        return -10000

    if is_goal(next_state):
        return -10000000


    #

    return 0

def search(graph, state, is_goal, limit, heuristic):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state

    # # The priority queue
    queue = [(0, (0, state))]
    #
    # # The dictionary that will be returned with the costs
    costs = {}
    costs[state] = 0
    #
    # # The dictionary that will store the backpointers
    backpointers = {}
    backpointers[state] = (None, None)


    while time() - start_time < limit:

        #while queue:
        prio, current = heappop(queue)
        current_cost = current[0]
        current_state = current[1]
        #print(current_state)


        # Check if current node is the destination
        if is_goal(current_state):

            # List containing all cells from initial_position to destination
            path = [(current_state, backpointers[current_state][1])]

            # Go backwards from destination until the source using backpointers
            # and add all the nodes in the shortest path into a list
            current_back = backpointers[current_state][0]
            while current_back is not None:
                path.append((current_back, backpointers[current_back][1]))
                current_back = backpointers[current_back][0]

            print("Compute Time:", time() - start_time)
            print("Cost:", costs[current_state])
            print("Len:", len(path)-1)
            return path[::-1]

        # Calculate cost from current note to all the adjacent ones
        for adj_name, adj_state, adj_cost in graph(current_state):
            pathcost = current_cost + adj_cost

            # print("adding to queue:", adj_name, "cost:", adj_cost)

            # If the cost is new
            if adj_state not in costs or pathcost < costs[adj_state]:
                costs[adj_state] = pathcost
                priority = pathcost#heuristic(current_state, adj_name)

                backpointers[adj_state] = (current_state, adj_name)
                heappush(queue, (heuristic(current_state, adj_state, adj_name), (pathcost, adj_state)))

    #return None


    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])
    """print("keys", state.keys())
    print("values", state.values())"""

    total_ore = 0
    total_ingots = 0;
    if "ore" in Crafting['Goal']:
        total_ingots = total_ingots + Crafting['Goal']["ore"]
        total_ore = Crafting['Goal']["ore"]
    if "ingot" in Crafting['Goal']:
        total_ingots = total_ingots + Crafting['Goal']["ingot"]
    if "iron_pickaxe" in Crafting['Goal']:
        total_ingots = total_ingots + Crafting['Goal']["iron_pickaxe"] * 3
    if "iron_axe" in Crafting['Goal']:
        total_ingots = total_ingots + Crafting['Goal']["iron_axe"] * 3
    if "cart" in Crafting['Goal']:
        total_ingots = total_ingots + Crafting['Goal']["cart"] * 5
    if "rail" in Crafting['Goal']:
        total_ingots = total_ingots + math.ceil(Crafting['Goal']["rail"]/16) * 6
    if "rail" in Crafting['Goal'] and "cart" in Crafting['Goal'] and not "iron_pickaxe" in Crafting['Goal']:
        total_ingots = total_ingots + 3
    #print(total_ingots)
    total_coal = total_ingots - total_ore


    #print(total_ore)

    """total_cobble = 0;
    if "cobble" in Crafting['Goal']:
        total_cobble = total_cobble + Crafting['Goal']["cobble"]
    if "furnace" in Crafting['Goal'] or total_ingots > 0:
        total_cobble = total_cobble + 11
    elif "stone_pickaxe" in Crafting['Goal']:
        total_cobble = total_cobble + 3
    if "stone_axe" in Crafting['Goal']:
        total_cobble = total_cobble + 3
    print(total_cobble)"""

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print(action)
            print('\t',state)
            #print(action)
