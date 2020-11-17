import copy
import heapq
import metrics
import multiprocessing.pool as mpool
import os
import random
import shutil
import time
import math

width = 200
height = 16

options = [
    "-",  # an empty space
    "X",  # a solid wall
    "?",  # a question mark block with a coin
    "M",  # a question mark block with a mushroom
    "B",  # a breakable block
    "o",  # a coin
    "|",  # a pipe segment
    "T",  # a pipe top
    "E",  # an enemy
    #"f",  # a flag, do not generate
    #"v",  # a flagpole, do not generate
    #"m"  # mario's start position, do not generate
]

# The level as a grid of tiles


class Individual_Grid(object):
    __slots__ = ["genome", "_fitness"]

    def __init__(self, genome):
        self.genome = copy.deepcopy(genome)
        self._fitness = None

    # Update this individual's estimate of its fitness.
    # This can be expensive so we do it once and then cache the result.
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Print out the possible measurements or look at the implementation of metrics.py for other keys:
        # print(measurements.keys())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Modify this, and possibly add more metrics.  You can replace this with whatever code you like.
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=2.0
        )
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients))
        return self

    # Return the cached fitness value or calculate it as needed.
    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    # Mutate a genome into a new genome.  Note that this is a _genome_, not an individual!
    def mutate(self, genome):
        # STUDENT implement a mutation operator, also consider not mutating this individual
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc

        # left = 1
        # right = width - 1
        # for y in range(height):
        #     for x in range(left, right):
        #         pass
        # return genome

        # pick a random column and row, i.e. coordinate
        to_change_col = random.randint(2, width - 7)
        to_change_row = random.randint(1, height - 2)

        num_mutations = random.randint(5, 10)

        for i in range(num_mutations):

            # completely random mutation - 10%
            if random.random() < 0.1 and len(genome) > 0:
                # print("random mutation")

                choice = random.random()
                if genome[to_change_row][to_change_col] != "T" or genome[to_change_row][to_change_col] != "|":
                    if choice < 0.15:
                        genome[to_change_row][to_change_col] = "?"
                    elif choice < 0.4:
                        genome[to_change_row][to_change_col] = "o"
                    elif choice < 0.55:
                        genome[to_change_row][to_change_col] = "E"
                    else:
                        genome[to_change_row][to_change_col] = "-"

            # "positive" mutation - 30%
            elif random.random() < 0.4 and len(genome) > 0:
                # print("positive mutation")
                # an unhittable question mark
                if to_change_row > height - 3 and genome[to_change_row][to_change_col] == "?":
                    genome[to_change_row][to_change_col] = "X"
                #lonely block boy
                elif genome[to_change_row][to_change_col] == "X" or genome[to_change_row][to_change_col] == "B" or genome[to_change_row][to_change_col] == "?":
                    if genome[to_change_row][to_change_col + 1] == "-" and genome[to_change_row][to_change_col - 1] == "-":
                        if genome[to_change_row][to_change_col] == "X":
                            genome[to_change_row][to_change_col + 1] = genome[to_change_row][to_change_col]
                        if genome[to_change_row][to_change_col] == "B":
                            genome[to_change_row][to_change_col + 1] = genome[to_change_row][to_change_col]
                        if genome[to_change_row][to_change_col] == "?":
                            genome[to_change_row][to_change_col + 1] = "X"
                         # genome[to_change_row][to_change_col - 1] = genome[to_change_row][to_change_col]
        return genome


    # Create zero or more children from self and other
    def generate_children(self, other):
        # print("generate_children entered")

        # Leaving first and last columns alone...
        # do crossover with other

        new_genome = copy.deepcopy(self.genome)
        other_genome = copy.deepcopy(other.genome)

        left = 1
        right = width - 2

        single_point = random.randint(left, right)

        for y in range(height):
            for x in range(left, right):
                # STUDENT Which one should you take?  Self, or other?  Why?
                # STUDENT consider putting more constraints on this to prevent pipes in the air, etc

                if x >= single_point:
                    new_genome[y][x] = other.genome[y][x]
                    other_genome[y][x] = self.genome[y][x]

        # do mutation; note we're returning a one-element tuple here
        return (Individual_Grid(self.mutate(new_genome)), Individual_Grid(self.mutate(other_genome)))

    # Turn the genome into a level string (easy for this genome)
    def to_level(self):
        return self.genome

    # These both start with every floor tile filled with Xs
    # STUDENT Feel free to change these
    @classmethod
    def empty_individual(cls):
        g = [["-" for col in range(width)] for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        for col in range(8, 14):
            g[col][-1] = "f"
        for col in range(14, 16):
            g[col][-1] = "X"
        return cls(g)

    @classmethod
    def random_individual(cls):
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        # STUDENT also consider weighting the different tile types so it's not uniformly random

        # distribution = [space = 0.53, wall = 0.07, \
        # question mark = 0.07, mushroom block = 0.05, \
        # breakable block = 0.08, coin = 0.07, \
        # pipe top = 0.05, enemy = 0.08]

        # print("random_individuals entered")

        empty = ["-", "-"]
        g = [random.choices(empty, k=width) for row in range(height)]

        for row in range(1, height):
            for column in range(2, width-4):
                choice = random.random()

                # leave first and last columns empty
                # if column == 0 or column == width-1:
                #     g[row][column] == "-"

                if column != 0 or column != width - 1:
                    if g[row][column - 1] != "T" and row-1 > 0 and g[row-1][column - 1] != "T" and row+1 < height and g[row+1][column - 1] != "T":
                        #empty space
                        if choice < 0.66:
                            g[row][column] = "-"

                        #unbreakable wall
                        elif choice < .70 and row <= height - 2:
                            g[row][column] = "X"

                        # question mark
                        elif choice < .72 and row <= height - 4 and row > 3:
                            g[row][column] = "?"
                            if row - 1 > 0:
                                g[row - 1][column] = "-"

                        # mushroom block
                        elif choice < .73 and row <= height - 3 and row > 3:
                            g[row][column] = "M"
                            if row - 1 > 0:
                                g[row - 1][column] = "-"
                            if row + 1 < height:
                                g[row + 1][column] = "-"

                        # breakable block
                        elif choice < .84 and row <= height - 3 and row > 2:
                            # thing above breakable block is not a ? or M
                            if row - 1 > 0 and g[row - 1][column] != "?" and g[row - 1][column] != "M":
                                g[row][column] = "B"
                            else:
                                g[row][column] = "-"
                            if column - 1 > 0:
                                g[row][column - 1] = "B"

                        # coins
                        elif choice < .85 and row > 3:
                            g[row][column] = "o"
                            # if row - 1 > 0 and column - 1 > 0:
                            #     g[row - 1][column - 1] = "o"

                        # pipe tops
                        elif choice < .89 and row > 3 * height / 5 and column < width - 3 and column > 3:
                            g[row][column] = "T"
                            if row > 0 and column - 2 > 0 and column + 2 < width:
                                g[row][column - 1] = "-"
                                g[row][column - 2] = "-"
                                g[row][column + 2] = "-"
                                g[row][column + 1] = "-"

                            for r in range(row-5, row):
                                if row-5 > 0:
                                    g[r][column] = "-"

                        # empty space
                        else:
                            g[row][column] = "-"

        # overwrite

        # leave random rows empty
        g[12][:] = ["-"] * width
        g[5][:] = ["-"] * width
        # g[6][:] = ["-"] * width
        g[9][:] = ["-"] * width
        # g[13][:] = ["-"] * width

        # = "|"  # pipe
        g[15][:] = ["X"] * width

        # pit - add random choice
        random_num_pits = random.randint(10, 25)
        for pit in range(random_num_pits):
            random_pit = random.randint(5, 195)
            random_pit_length = random.randint(0, 3)
            for length in range(random_pit_length):
                g[15][random_pit-length] = "-"


        for row in range(height):
            for column in range(width):

                # for each block, random chance of generating enemy
                if g[row][column] == "X" or g[row][column] == "B":
                    enemy_chance = random.random()
                    if enemy_chance < 0.13 and row - 1 > 0 and column > 5 and column < width - 2:
                        g[row - 1][column] = "E"

                # for each pipe top T, generate segments underneath
                if g[row][column] == "T":
                    # g[row:height][column] = ["|"] * (height - row)
                    if row + 1 < height:
                        # overwrite all spaces under pipe top as pipe segment
                        for row_num in range(row+1, height):
                            g[row_num][column] = "|"

        g[14][0] = "m"
        # [row][column]

        # flag
        # g[7][-1] = "v"
        # flagpole
        # g[8:14][-1] = ["f"] * 6

        # flag
        g[7][-3] = "v"
        # flagpole
        for i in range(8, 15):
            g[i][-3] = "f"

        g[14:16][-1] = ["X", "X"]
        return cls(g)

# 1. enemies not spawning 2. left and right not empty 3. coins all neaer bottom
# question mark on top of X and B

def offset_by_upto(val, variance, min=None, max=None):
    val += random.normalvariate(0, variance**0.5)
    if min is not None and val < min:
        val = min
    if max is not None and val > max:
        val = max
    return int(val)


def clip(lo, val, hi):
    if val < lo:
        return lo
    if val > hi:
        return hi
    return val

# Inspired by https://www.researchgate.net/profile/Philippe_Pasquier/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000.pdf


class Individual_DE(object):
    # Calculating the level isn't cheap either so we cache it too.
    __slots__ = ["genome", "_fitness", "_level"]

    # Genome is a heapq of design elements sorted by X, then type, then other parameters
    def __init__(self, genome):
        self.genome = list(genome)
        heapq.heapify(self.genome)
        self._fitness = None
        self._level = None

    # Calculate and cache fitness
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Add more metrics?
        # STUDENT Improve this with any code you like
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.4,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=2.0,
            meaningfulJumps=0.15,
        )

        # add penalties for unaesthetic things
        penalties = 0

        # too many stairs
        if len(list(filter(lambda de: de[1] == "6_stairs", self.genome))) > 10:
            penalties -= 2

        # if not solvable
        # if measurements[solvability] == 0:
        #     penalties -= 10

        # STUDENT If you go for the FI-2POP extra credit, you can put constraint calculation in here too and cache it in a new entry in __slots__.
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients)) + penalties

        #print(self._fitness)
        return self

    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    def mutate(self, new_genome):
        # STUDENT How does this work?  Explain it in your writeup.
        # STUDENT consider putting more constraints on this, to prevent generating weird things
        if random.random() < 0.2 and len(new_genome) > 0:
            to_change = random.randint(0, len(new_genome) - 5)
            de = new_genome[to_change]
            new_de = de
            x = de[0]
            de_type = de[1]
            choice = random.random()
            if de_type == "4_block":
                y = de[2]
                breakable = de[3]
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    breakable = not de[3]
                new_de = (x, de_type, y, breakable)
            elif de_type == "5_qblock":
                y = de[2]
                has_powerup = de[3]  # boolean
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    has_powerup = not de[3]
                new_de = (x, de_type, y, has_powerup)
            elif de_type == "3_coin":
                y = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                new_de = (x, de_type, y)
            elif de_type == "7_pipe":
                h = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    h = offset_by_upto(h, 2, min=2, max=height - 8)
                new_de = (x, de_type, h)
            elif de_type == "0_hole":
                w = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    w = offset_by_upto(w, 4, min=1, max=width - 2)
                new_de = (x, de_type, w)
            elif de_type == "6_stairs":
                h = de[2]
                dx = de[3]  # -1 or 1
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    h = offset_by_upto(h, 8, min=1, max=height - 6)
                else:
                    dx = -dx
                new_de = (x, de_type, h, dx)
            elif de_type == "1_platform":
                w = de[2]
                y = de[3]
                madeof = de[4]  # from "?", "X", "B"
                if choice < 0.25:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.5:
                    w = offset_by_upto(w, 8, min=1, max=width - 2)
                elif choice < 0.75:
                    y = offset_by_upto(y, height, min=0, max=height - 1)
                else:
                    madeof = random.choice(["?", "X", "B"])
                new_de = (x, de_type, w, y, madeof)
            elif de_type == "2_enemy":
                pass
            new_genome.pop(to_change)
            heapq.heappush(new_genome, new_de)
        return new_genome

    def generate_children(self, other):
        # STUDENT How does this work?  Explain it in your writeup.
        pa = random.randint(0, len(self.genome) - 1)
        pb = random.randint(0, len(other.genome) - 1)
        a_part = self.genome[:pa] if len(self.genome) > 0 else []
        b_part = other.genome[pb:] if len(other.genome) > 0 else []
        ga = a_part + b_part
        b_part = other.genome[:pb] if len(other.genome) > 0 else []
        a_part = self.genome[pa:] if len(self.genome) > 0 else []
        gb = b_part + a_part
        # do mutation
        return Individual_DE(self.mutate(ga)), Individual_DE(self.mutate(gb))

    # Apply the DEs to a base level.
    def to_level(self):
        if self._level is None:
            base = Individual_Grid.empty_individual().to_level()
            for de in sorted(self.genome, key=lambda de: (de[1], de[0], de)):
                # de: x, type, ...
                x = de[0]
                de_type = de[1]
                if de_type == "4_block":
                    y = de[2]
                    breakable = de[3]
                    base[y][x] = "B" if breakable else "X"
                elif de_type == "5_qblock":
                    y = de[2]
                    has_powerup = de[3]  # boolean
                    base[y][x] = "M" if has_powerup else "?"
                elif de_type == "3_coin":
                    y = de[2]
                    base[y][x] = "o"
                elif de_type == "7_pipe":
                    h = de[2]
                    base[height - h - 1][x] = "T"
                    for y in range(height - h, height):
                        base[y][x] = "|"
                elif de_type == "0_hole":
                    w = de[2]
                    for x2 in range(w):
                        base[height - 1][clip(1, x + x2, width - 2)] = "-"
                elif de_type == "6_stairs":
                    h = de[2]
                    dx = de[3]  # -1 or 1
                    for x2 in range(1, h + 1):
                        for y in range(x2 if dx == 1 else h - x2):
                            base[clip(0, height - y - 1, height - 1)][clip(1, x + x2, width - 2)] = "X"
                elif de_type == "1_platform":
                    w = de[2]
                    h = de[3]
                    madeof = de[4]  # from "?", "X", "B"
                    for x2 in range(w):
                        base[clip(0, height - h - 1, height - 1)][clip(1, x + x2, width - 2)] = madeof
                elif de_type == "2_enemy":
                    base[height - 2][x] = "E"
            self._level = base
        return self._level

    @classmethod
    def empty_individual(_cls):
        # STUDENT Maybe enhance this
        g = []
        return Individual_DE(g)

    @classmethod
    def random_individual(_cls):
        # STUDENT Maybe enhance this
        elt_count = random.randint(300, 500)
        g = [random.choice([
            (random.randint(1, width - 2), "0_hole", random.randint(1, 8)),
            (random.randint(1, width - 2), "1_platform", random.randint(1, 8), random.randint(0, height - 1), random.choice(["?", "X", "B"])),
            (random.randint(1, width - 2), "2_enemy"),
            (random.randint(1, width - 2), "3_coin", random.randint(0, height - 1)),
            (random.randint(1, width - 2), "4_block", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "5_qblock", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "6_stairs", random.randint(1, height - 4), random.choice([-1, 1])),
            (random.randint(1, width - 2), "7_pipe", random.randint(2, height - 8))
        ]) for i in range(elt_count)]
        return Individual_DE(g)


