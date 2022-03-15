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
        x = random.randint(0, solution.board_size_x)
        y = random.randint(0, solution.board_size_y)
        while check_if_position(x, y):
            x = random.randint(0, solution.board_size_x)
            y = random.randint(0, solution.board_size_y)
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
    return solution


def selection_tournament(solution: FLOSolution, sample_size: Union[int, float] = 5, number_of_results: int = 2) -> list[
    Chromosome]:
    if sample_size < 1.0:
        sample_size = len(solution.chromosomes) * sample_size
    all_chromosomes = []
    for i in range(number_of_results):
        chromo = None
        while chromo is None or chromo in all_chromosomes:
            selected_chromosomes = random.sample(solution.chromosomes, sample_size)
            selected_chromosomes.sort(key=lambda d: solution.calculate_sum_cost(d))
            chromo = selected_chromosomes[0]
        all_chromosomes.append(chromo)
    return all_chromosomes


def roulette(soultion: FLOSolution, number_of_results: int = 2):
    all_chromosomes = []
    solution.sort_chromosomes_by_score()
    max = solution.calculate_sum_cost(solution.chromosomes[-1])

    def scale(val):
        """
        Scale the given value from the scale of src to the scale of 0-1.
        """
        return 1 - ((val) / (max))

    weights = list(map(lambda d: scale(solution.calculate_sum_cost(d)), solution.chromosomes))

    for i in range(number_of_results):
        chromo = None
        while chromo is None or chromo in all_chromosomes:
            chromo = random.choices(solution.chromosomes, weights=weights, k=1)[0]
        all_chromosomes.append(chromo)
    return all_chromosomes


def cross(solution: FLOSolution, parent1: Chromosome, parent2: Chromosome,
          number_of_cuts_per_chromosome: int = 2) -> FLOSolution:
    next_generation = solution.next_generation()
    next_generation.connections = solution.connections

    for _ in range(solution.number_of_chromosomes):
        target_length = len(parent1.machines)
        last_cut_pos = random.randrange(target_length)
        list_of_machines: list = parent1.machines[0:last_cut_pos]
        parent2_insert = True
        for i in range(number_of_cuts_per_chromosome):
            remaining_length = target_length - len(list_of_machines)
            if remaining_length <= 0:
                break
            cut_point = random.randrange(remaining_length)
            if parent2_insert:
                list_of_machines = list_of_machines + parent2.machines[last_cut_pos: last_cut_pos + cut_point]
            else:
                list_of_machines = list_of_machines + parent1.machines[last_cut_pos: last_cut_pos + cut_point]
            last_cut_pos = cut_point
            parent2_insert = not parent2_insert

        remaining_length = target_length - len(list_of_machines)
        if parent2_insert:
            list_of_machines = list_of_machines + parent2.machines[last_cut_pos: last_cut_pos + remaining_length]
        else:
            list_of_machines = list_of_machines + parent1.machines[last_cut_pos: last_cut_pos + remaining_length]

        assert len(list_of_machines) == target_length and len(list_of_machines) == len(parent1.machines)
        next_generation.chromosomes.append(Chromosome(list_of_machines))
    return next_generation


def mutation(solution: FLOSolution, mutation_chance: float = 0.1, number_of_mutations: int = 5):
    for e in solution.chromosomes:
        if random.random() < mutation_chance:
            print("We got mutation!")
            for i in range(number_of_mutations):
                random_machine: FLOMachine = random.choice(e.machines)
                random_machine.posX = random.randrange(solution.board_size_x)
                random_machine.posY = random.randrange(solution.board_size_y)


if __name__ == '__main__':
    solution = generate_random_solution("dane\\easy_flow.json", "dane\\easy_cost.json", 3, 3)

    a = roulette(solution)
    for e in a:
        print(solution.calculate_sum_cost(e))

    b = cross(solution, a[0], a[1])
    print(b)
    mutation(b)
    print(b)
