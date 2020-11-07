import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
import math

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])

Tools = ["bench", "furnace", "wooden_pickaxe", "stone_pickaxe", "iron_pickaxe", "wooden_axe", "stone_axe", "iron_axe"]

goal = {}
needed_consumes = {}
needed_requires = {}
recipes = {}

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
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(current_state, next_state):
    # Implement your heuristic here!

    # if you reach your goal, prioritize
    if is_goal(next_state):
        print("next goal")
        return -math.inf

    # don't remake Tools
    for item, quantity in next_state.items():
        if item in Tools:
            if quantity > 1:
                return math.inf

    # prioritize getting requires that give you goal consumes
    # for needed_item in needed_consumes:
        # print("need", needed_item)
        # if needed_consumes[needed_item] > 0:
        #     # print("need amount", needed_consumes[needed_item])
        #     if next_state[needed_item] > current_state[needed_item]:
        #         print("item", needed_item, "next state", next_state[needed_item])
        #         print("current state", current_state[needed_item])
        #         needed_consumes[needed_item] = needed_consumes[needed_item]-next_state[needed_item]
        #         return -math.inf

    # for item in needed_requires:
    #     for name, rule in recipes.items():
    #         if item in rule["Produces"]:
    #             for consumes in rule["Consumes"]:
    #                 if consumes in current_state:


    # prioritize getting goal consumes (getting items that complete your goal)
    # for needed_item in needed_consumes:
    #     print("need", needed_item, "amount", needed_consumes[needed_item])
    #     print("have", current_state[needed_item])
    #     print("will have", next_state[needed_item])
    #     # if the item is in the next state, prioritize
    #     if current_state[needed_item] < next_state[needed_item]:
    #         # if there is enough of the item
    #         print("next state gives items", state)
    #         return -math.inf

    return 0

def search(graph, state, is_goal, limit, heuristic):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state

    # # The priority queue
    queue = [(0, state)]
    #
    # # The dictionary that will be returned with the costs
    costs = {}
    costs[state] = 0
    #
    # # The dictionary that will store the backpointers
    backpointers = {}
    backpointers[state] = (None, None)


    while queue and time() - start_time < limit:

        #while queue:
        current_cost, current_state = heappop(queue)

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
                priority = pathcost + heuristic(current_state, adj_state)

                # print("from cur state", current_state)
                # print("adding to q", adj_state, "prio", priority)

                backpointers[adj_state] = (current_state, adj_name)
                heappush(queue, (priority, adj_state))

    #return None


    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # List of items in your initial inventory with amounts:
    print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    recipes = Crafting['Recipes'].copy()
    goal = Crafting['Goal'].copy()
    for item, quantity in goal.items():
        for name, rule in recipes.items():
            if item in rule["Produces"]:
                needed_consumes = dict(rule["Consumes"])
                needed_requires = dict(rule["Requires"])

    print(needed_consumes)
    print(needed_requires)

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])
    """print("keys", state.keys())
    print("values", state.values())"""

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print(action)
            print('\t',state)
            #print(action)
