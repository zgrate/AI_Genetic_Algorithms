import os
import pickle
import statistics
from datetime import datetime
from multiprocessing import Pool

from genetic_operations import generate_random_solution, roulette, cross, mutation, selection_tournament
from storage_data import FLOSolution

RESULTS_FOLDER = "results"


def save_data(solution: FLOSolution, file_name: str = "copy.bin"):
    with open(file_name, "wb") as file:
        pickle.dump(solution, file)


def load_data(file_name: str = "copy.bin"):
    with open(file_name, "rb") as file:
        return pickle.load(file)


def start_training_with_roulette(flow_name: str, cost_name: str, x_board_size: int, y_board_size: int,
                                 number_of_chromosomes: int,
                                 number_of_cuts_per_chromosome: int, mutation_chance: float, number_of_mutations: int,
                                 cross_chance: float,
                                 max_generations: int = 0, load_existing_generation: int = False,
                                 folder: str = RESULTS_FOLDER, id=0):
    print(
        f"Training soluion for {x_board_size}x{y_board_size} with {number_of_chromosomes} {mutation_chance} {number_of_mutations}")
    if not load_existing_generation:
        current_solution = generate_random_solution(flow_name, cost_name, x_board_size, y_board_size,
                                                    number_of_chromosomes)
    else:
        current_solution = load_data()
    last_solutions = []

    # print(current_solution.max_id())
    with open(os.path.join(folder,
                           f"output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_roulette_{x_board_size}_{y_board_size}_{number_of_chromosomes}_{mutation_chance}_{number_of_mutations}_{cross_chance}.txt"),
              "w", encoding="utf-8") as output:
        try:
            while max_generations == 0 or current_solution.generation <= max_generations:
                current_solution.sort_chromosomes_by_score()
                last_solutions.append(current_solution.best_score)
                if len(last_solutions) > 10:
                    last_solutions.pop(0)
                if current_solution.generation % 10 == 0 or current_solution.generation == max_generations:
                    print(current_solution)
                    output.write(
                        f"{current_solution.generation};{current_solution.best_score};{current_solution.dump_best_chromo()}\n")
                    output.flush()
                else:
                    output.write(f"{current_solution.generation};{current_solution.best_score}\n")

                results = roulette(current_solution, number_of_results=2)
                # print(str(current_solution.calculate_sum_cost(results[0])) + " " + str(
                #     current_solution.calculate_sum_cost(results[1])))
                current_solution = cross(current_solution, results, cross_chance)
                if statistics.mean(last_solutions) == current_solution.best_score:
                    print("Stagnation!")
                    mutation(current_solution, mutation_chance * 2, number_of_mutations * 2)
                else:
                    mutation(current_solution, mutation_chance, number_of_mutations)
        except Exception as e:
            print(e)
            output.close()
    print(f"Finished training at generation {current_solution.generation} with score {current_solution.best_score}")
    with open(os.path.join(folder, "finished", f"{id}.finished"), "w") as out:
        out.close()


def start_training_with_tournament(flow_name: str, cost_name: str, x_board_size: int, y_board_size: int,
                                   number_of_chromosomes: int,
                                   number_of_cuts_per_chromosome: int, mutation_chance: float, number_of_mutations: int,
                                   sample_size: float, cross_chance: float, max_generations: int = -1,
                                   load_existing_generation: bool = False, results_folder: str = RESULTS_FOLDER, id=0):
    if not load_existing_generation:
        current_solution = generate_random_solution(flow_name, cost_name, x_board_size, y_board_size,
                                                    number_of_chromosomes)
    else:
        current_solution = load_data()
    last_solutions = []
    with open(os.path.join(results_folder,
                           f"output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tournament_{x_board_size}_{y_board_size}_{number_of_chromosomes}_{mutation_chance}_{number_of_mutations}_{max_generations}_{cross_chance}_{sample_size}.txt"),
              "w", encoding="utf-8") as output:
        while max_generations == -1 or current_solution.generation <= max_generations:
            current_solution.sort_chromosomes_by_score()
            last_solutions.append(current_solution.best_score)
            if len(last_solutions) > 10:
                last_solutions.pop(0)

            if current_solution.generation % 10 == 0 or current_solution.generation == max_generations:
                print(current_solution)
                output.write(
                    f"{current_solution.generation};{current_solution.best_score};{current_solution.dump_best_chromo()}\n")
                output.flush()
            else:
                output.write(f"{current_solution.generation};{current_solution.best_score}\n")
            # best_chromo = current_solution.chromosomes[0]
            # show_machines(current_solution, best_chromo)
            results = selection_tournament(current_solution, sample_size, number_of_results=2)
            # print(str(current_solution.calculate_sum_cost(results[0])) + " " + str(
            #     current_solution.calculate_sum_cost(results[1])))
            current_solution = cross(current_solution, results, cross_chance)
            current_solution.sort_chromosomes_by_score()
            if statistics.mean(last_solutions) == current_solution.best_score:
                print("Stagnation!")
                mutation(current_solution, mutation_chance * 2, number_of_mutations * 2)
            else:
                mutation(current_solution, mutation_chance, number_of_mutations)
    with open(os.path.join(results_folder, "finished", f"{id}.finished"), "w") as out:
        out.close()
        pass


