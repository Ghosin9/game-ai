import sys
import logging

sys.path.insert(0, '../')
from planet_wars import issue_order

NEARBY = 25
MAX_SHIPS = 100
LOW_SHIPS = 20


def spread_to_nearby_neutral(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)

    neutral_planets = [planet for planet in state.neutral_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    neutral_planets.sort(key=lambda p: p.num_ships)

    for my_planet in my_planets:
        for target_planet in neutral_planets:
            required_ships = target_planet.num_ships + 1
            
            for fleet in state.enemy_fleets():
                if fleet.destination_planet == target_planet.ID:
                    ships_on_arrival = fleet.num_ships - target_planet.num_ships + target_planet.growth_rate * (state.distance(my_planet.ID, target_planet.ID) - fleet.turns_remaining + 1)
                    required_ships = max(ships_on_arrival, target_planet.num_ships)

            distance = state.distance(my_planet.ID, target_planet.ID)

            if my_planet.num_ships > required_ships and distance <= NEARBY:
                return issue_order(state, my_planet.ID, target_planet.ID, required_ships)

    return False


def attack_low_nearby_enemy(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)

    enemy_planets = [planet for planet in state.enemy_planets()
                     if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships)

    for my_planet in my_planets:
        for target_planet in enemy_planets:
            required_ships = target_planet.num_ships + 1 + state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate
            distance = state.distance(my_planet.ID, target_planet.ID)

            if my_planet.num_ships > required_ships and distance <= NEARBY / 3 and target_planet.num_ships <= LOW_SHIPS:
                return issue_order(state, my_planet.ID, target_planet.ID, required_ships)

    return False


def attack_weakest_enemy_planet(state):
    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    elif strongest_planet.num_ships <= MAX_SHIPS:
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def defend(state):
    my_planets = [planet for planet in state.my_planets()]
    if not my_planets:
        return

    def strength(p):
        return p.num_ships \
               + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
               - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    avg = sum(strength(planet) for planet in my_planets) / len(my_planets)

    weak_planets = [planet for planet in my_planets if strength(planet) < avg]
    strong_planets = [planet for planet in my_planets if strength(planet) > avg]

    if (not weak_planets) or (not strong_planets):
        return

    weak_planets = iter(sorted(weak_planets, key=strength))
    strong_planets = iter(sorted(strong_planets, key=strength, reverse=True))

    try:
        weak_planet = next(weak_planets)
        strong_planet = next(strong_planets)
        while True:
            need = int(avg - strength(weak_planet))
            have = int(strength(strong_planet) - avg)

            if have >= need > 0 and enemy_fleet_en_route(state, weak_planet):
                return issue_order(state, strong_planet.ID, weak_planet.ID, need)
                weak_planet = next(weak_planets)
            elif have > 0:
                return issue_order(state, strong_planet.ID, weak_planet.ID, have)
                strong_planet = next(strong_planets)
            else:
                strong_planet = next(strong_planets)

    except StopIteration:
        return


def spread_to_optimal_neutral_planet(state):
    for my_planet in state.my_planets():
        #if my fleet is already en route from this planet skip it
        close_planets = closest_neutral_planets(state, my_planet, 5)

        best_prospect = None #find best close planet to go to
        for close_planet in close_planets:  
            passing = False
            for fleet in state.my_fleets():
                if fleet.destination_planet == close_planet.ID:
                    passing = True
            if passing == False:
                try:
                    if best_prospect == None:
                        best_prospect = close_planet
                    elif close_planet.growth_rate / close_planet.num_ships > best_prospect.growth_rate / best_prospect.num_ships:
                        best_prospect = close_planet
                except: #divide by 0 catch case
                    best_prospect = close_planet
        try: #incase every neutral planet is being spread to
            necessary_ships = best_prospect.num_ships
            for fleet in state.enemy_fleets():
                if fleet.destination_planet == best_prospect.ID:
                    ships_on_arrival = fleet.num_ships \
                        - best_prospect.num_ships \
                        + best_prospect.growth_rate \
                        * (state.distance(my_planet.ID, best_prospect.ID) - fleet.turns_remaining)
                    necessary_ships = max(necessary_ships, ships_on_arrival)
            if best_prospect in state.my_planets():
                return False
            return issue_order(state, my_planet.ID, best_prospect.ID, necessary_ships + 1)
        except:
            return False


def spread_to_optimal_enemy_planet(state):
    for my_planet in state.my_planets():
        #if my fleet is already en route from this planet skip it
        if len(state.enemy_planets()) != 0: #no fleet en route from here
            close_planets = closest_enemy_planets(state, my_planet, 5)

            best_prospect = None #find best close planet to go to
            for close_planet in close_planets:
                passing = False
                for fleet in state.my_fleets():
                    if fleet.destination_planet == close_planet.ID:
                        passing = True
                if passing == False:
                    try:
                        if best_prospect == None:
                            best_prospect = close_planet
                        elif close_planet.growth_rate / close_planet.num_ships > best_prospect.growth_rate / best_prospect.num_ships:
                            best_prospect = close_planet
                    except: #divide by 0 catch case
                        best_prospect = close_planet
            try:
                necessary_ships = best_prospect.num_ships + state.distance(my_planet.ID, best_prospect.ID) * best_prospect.growth_rate
                for fleet in state.enemy_fleets():
                    if fleet.destination_planet == best_prospect.ID:
                        ships_on_arrival = fleet.num_ships \
                            - best_prospect.num_ships \
                            + best_prospect.growth_rate \
                            * (state.distance(my_planet.ID, best_prospect.ID) - fleet.turns_remaining)
                        necessary_ships = max(necessary_ships, ships_on_arrival)
                if best_prospect in state.my_planets():
                    return False
                return issue_order(state, my_planet.ID, best_prospect.ID, necessary_ships + 10)
            except:
                return False


#helper function to return num_planets closest planets to planet
def closest_planets(state, planet, num_planets):
    #setup all planets - the given planet in a list
    distance_sorted_planets = state.planets.copy()
    distance_sorted_planets.remove(planet)

    #sort planets based on distance
    sorted_planets = []
    while distance_sorted_planets:
        prospect = None
        for p in distance_sorted_planets:
            if prospect == None:
                prospect = p
            elif state.distance(planet.ID, p.ID) > state.distance(planet.ID, prospect.ID):
                prospect = p
        sorted_planets.append(prospect)
        distance_sorted_planets.remove(prospect)

    return_planets = []

    for i in range(0, num_planets):
        return_planets.append(sorted_planets.pop())

    return return_planets


def closest_neutral_planets(state, planet, num_planets):
    #setup all planets - the given planet in a list
    distance_sorted_planets = state.neutral_planets().copy()

    #sort planets based on distance
    sorted_planets = []
    while distance_sorted_planets:
        prospect = None
        for p in distance_sorted_planets:
            if prospect == None:
                prospect = p
            elif state.distance(planet.ID, p.ID) > state.distance(planet.ID, prospect.ID):
                prospect = p
        sorted_planets.append(prospect)
        distance_sorted_planets.remove(prospect)

    return_planets = []

    for i in range(0, num_planets):
        if len(sorted_planets) != 0:
            return_planets.append(sorted_planets.pop())

    return return_planets


def closest_enemy_planets(state, planet, num_planets):
    #setup all planets - the given planet in a list
    distance_sorted_planets = state.enemy_planets().copy()

    #sort planets based on distance
    sorted_planets = []
    while distance_sorted_planets:
        prospect = None
        for p in distance_sorted_planets:
            if prospect == None:
                prospect = p
            elif state.distance(planet.ID, p.ID) > state.distance(planet.ID, prospect.ID):
                prospect = p
        sorted_planets.append(prospect)
        distance_sorted_planets.remove(prospect)

    return_planets = []

    for i in range(0, num_planets):
        if len(sorted_planets) != 0:
            return_planets.append(sorted_planets.pop())

    return return_planets


def my_fleet_en_route(state, planet):
    for fleet in state.my_fleets():
        if fleet.destination_planet == planet.ID:
            return fleet
    return None


def enemy_fleet_en_route(state, planet):
    closest_fleet = None
    for fleet in state.enemy_fleets():
        if fleet.destination_planet == planet.ID:
            return fleet
    return None


def neutral_planet_cost(state, planet, source):
    e_fleet = enemy_fleet_en_route(state, planet)
    if e_fleet != None:
        if e_fleet.turns_remaining > state.distance(source.ID, planet.ID):
            return -1
        else:
            return e_fleet.num_ships - planet.num_ships + planet.growth_rate * (state.distance(source.ID, planet.ID) - e_fleet.turns_remaining) + 1
    return planet.num_ships + 1
    

def enemy_planet_cost(state, planet, source):
    e_fleet = enemy_fleet_en_route(state, planet)
    if e_fleet != None:
        return e_fleet.num_ships + planet.num_ships + planet.growth_rate * state.distance(source.ID, planet.ID) + 1
    return + planet.num_ships + planet.growth_rate * state.distance(source.ID, planet.ID) + 1