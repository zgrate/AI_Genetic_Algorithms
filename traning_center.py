import os
import pickle
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
                                 max_generations: int = 0, load_existing_generation: int = False,
                                 folder: str = RESULTS_FOLDER):
    print(
        f"Training soluion for {x_board_size}x{y_board_size} with {number_of_chromosomes} {mutation_chance} {number_of_mutations}")
    if not load_existing_generation:
        current_solution = generate_random_solution(flow_name, cost_name, x_board_size, y_board_size,
                                                    number_of_chromosomes)
    else:
        current_solution = load_data()
    # print(current_solution.max_id())
    with open(os.path.join(folder,
                           f"output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_roulette_{x_board_size}_{y_board_size}_{number_of_chromosomes}_{mutation_chance}_{number_of_mutations}.txt"),
              "w", encoding="utf-8") as output:
        try:
            while max_generations == 0 or current_solution.generation <= max_generations:
                current_solution.sort_chromosomes_by_score()
                if current_solution.generation % 10 == 0 or current_solution.generation == max_generations:
                    print(current_solution)
                    output.write(
                        f"{current_solution.generation};{current_solution.best_score};{current_solution.dump_best_chromo()}\n")
                    output.flush()
                else:
                    output.write(f"{current_solution.generation};{current_solution.best_score}\n")

                results = roulette(current_solution)
                # print(str(current_solution.calculate_sum_cost(results[0])) + " " + str(
                #     current_solution.calculate_sum_cost(results[1])))
                current_solution = cross(current_solution, results[0], results[1], number_of_cuts_per_chromosome)
                mutation(current_solution, mutation_chance, number_of_mutations)
        except Exception as e:
            print(e)
            output.close()
    print(f"Finished training at generation {current_solution.generation} with score {current_solution.best_score}")


def start_training_with_tournament(flow_name: str, cost_name: str, x_board_size: int, y_board_size: int,
                                   number_of_chromosomes: int,
                                   number_of_cuts_per_chromosome: int, mutation_chance: float, number_of_mutations: int,
                                   sample_size: float, max_generations: int = -1,
                                   load_existing_generation: bool = False, results_folder: str = RESULTS_FOLDER):
    if not load_existing_generation:
        current_solution = generate_random_solution(flow_name, cost_name, x_board_size, y_board_size,
                                                    number_of_chromosomes)
    else:
        current_solution = load_data()
    with open(os.path.join(results_folder,
                           f"output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tournament_{x_board_size}_{y_board_size}_{number_of_chromosomes}_{mutation_chance}_{number_of_mutations}_{max_generations}.txt"),
              "w", encoding="utf-8") as output:
        while max_generations == -1 or current_solution.generation <= max_generations:
            current_solution.sort_chromosomes_by_score()
            if current_solution.generation % 10 == 0 or current_solution.generation == max_generations:
                print(current_solution)
                output.write(
                    f"{current_solution.generation};{current_solution.best_score};{current_solution.dump_best_chromo()}\n")
                output.flush()
            else:
                output.write(f"{current_solution.generation};{current_solution.best_score}\n")
            # best_chromo = current_solution.chromosomes[0]
            # show_machines(current_solution, best_chromo)
            results = selection_tournament(current_solution, sample_size)
            # print(str(current_solution.calculate_sum_cost(results[0])) + " " + str(
            #     current_solution.calculate_sum_cost(results[1])))
            current_solution = cross(current_solution, results[0], results[1], number_of_cuts_per_chromosome)
            mutation(current_solution, mutation_chance, number_of_mutations)


pass


def generate_random_tournament(flow_name: str, cost_name: str, x_board_size: int, y_board_size: int,
                               number_of_randoms=10000, folder="results\\random"):
    with open(os.path.join(folder,
                           f"random_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tournament_{x_board_size}_{y_board_size}.txt"),
              "w", encoding="utf-8") as output:
        for i in range(number_of_randoms):
            current_solution = generate_random_solution(flow_name, cost_name, x_board_size, y_board_size, 1)
            current_solution.sort_chromosomes_by_score()
            output.write(
                f"{i};{current_solution.best_score};{current_solution.dump_best_chromo()}\n")
            output.flush()


if __name__ == '__main__':
    # generate_random_tournament("dane\\easy_flow.json", "dane\\easy_cost.json", 3, 3)
    # exit(0)
    start_training_with_tournament("dane\\hard_flow.json", "dane\\hard_cost.json", 5, 6, 1000, 1, 0.3, 10, 0.1, 1200,
                                   False, results_folder="hard\\tournament")
    # start_training_with_roulette("dane\\hard_flow.json", "dane\\hard_cost.json", 5, 6, 200, 1, 0.4, 10, 1000, False, folder="hard\\tournament")
    #
    exit(0)
    count = 0
    with Pool(6) as p:
        for max_generations in range(10, 100, 5):
            for chromosomes in range(10, 50, 10):
                for mutations in range(0, 100, 10):
                    for mutation_count in range(0, 3):
                        p.apply_async(start_training_with_roulette,
                                      ["dane\\easy_flow.json", "dane\\easy_cost.json", 3, 3, chromosomes, 1,
                                       float(mutations) / 100, mutation_count, max_generations, False,
                                       "results\\roulette"])
        p.close()
        p.join()
    # sol = load_data()
    # print(sol)


def generateNaive(flow_name: str, cost_name: str, x_board_size: int, y_board_size: int):
    current_solution = generate_random_solution(flow_name, cost_name, x_board_size, y_board_size, 1)
    machines_id = [0, 1, 2, 3, 4, 5, 6, 7, 8]
