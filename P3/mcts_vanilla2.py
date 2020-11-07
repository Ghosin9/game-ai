from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 50
explore_faction = 1.8


def uct(node, child, board, state, identity):
    if identity == board.current_player(state):
        win_rate = child.wins / child.visits
    else:
        win_rate = 1 - (child.wins / child.visits)

    explore = explore_faction * (sqrt(log(node.visits) / child.visits))
    uct_num = win_rate + explore

    return uct_num


def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """

    # if there are untried actions, automatically a leaf node
    if len(node.untried_actions) > 0:
        return node, state
    else:
        max_uct = 0
        max_child = None

        # for each child node
        for child in node.child_nodes:
            child_node = node.child_nodes[child]

            num = uct(node, child_node, board, state, identity)
            if num > max_uct:
                max_uct = num
                max_child = child_node

        if max_child is None:
            return None

        next_state = board.next_state(state, max_child.parent_action)
        return traverse_nodes(max_child, board, next_state, identity)

    return None
    # Hint: return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """

    # choose a random action from untried actions
    action = choice(node.untried_actions)
    # remove the action
    node.untried_actions.remove(action)

    # next state
    next_state = board.next_state(state, action)
    # create the new node
    new_node = MCTSNode(parent=node, parent_action=action, action_list=board.legal_actions(next_state))

    # add the new node to the child nodes of the parent node
    node.child_nodes[action] = new_node

    return new_node, next_state
    # Hint: return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    # while the game is not over
    if board.is_ended(state):
        return board.points_values(state)
    else:
        # make a random action
        random_action = choice(board.legal_actions(state))

        # recursively call until the game is over
        return rollout(board, board.next_state(state, random_action))
    # points_values stores a dictionary with the score for each player


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    node.wins += won
    node.visits += 1

    if node.parent is None:
        return node
    else:
        backpropagate(node.parent, won)


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        # run the 4 steps, selection, expansion, rollout and backprop
        leaf_node = traverse_nodes(node, board, sampled_game, identity_of_bot)

        # if we have no more leaf nodes to run MCTS on, we are done
        if leaf_node is None:
            break

        # expand at the leaf node
        expanded_node, expanded_state = expand_leaf(leaf_node[0], board, leaf_node[1])

        # rollout using the new node's parent action
        # winner keeps track if the player won with a 1, and lost with a -1
        next_state = board.next_state(expanded_state, expanded_node.parent_action)
        winner = rollout(board, next_state)

        # back prop
        backpropagate(expanded_node, winner.get(identity_of_bot))

        # print("on step: ", step)

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.

    best_wins = -1000
    best_child = None

    for child in node.child_nodes:
        child_node = node.child_nodes[child]

        value = child_node.wins/child_node.visits

        if value > best_wins:
            best_wins = value
            best_child = child_node

    return best_child.parent_action
