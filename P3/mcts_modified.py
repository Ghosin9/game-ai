
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 10
explore_faction = 2.

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    
    #return if leaf
    if(len(node.untried_actions)>0):
        leaf_node = node   
        return (leaf_node, state)
    else:
    #calculate UCT for all children
        children = []
        #find whose turn
        myMove=(identity == board.current_player(state))
        for child in node.child_nodes:
            value=UCT(node, node.child_nodes[child],myMove)
            children.append((value,child))
            
        #sort by UCT
        children.sort(key=byVal,reverse=True)
             
        for child in children:
        #call recurusively until a leaf is found
            possible_leaf = node.child_nodes[child[1]]
            possible_leaf_pair = traverse_nodes(possible_leaf, board, board.next_state(state, possible_leaf.parent_action), identity)
            if(possible_leaf != None):
                return possible_leaf_pair
    #if no leaf is found return none    
    return None
   
#sort by first in tuple   
def byVal(e):
    return e[0]

def expand_leaf(node, board, state,identity):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    
    #get random action and remove from untried
    action=choice(node.untried_actions)
    (node.untried_actions).remove(action)
    #make new node with that action and return it
    new_node = MCTSNode(parent=node, parent_action=action, action_list=board.legal_actions(board.next_state(state, action)))
    node.child_nodes[action]=new_node
    return (new_node, board.next_state(state, action))


def rollout(board, state,identity):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    #if game is over return points
    if(board.is_ended(state)):
        return board.points_values(state)
    else:   
        #if some move wins, choose it
        for act in board.legal_actions(state):
            points = board.points_values(board.next_state(state, act))
            if(points!=None and points[identity] == 1):
                return rollout(board, board.next_state(state, act),identity)
        
        #if not make a random choice and call recursively
        action=choice(board.legal_actions(state))
        return rollout(board, board.next_state(state, action),identity) 


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    #add to visits, and wins if won
    node.wins=node.wins+won
    node.visits = node.visits+1
    #return if root, call recursively if not
    if(node.parent == None):
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
    
    #False if there are unexplored actions
    fullyExplored= False
    
    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        
        #traverse, returns node and state
        pair = traverse_nodes(node, board, sampled_game, identity_of_bot)
        #if pair is none, then all nodes are explored, and we can stop searching
        if(pair == None):
            fullyExplored=True
            break
        
        #use found node and state to make a new node and state
        new_pair = expand_leaf(pair[0], board, pair[1], identity_of_bot)
        
        #simulate game to end, return points
        points = rollout(board, board.next_state(new_pair[1], new_pair[0].parent_action),identity_of_bot)
        
        #if we won, then set won to 1, if not 0
        '''if(points[identity_of_bot]==1):
            won=1
        else:
            won=0'''
        won = points[identity_of_bot]
        #give this information to all nodes on path    
        backpropagate(new_pair[0],won)
        
        

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best =[]
    #search all children of root
    for child in root_node.child_nodes:
        loose = False
        model_state=state
        child_node=root_node.child_nodes[child]
        model_state = board.next_state(model_state,child_node.parent_action)
        #check for failing child
        for grand in child_node.child_nodes:
            grandChild = child_node.child_nodes[grand]
            model_state = board.next_state(model_state,grandChild.parent_action)
            points = board.points_values(model_state)
            if(points!=None and points[identity_of_bot]==-1):
                loose=True
                break
        #if fully explored then pick best win rate
        if(fullyExplored):
            best.append((child_node.wins/child_node.visits,child_node,loose))
        else:
        #if not then pick most visited
            best.append((child_node.visits,child_node,loose))
    #sort by win/visit rate
    best.sort(key=byVal,reverse=True)
    #return best without failing child
    for n in best:
        if(n[2]==False):
            return n[1].parent_action
        
    #if not possible return best
    return best[0][1].parent_action
    
    
#return UCT value
def UCT(node, child, myMove):
    winRate = child.wins/child.visits
    #if not my turn use opponants win rate
    if(myMove==False):
        winRate=1-winRate
    exploration = log(node.visits)/child.visits
    return winRate+explore_faction*sqrt(exploration)