pass


def generate_random_tournament(flow_name: str, cost_name: str, x_board_size: int, y_board_size: int,
                               number_of_randoms=10000, folder="results\\random"):
    with open(os.path.join(folder,
                           f"random_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{x_board_size}_{y_board_size}.txt"),
              "w", encoding="utf-8") as output:
        for i in range(number_of_randoms):
            current_solution = generate_random_solution(flow_name, cost_name, x_board_size, y_board_size, 1)
            current_solution.sort_chromosomes_by_score()
            output.write(
                f"{i};{current_solution.best_score};{current_solution.dump_best_chromo()}\n")
            output.flush()


def load(input_file_name="input.txt"):
    with open(input_file_name, "r", encoding="utf-8") as input:
        return list(map(lambda d: int(d), input.readline().split(";")))


def save(completed_id, input_file_name="input.txt"):
    with open(input_file_name, "w", encoding="utf-8") as input:
        print(completed_id)
        ids = ";".join(list(map(lambda d: str(d), completed_id)))
        input.write(ids)
        input.flush()
        input.close()


dic = {}
if __name__ == '__main__':
    generate_random_tournament("dane\\hard_flow.json", "dane\\hard_cost.json", 5, 6, number_of_randoms=20000,
                               folder="hard\\automat")
    exit(0)
    # start_training_with_tournament("dane\\hard_flow.json", "dane\\hard_cost.json", 5, 6, 1000, 1, 0.3, 8, 0.2, 0.9, 1200,
    #                                False, results_folder="hard\\tournament")
    # start_training_with_roulette("dane\\hard_flow.json", "dane\\hard_cost.json", 5, 6, 200, 1, 0.004, 2, 0.9, 1000, False, folder="hard\\tournament")
    # #
    # exit(0)
    id = 0

    # dic["completed_id"] = load()

    # def save_thread():

    # threading.Thread(daemon=True, target=save_thread).start()

    with Pool(6) as p:
        with open("all_gens.txt", "r", encoding="utf-8") as input_file:
            for e in input_file.readlines():
                split = e.split(";")
                if not os.path.exists(os.path.join("hard\\automat\\finished", f"{split[0]}.finished")):
                    if split[1] == "r":
                        # f"{id};t;{max_generations};{chromosomes};{mutations / 1000};{mutation_count};{cross_chance};{tournament_size / 10};\n")
                        p.apply_async(start_training_with_roulette,
                                      ["dane\\hard_flow.json", "dane\\hard_cost.json", 5, 6, int(split[3]), 1,
                                       float(split[4]), int(split[5]), int(split[6]) / 10, int(split[2]), False,
                                       "hard\\automat", int(split[0])])
                    else:
                        p.apply_async(start_training_with_tournament,
                                      ["dane\\hard_flow.json", "dane\\hard_cost.json", 5, 6, int(split[3]), 1,
                                       float(split[4]), int(split[5]), float(split[7]), int(split[6]) / 10,
                                       int(split[2]), False,
                                       "hard\\automat", int(split[0])])
                else:
                    print(f"{split[0]} exists!")
        p.close()
        p.join()

    exit(0)
    with open("all_gens.txt", "w", encoding="utf-8") as output:
        for max_generations in range(10, 200, 10):  # liczba pokoleń
            for chromosomes in range(200, 600, 100):  # rozmiar populacji
                for mutations in range(0, 100,
                                       10):  # prawdopodinstwo mutacji, w turnieju / 100, w przypadku ruletki /1000
                    for mutation_count in range(8, 9, 4):  # ilość mutacji
                        for cross_chance in range(7, 9):  # prawdopodobieństwo cross / 10
                            id += 1
                            output.write(
                                f"{id};r;{max_generations};{chromosomes};{mutations / 1000};{mutation_count};{cross_chance};\n")

                            # p.apply_async(start_training_with_roulette,
                            #               ["dane\\hard_flow.json", "dane\\hard_cost.json", 5, 6, chromosomes, 1,
                            #                float(mutations) / 100, mutation_count, cross_chance, max_generations, False,
                            #                "hard\\automat"])
                            for tournament_size in range(0, 10):  # ile % turnieju
                                id += 1
                                output.write(
                                    f"{id};t;{max_generations};{chromosomes};{mutations / 1000};{mutation_count};{cross_chance};{tournament_size / 10};\n")

                            # p.apply_async(start_training_with_tournament,
                            #                   ["dane\\hard_flow.json", "dane\\hard_cost.json", 5, 6, chromosomes, 1,
                            #                    float(mutations) / 100, mutation_count, tournament_size/10, cross_chance, max_generations, False,
                            #                    "hard\\automat"])

    # sol = load_data()
    # print(count)


def generateNaive(flow_name: str, cost_name: str, x_board_size: int, y_board_size: int):
    current_solution = generate_random_solution(flow_name, cost_name, x_board_size, y_board_size, 1)
    machines_id = [0, 1, 2, 3, 4, 5, 6, 7, 8]
