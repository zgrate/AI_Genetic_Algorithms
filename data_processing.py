import json
import os
import statistics
from datetime import datetime
from typing import Union, Optional

from sqlalchemy import Column, Integer, Float, Date, Unicode, ForeignKey, TEXT
from sqlalchemy.orm import declarative_base

from storage_data import Chromosome

Base = declarative_base()
metadata = Base.metadata


class TrainingInfo(Base):
    __tablename__ = 'TrainingInfo'

    id = Column(Integer, primary_key=True, autoincrement=False)
    method = Column(Unicode(30), nullable=False)
    total_generations = Column(Integer, nullable=False)
    mutation_rate = Column(Float(53), nullable=False)
    mutation_number = Column(Integer, nullable=False)
    cross_chance = Column(Float(53), nullable=False)
    date = Column(Date)
    chromosomes = Column(Integer, nullable=False)
    tournament_size = Column(Float(53), nullable=False)


class ResultsTable(TrainingInfo):
    __tablename__ = 'ResultsTable'

    IdR = Column(ForeignKey('TrainingInfo.id'), primary_key=True)
    generation = Column(Integer, nullable=False)
    best_score = Column(Integer, nullable=False)
    best_machines = Column(TEXT(2147483647, 'Polish_CI_AS'))
    IdT = Column(Integer, nullable=False)


from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def push_all_gens_data():
    engine = create_engine("mssql+pyodbc://root:root@localhost:1433/AI_GENETIC?driver=ODBC+Driver+17+for+SQL+Server")
    with Session(engine) as session:
        with open("all_gens.txt", "r", encoding="utf-8") as input_file:
            # f"{id};t;{max_generations};{chromosomes};{mutations / 1000};{mutation_count};{cross_chance};{tournament_size / 10};\n")
            l = []
            for e in input_file:
                split = e.split(";")
                info = TrainingInfo()
                info.id = int(split[0])
                info.method = split[1]
                info.total_generations = int(split[2])
                info.chromosomes = int(split[3])
                info.mutation_rate = float(split[4])
                info.mutation_number = int(split[5])
                info.cross_chance = int(split[6]) / 10
                if info.method == "t":
                    info.tournament_size = float(split[7])
                else:
                    info.tournament_size = 0
                l.append(info)
            session.bulk_save_objects(l)
            session.commit()


class LoadedData:
    def __init__(self, method: str, total_generations: int, chromosomes: int,
                 mutation_rate: float, mutation_number: int, real_generations: int, cross_chance: float,
                 tournament_sample_size: float, results: list[tuple[int, Optional[Chromosome]]]):
        self.mutation_number = mutation_number
        self.mutation_rate = mutation_rate
        self.chromosomes = chromosomes
        self.total_generations = total_generations
        self.real_generations = real_generations
        self.method = method
        self.results = results
        self.cross_chance = cross_chance
        self.tournament_sample_size = tournament_sample_size
        self.date = datetime

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
    splitted = output_file[:-4].split("_")

    results = []
    # f"output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_roulette_{x_board_size}_{y_board_size}_{number_of_chromosomes}_{mutation_chance}_{number_of_mutations}_{cross_chance}.txt"),

    # f"output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tournament_{x_board_size}_{y_board_size}_{number_of_chromosomes}_{mutation_chance}_{number_of_mutations}_{max_generations}_{cross_chance}_{sample_size}.txt"),
    date = datetime.strptime(splitted[1] + "-" + splitted[2], '%Y-%m-%d-%H-%M-%S')
    method = "t" if splitted[3] == "tournament" else "r"
    sample_size = 0 if method != "t" else float(splitted[11])
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

    if method == "t":
        return LoadedData(method, int(splitted[9]), int(splitted[6]), float(splitted[7]), int(splitted[8]),
                          len(results), float(splitted[10]), sample_size, results)
    else:
        return LoadedData(method, 0, int(splitted[6]), float(splitted[7]), int(splitted[8]), len(results),
                          float(splitted[9]), 0, results)


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
        # f"output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tournament_{x_board_size}_{y_board_size}_{number_of_chromosomes}_{mutation_chance}_{number_of_mutations}_{max_generations}_{cross_chance}_{sample_size}.txt"),

        output.write(
            "id;method;chromosome;mutation_rate;mutation_number;total_generations;real_generations;cross_chance;sample_size;last_score;min_score;variance;median;mean\n")
        i = 0
        for item in os.listdir(folder):
            print(item)
            if item.startswith("output"):
                i += 1
                loaded = (load_file(item, "hard\\automat"))
                if len(loaded.results) >= 10:
                    vals = loaded.get_values()
                    variance = statistics.variance(vals)
                    median = statistics.median(vals)
                    mean = statistics.mean(vals)

                    output.write(
                        f"{i};{loaded.method};{loaded.chromosomes};{loaded.mutation_rate};{loaded.mutation_number};{loaded.total_generations};{loaded.real_generations};{loaded.cross_chance};{loaded.tournament_sample_size};{loaded.get_values()[-1]};{loaded.get_score_sorted()[0]};{variance};{median};{mean}\n")
        output.flush()


from sqlalchemy import select


# def check_invalid():
#     with open("all_gens.txt", "r", encoding="utf-8") as input_file:
#         for e in input_file.readlines():
#             split = e.split(";")
#             if os.path.exists(os.path.join("hard\\automat\\finished", f"{split[0]}.finished")):
#                 for f in os.listdir("hard\\automat"):


def get_results_push_db(folder="hard\\automat"):
    engine = create_engine("mssql+pyodbc://root:root@localhost:1433/AI_GENETIC?driver=ODBC+Driver+17+for+SQL+Server")
    with Session(engine) as session:
        for e in os.listdir(folder):
            if e.startswith("output"):
                a = load_file(e, folder)
                select(TrainingInfo).where(TrainingInfo.method)


# get_results_push_db()
# exit(0)

if __name__ == "__main__":
    # load_plot("output_2022-03-20_14-26-06_tournament_3_3_50_0.3_2_100.txt")
    # exit(0)
    data_against_score("hard\\automat")
    exit(0)
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