Individual = Individual_Grid
# Individual = Individual_DE


def generate_successors(population):
    results = []
    # STUDENT Design and implement this
    # Hint: Call generate_children() on some individuals and fill up results.

    selection1 = tournament_selection(population)

    for child in range(0, len(selection1) - 1, 2):
        parent1 = selection1[child]
        parent2 = selection1[child + 1]
        results.append(parent1.generate_children(parent2)[0])
        results.append(parent2.generate_children(parent1)[0])

    selection2 = elitism_selection(population)

    for child in range(0, len(selection2) - 1):
        results.append(selection2[child])

    return results

def tournament_selection(population):
    children = []
    random.shuffle(population)
    for i in range(0, len(population)-1, 2):
        player1 = population[i]
        player2 = population[i+1]
        if player1._fitness > player2._fitness:
            children.append(player1)
        else:
            children.append(player2)
    return children

def elitism_selection(population):
    children = []
    # descending
    sort = sorted(population, key=lambda p: p._fitness, reverse=True)

    #choose the 10 highest fitness children
    for i in range(int(len(population)/2)):
        children.append(sort[i])

    return children


def ga():
    # STUDENT Feel free to play with this parameter
    pop_limit = 50
    # Code to parallelize some computations
    batches = os.cpu_count()
    if pop_limit % batches != 0:
        print("It's ideal if pop_limit divides evenly into " + str(batches) + " batches.")
    batch_size = int(math.ceil(pop_limit / batches))
    with mpool.Pool(processes=os.cpu_count()) as pool:
        init_time = time.time()
        # STUDENT (Optional) change population initialization
        population = [Individual.random_individual() if random.random() < 1
                      else Individual.empty_individual()
                      for _g in range(pop_limit)]
        # But leave this line alone; we have to reassign to population because we get a new population that has more cached stuff in it.
        population = pool.map(Individual.calculate_fitness,
                              population,
                              batch_size)

        init_done = time.time()
        print("Created and calculated initial population statistics in:", init_done - init_time, "seconds")
        generation = 0
        start = time.time()
        now = start
        print("Use ctrl-c to terminate this loop manually.")
        try:
            while True:
                now = time.time()
                # Print out statistics
                if generation > 0:
                    best = max(population, key=Individual.fitness)
                    print("Generation:", str(generation))
                    print("Max fitness:", str(best.fitness()))
                    print("Average generation time:", (now - start) / generation)
                    print("Net time:", now - start)
                    with open("levels/last.txt", 'w') as f:
                        for row in best.to_level():
                            f.write("".join(row) + "\n")
                generation += 1
                # STUDENT Determine stopping condition
                stop_condition = False
                if stop_condition:
                    break
                # STUDENT Also consider using FI-2POP as in the Sorenson & Pasquier paper
                gentime = time.time()
                next_population = generate_successors(population)
                gendone = time.time()
                print("Generated successors in:", gendone - gentime, "seconds")
                # Calculate fitness in batches in parallel
                next_population = pool.map(Individual.calculate_fitness,
                                           next_population,
                                           batch_size)
                popdone = time.time()
                print("Calculated fitnesses in:", popdone - gendone, "seconds")
                population = next_population
        except KeyboardInterrupt:
            pass
    return population


if __name__ == "__main__":
    final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
    best = final_gen[0]
    print("Best fitness: " + str(best.fitness()))
    now = time.strftime("%m_%d_%H_%M_%S")
    # STUDENT You can change this if you want to blast out the whole generation, or ten random samples, or...
    for k in range(0, 10):
        with open("levels/" + now + "_" + str(k) + ".txt", 'w') as f:
            for row in final_gen[k].to_level():
                f.write("".join(row) + "\n")
