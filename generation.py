import random

from storage_data import Chromosome, load_machine_connections


class FLOSolution:
    def __init__(self, paths_flow_file_name: str, paths_cost_file_name: str, board_size_x: int, board_size_y: int):
        self.chromosomes: list[Chromosome] = []
        self.connections = load_machine_connections(paths_flow_file_name, paths_cost_file_name)
        self.board_size_x = board_size_x
        self.board_size_y = board_size_y

    def max_id(self):
        return max([max(x.source, x.target) for x in self.connections])

    def generate_chromosomes(self, number_of_chromos: int):
        for _ in range(number_of_chromos):
            chromo = Chromosome([])
            chromo.generate_machines(self.max_id())
            self.generate_random_positions(chromosome=chromo)
            print(self.calculate_sum_cost(chromo))
            self.chromosomes.append(chromo)

    def calculate_sum_cost(self, chromosome: Chromosome):
        return sum([x.calculate_cost(chromosome[x.source], chromosome[x.target]) for x in self.connections])

    def generate_random_positions(self, chromosome: Chromosome):
        def check_if_position(x: int, y: int):
            for L in chromosome.machines:
                if L.posX == x and L.posY == y:
                    return True
            return False

        for e in chromosome.machines:
            x = random.randint(0, self.board_size_x)
            y = random.randint(0, self.board_size_y)
            while check_if_position(x, y):
                x = random.randint(0, self.board_size_x)
                y = random.randint(0, self.board_size_y)
            e.posX = x
            e.posY = y


if __name__ == '__main__':
    solution = FLOSolution("dane\\easy_flow.json", "dane\\easy_cost.json", 3, 3)
    solution.generate_chromosomes(10)
