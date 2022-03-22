import json
import os
import statistics
from typing import Union, Optional

from storage_data import Chromosome


class LoadedData:
    def __init__(self, method: str, total_generations: int, chromosomes: int,
                 mutation_rate: float, mutation_number: int, results: list[tuple[int, Optional[Chromosome]]]):
        self.mutation_number = mutation_number
        self.mutation_rate = mutation_rate
        self.chromosomes = chromosomes
        self.total_generations = total_generations
        self.method = method
        self.results = results

    def __str__(self):
        return str(self.__dict__)

    def average_results(self, average_number: int):
        new_results = []
        for i in range(int(len(self.results) / average_number)):
            sum = 0
            for j in range(average_number):
                sum += self.results[i * 10 + j]
            new_results.append(sum / 10)
        self.results = new_results

    def get_values(self):
        return list(map(lambda d: d[0], self.results))

    def get_score_sorted(self):
        l = self.get_values()
        l.sort()
        return l


def load_file(output_file: str, folder: str = "results") -> LoadedData:
    splitted = output_file.split("_")
    results = []
    with open(os.path.join(folder, output_file), "r", encoding="utf-8") as file:
        for e in file.readlines():
            if e.strip() != "":
                split = e.split(";")
                if len(split) == 2:
                    results.append((int(split[1]), None))
                else:
                    val = int(split[1])
                    c = Chromosome()
                    c.__dict__.update(json.loads(split[2]))
                    results.append((val, c))
    return LoadedData(splitted[3], len(results), int(splitted[6]), float(splitted[7]), int(splitted[8].split(".")[0]),
                      results)


import matplotlib.pyplot as plt


def draw_machines(chromosome: Chromosome):
    import matplotlib.pyplot as plt

    y = []
    x = []
    labels = []
    for m in chromosome.machines:
        x.append(m["posX"])
        y.append(m["posY"])
        labels.append(f"Machine ID {m['machineId']}")

    fig, ax = plt.subplots()
    ax.scatter(x, y)

    for i, m in enumerate(chromosome.machines):
        print(m)
        ax.annotate(f"Machine ID {m['machineId']}", (x[i], y[i]))
    print(m)
    plt.show()


def load_plot(loaded: Union[str, LoadedData]):
    if isinstance(loaded, str):
        loaded = load_file(loaded)
    plt.title(
        f"Generations:{loaded.total_generations} {loaded.method}Chromo: {loaded.chromosomes}\nMutation:{loaded.mutation_rate} x {loaded.mutation_number} BEST SCORE: {min(loaded.get_values())}")
    plt.plot(loaded.get_values())
    plt.show()
    draw_machines(loaded.results[-1][1])


def data_against_score(folder):
    with open(os.path.join(folder, "score_data_analysis.txt"), "w", encoding="utf-8") as output:
        output.write(
            "id;chromosome;mutation_rate;mutation_number;total_generations;last_score;min_score;variance;median;mean\n")
        i = 0
        for item in os.listdir(folder):
            if item.startswith("output"):
                i += 1
                loaded = (load_file(item, "results\\tournament"))
                vals = loaded.get_values()
                variance = statistics.variance(vals)
                median = statistics.median(vals)
                mean = statistics.mean(vals)
                output.write(
                    f"{i};{loaded.chromosomes};{loaded.mutation_rate};{loaded.mutation_number};{loaded.total_generations};{loaded.get_values()[-1]};{loaded.get_score_sorted()[0]};{variance};{median};{mean}\n")
        output.flush()


if __name__ == "__main__":
    # load_plot("output_2022-03-20_14-26-06_tournament_3_3_50_0.3_2_100.txt")
    # exit(0)
    # data_against_score("results\\tournament")
    # exit(0)
    minimum = []
    minimum_loaded = []
    i = 0
    accept = [1722,
              1283,
              1958,
              810,
              ]
    for item in os.listdir("results\\tournament"):
        if item.startswith("output"):
            i += 1
            print(item)
            loaded = (load_file(item, "results\\tournament"))
            if i in accept:
                minimum_loaded.append(loaded)

        #
        # if len(loaded.results) > 10 and (
        #         sum(loaded.results) / len(loaded.results)) < 10000 and loaded.chromosomes == 100:
        #     # loaded.average_results(10)
        #     load_plot(loaded)
    print(minimum_loaded)
    for e in minimum_loaded:
        load_plot(e)
    # print(loaded)
