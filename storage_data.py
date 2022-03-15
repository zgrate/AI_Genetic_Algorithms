import json
from typing import Optional


class FLOMachine:
    def __init__(self, machineId: int, posX: int, posY: int):
        self.machineId = machineId
        self.posX = posX
        self.posY = posY

    def __str__(self):
        return f"Machine: ${self.machineId} with pos {self.posX}x{self.posY}"


class FLOMachineConnection:
    def __init__(self, source: int, target: int, amount: int, cost: int):
        self.source = source
        self.target = target
        self.amount = amount
        self.cost = cost

    def __str__(self):
        return f"Connection from ${self.source} to ${self.target} amount: ${self.amount} cost: ${self.cost}"

    def calculate_cost(self, source: FLOMachine, target: FLOMachine):
        return self.amount * self.cost * (abs(source.posX - target.posX) + abs(source.posY - target.posY))


class Chromosome:
    def __init__(self, floMachines: list[FLOMachine] = None):
        if floMachines is None:
            floMachines = []
        self.machines = floMachines
        self.machines.sort(key=lambda d: d.machineId)

    def generate_machines(self, max_id):
        for e in range(max_id + 1):
            self.machines.append(FLOMachine(e, 0, 0))
        self.machines.sort(key=lambda d: d.machineId)

    def get_number_of_overlaps(self):
        overlaps = 0
        for i in range(len(self.machines)):
            machine1 = self.machines[i]
            for j in range(len(self.machines) - i):
                machine2 = self.machines[j]
                if machine1.posX == machine2.posX and machine1.posY == machine2.posY:
                    overlaps += 1
        return overlaps

    def __getitem__(self, key):
        return self.machines[key]

    def __str__(self):
        return "Machines:\n" + "\n".join([str(x) for x in self.machines])


class FLOSolution:
    def __init__(self, paths_flow_file_name: Optional[str], paths_cost_file_name: Optional[str], board_size_x: int,
                 board_size_y: int,
                 number_of_chromosomes: int = 10, generation: int = 0, best_score: int = 0):
        self.generation = generation
        self.best_score = best_score
        self.number_of_chromosomes = number_of_chromosomes
        self.chromosomes: list[Chromosome] = []
        if paths_cost_file_name is not None and paths_cost_file_name is not None:
            self.connections = load_machine_connections(paths_flow_file_name, paths_cost_file_name)
        else:
            self.connections = []
        self.board_size_x = board_size_x
        self.board_size_y = board_size_y

    def max_id(self):
        return max([max(x.source, x.target) for x in self.connections])

    def sort_chromosomes_by_score(self):
        self.chromosomes.sort(key=lambda d: self.calculate_sum_cost(d))
        self.best_score = self.calculate_sum_cost(self.chromosomes[0])

    def calculate_sum_cost(self, chromosome: Chromosome, overlap_penelty: int = 1000):
        return sum([x.calculate_cost(chromosome[x.source], chromosome[x.target]) for x in
                    self.connections]) + overlap_penelty * chromosome.get_number_of_overlaps()

    def next_generation(self):
        s = FLOSolution(None, None, self.board_size_x, self.board_size_y, self.number_of_chromosomes,
                        self.generation + 1, 0)
        s.connect = self.connections
        return s

    def __str__(self):
        self.sort_chromosomes_by_score()
        return f"GENERATION {self.generation} FLOSolution of board size {self.board_size_x}x{self.board_size_y} with {self.number_of_chromosomes} chromos\n" \
               f"Best Solution: {self.best_score}"


def load_machine_connections(flow_file_name: str, cost_file_name: str) -> list[FLOMachineConnection]:
    with open(flow_file_name, "r", encoding="utf-8") as flow_file:
        with open(cost_file_name, "r", encoding="utf-8") as cost_file:
            flow_json = json.load(flow_file)
            cost_json = json.load(cost_file)

            def get_cost(source, dest):
                for a in cost_json:
                    if a["source"] == source and a["dest"] == dest:
                        return a["cost"]

            connections = []
            for e in flow_json:
                connections.append(
                    FLOMachineConnection(e["source"], e["dest"], e["amount"], get_cost(e["source"], e["dest"])))
            return connections
