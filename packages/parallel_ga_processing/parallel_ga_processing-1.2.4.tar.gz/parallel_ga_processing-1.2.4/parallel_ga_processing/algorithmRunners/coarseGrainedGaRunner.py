from scoop import futures, logger
from parallel_ga_processing.geneticAlgorithms import CoarseGrainedBase


def run_coarse_grained_ga(population_size, chromosome_size,
                          number_of_generations,
                          neighbourhood_size, server_ip_addr, num_of_migrants, fitness):
    ins = CoarseGrainedBase(population_size=population_size, chromosome_size=chromosome_size,
                            number_of_generations=number_of_generations,
                            neighbourhood_size=neighbourhood_size, server_ip_addr=server_ip_addr,
                            num_of_migrants=num_of_migrants, fitness=fitness)

    populations = ins.initialize_population()
    channels = ins.initialize_topology()
    results = list(futures.map(ins, populations, channels))
    dct = {}
    logger.info("fuuu")
    for data in results:
        best_chromosome = data.pop(0)
        fitness_val = best_chromosome.fit
        vector = best_chromosome.chromosome
        dct[fitness_val] = vector
    logger.info("END RESULTTTTTT " + str(sorted(dct.items()).pop()))


def run_coarse_grained_ga_remote(population_size, chromosome_size,
                                 number_of_generations,
                                 neighbourhood_size, server_ip_addr, num_of_migrants, fitness):
    ins = CoarseGrainedBase(population_size=population_size, chromosome_size=chromosome_size,
                            number_of_generations=number_of_generations,
                            neighbourhood_size=neighbourhood_size, server_ip_addr=server_ip_addr,
                            num_of_migrants=num_of_migrants, fitness=fitness)
