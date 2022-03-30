import random
from typing import Union

from storage_data import Chromosome, FLOSolution, FLOMachine


def generate_random_positions(solution: FLOSolution, chromosome: Chromosome):
    def check_if_position(x: int, y: int):
        for L in chromosome.machines:
            if L.posX == x and L.posY == y:
                return True
        return False

    for e in chromosome.machines:
        x = random.randrange(solution.board_size_x)
        y = random.randrange(solution.board_size_y)
        while check_if_position(x, y):
            x = random.randrange(solution.board_size_x)
            y = random.randrange(solution.board_size_y)
        e.posX = x
        e.posY = y


def generate_random_solution(paths_flow_file_name: str, paths_cost_file_name: str, board_size_x: int, board_size_y: int,
                             number_of_chromosomes: int = 10) -> FLOSolution:
    solution = FLOSolution(paths_flow_file_name, paths_cost_file_name, board_size_x, board_size_y,
                           number_of_chromosomes, 1)
    max_id = solution.max_id()
    for _ in range(number_of_chromosomes):
        chromo = Chromosome([])
        chromo.generate_machines(max_id)
        generate_random_positions(solution, chromosome=chromo)
        solution.chromosomes.append(chromo)

    # print(solution)
    # for c in solution.chromosomes:
    #     print(c)
    return solution


old = {}


def selection_tournament(solution: FLOSolution, sample_size: Union[int, float] = 5, number_of_results: int = 2) -> list[
    Chromosome]:

    if sample_size < 1.0:
        sample_size = int(len(solution.chromosomes) * sample_size)
    if sample_size == 0:
        return solution.chromosomes
    all_chromosomes = []

    def inside(check):
        for e in all_chromosomes:
            if e == check:
                return True
        return False

    for i in range(number_of_results):
        chromo = None
        selected_chromosomes = random.sample(solution.chromosomes, k=sample_size)
        selected_chromosomes.sort(key=lambda d: solution.calculate_sum_cost(d))
        while chromo is None or inside(chromo):
            chromo = selected_chromosomes.pop(0)

        all_chromosomes.append(chromo)

    assert len(all_chromosomes) == number_of_results
    return all_chromosomes


def roulette(solution: FLOSolution, number_of_results: int = 2):
    all_chromosomes = []
    solution.sort_chromosomes_by_score()
    # min = solution.calculate_sum_cost(solution.chromosomes[0])
    # temp_list = list(map(lambda d: solution.calculate_sum_cost(d), solution.chromosomes))

    # for e in solution.chromosomes:
    #     print(solution.calculate_sum_cost(e))
    l = list(map(lambda d: solution.calculate_sum_cost(d), solution.chromosomes))
    suma = sum(l)
    inverse_prob = list(map(lambda d: 1 / (d / suma), l))
    sum_inverse_prob = sum(inverse_prob)

    def scale(val):
        """
        Scale the given value from the scale of src to the scale of 0-1.
        """
        return (suma / val) ** 3

    weights = list(map(lambda d: scale(solution.calculate_sum_cost(d)), solution.chromosomes))
    #  mi = min(weights)
    #  weights = list(map(lambda d: (d), weights))
    #   a = ""
    #   for i in range(len(weights)):
    #       a += f"{l[i]} - {weights[i]}, "
    # print(a)
    # print(weights)
    for i in range(number_of_results):
        chromo = None
        while chromo is None or chromo in all_chromosomes:
            return random.choices(solution.chromosomes, weights=weights, k=2)
        all_chromosomes.append(chromo)
    assert len(all_chromosomes) == number_of_results
    return all_chromosomes


def anydup(thelist):
    seen = set()
    for x in thelist:
        if x in seen: return True
        seen.add(x)
    return False


