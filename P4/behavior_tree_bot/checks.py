def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > (sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())) \
             * 1.1 #make sure we have a little lee-way before we start rushing


def steal_opportunity(state):
    for fleet in state.enemy_fleets():
        destination = fleet.destination_planet
        for planet in state.neutral_planets():
            if destination == planet.ID:
                return True
    return False


def have_smaller_fleet(state):
    return (sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets())) * 1.1 \
           < sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets()) \



def under_threat(state):
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in state.my_planets():
            return True
    return False


