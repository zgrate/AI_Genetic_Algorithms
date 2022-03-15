import json


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

    def __getitem__(self, key):
        return self.machines[key]

    def __str__(self):
        return "Machines:\n" + "\n".join([str(x) for x in self.machines])


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