# prawdopodbienstwo krzyzowania
def cross(solution: FLOSolution, parents_sample: list[Chromosome], cross_chance: float = 0.1,
          number_of_cuts_per_chromosome: int = 1) -> FLOSolution:
    next_generation = solution.next_generation()
    next_generation.connections = solution.connections
    total_rotations = 0
    # next_generation.chromosomes.append(parent1)
    # next_generation.chromosomes.append(parent2)

    if random.random() > cross_chance:
        for e in parents_sample:
            next_generation.chromosomes.append(Chromosome(list(map(lambda d: d.copy(), e.machines))))
        return next_generation

    def fix_machines(list_machines: list[FLOMachine]):
        source = random.choice(parents_sample)
        machines_id_list = list(map(lambda d: d.machineId, list_machines))
        machines_id_set = set(machines_id_list)
        machines_indexes = list(map(lambda d: machines_id_list.index(d), machines_id_set))
        list_mac = []
        for i in machines_indexes:
            list_mac.append(list_machines[i])
        machines_id_list = list(map(lambda d: d.machineId, list_mac))
        sources_id = list(map(lambda d: d.machineId, source.machines))
        for i in range(solution.max_id() + 1):
            if machines_id_list.count(i) == 0:
                list_mac.append(source.machines[sources_id.index(i)])

        assert len(list_mac) == len(parents_sample[0].machines)
        assert len(list_mac) == solution.max_id() + 1
        l = list(map(lambda d: d.machineId, list_mac))
        assert len(set(l)) == len(l)

        return list_mac

    # print(list(map(lambda d: d.machineId, parent1.machines)))
    # print(list(map(lambda d: d.machineId, parent2.machines)))

    for _ in range(solution.number_of_chromosomes):
        list_of_machines = []
        for i in range(solution.max_id() + 1):
            list_of_machines.append(random.choice(parents_sample)[i])

        # parent1 = random.choice(parents_sample)
        # parent2 = random.choice(parents_sample)
        # random.shuffle(parent1.machines)
        # random.shuffle(parent2.machines)
        target_length = len(parents_sample[0].machines)
        # last_cut_pos = random.randrange(target_length)
        # list_of_machines: list = parent1.machines[0:last_cut_pos] + parent2.machines[last_cut_pos:]

        # parent2_insert = True
        # for i in range(number_of_cuts_per_chromosome):
        #     remaining_length = target_length - len(list_of_machines)
        #     if remaining_length <= 0:
        #         break
        #     cut_point = random.randrange(remaining_length)
        #     if parent2_insert:
        #         list_of_machines = list_of_machines + parent2.machines[last_cut_pos:]
        #     else:
        #         list_of_machines = list_of_machines + parent1.machines[last_cut_pos:]
        #     last_cut_pos += cut_point
        #     parent2_insert = not parent2_insert

        # remaining_length = target_length - len(list_of_machines)
        # # if parent2_insert:
        # #     list_of_machines = list_of_machines + parent2.machines[last_cut_pos: last_cut_pos + remaining_length]
        # # else:
        # #     list_of_machines = list_of_machines + parent1.machines[last_cut_pos: last_cut_pos + remaining_length]

        assert len(list_of_machines) == target_length and len(list_of_machines) == len(parents_sample[0].machines)
        # assert not anydup(list(map(lambda d: d.machineId, list_of_machines)))
        # print(list(map(lambda d: d.machineId, list_of_machines)))

        list_of_machines_copy = list(map(lambda d: d.copy(), fix_machines(list_of_machines)))
        next_generation.chromosomes.append(Chromosome(list_of_machines_copy))

    return next_generation


def mutation(solution: FLOSolution, mutation_chance: float = 0.1, number_of_mutations: int = 5):
    for e in solution.chromosomes:
        def get_overlaping(pos_x, pos_y):
            for i in range(len(e.machines)):
                machine1 = e.machines[i]
                if machine1.posX == pos_x and machine1.posY == pos_y:
                    return machine1
            return None

        if random.random() < mutation_chance:
            # print("We got mutation!")
            for i in range(number_of_mutations):
                random_machine: FLOMachine = random.choice(e.machines)
                new_pos_x = random.randrange(solution.board_size_x)
                new_pos_y = random.randrange(solution.board_size_y)
                overlap = get_overlaping(new_pos_x, new_pos_y)
                if overlap is None:
                    random_machine.posX = new_pos_x
                    random_machine.posY = new_pos_y
                else:  # swap
                    overlap.posX = random_machine.posX
                    overlap.posY = random_machine.posY
                    random_machine.posX = new_pos_x
                    random_machine.posY = new_pos_y

                # movement = random.choice(e.machines)
                # movement.posX += random.randrange(3)
                # if movement.posX > solution.board_size_x:
                #     movement.posX -= solution.board_size_x
                # movement.posY += random.randrange(3)
                # if movement.posY > solution.board_size_y:
                #     movement.posY -= solution.board_size_y


if __name__ == '__main__':
    solution2 = generate_random_solution("dane\\easy_flow.json", "dane\\easy_cost.json", 3, 3)

    a = roulette(solution2)
    for e in a:
        print(solution2.calculate_sum_cost(e))

    # b = cross(solution2, a[0], a[1])
    # print(b)
    # mutation(b)
    # print(b)
