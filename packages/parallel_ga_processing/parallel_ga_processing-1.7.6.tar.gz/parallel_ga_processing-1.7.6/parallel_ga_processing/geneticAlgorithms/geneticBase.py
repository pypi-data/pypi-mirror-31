import numpy as np
import random
from .decorator import log_method
from scoop import logger


class GeneticAlgorithmBase(object):
    def __init__(self, population_size, chromosome_size, number_of_generations, fitness):
        self._population_size = population_size
        self._chromosome_size = chromosome_size
        self._number_of_generations = number_of_generations
        self._fitness = fitness

    @log_method()
    def initialize_population(self):
        """
        Generate the population
        :return: population
        """
        population = []
        for i in range(0, self._population_size):
            population.append(self._gen_individual())
        return population

    def _gen_individual(self):
        """
        Generate binary array
        """
        return list(map(int,
                        np.random.randint(2,
                            size=self._chromosome_size)))

    @log_method()
    def _crossover(self, father, mother):
        """
        Exchange the random number of bits
        between father and mother
        :param father
        :param mother
        """
        #cross = 1
        #for i in range(0, cross):
        #    mother[i] = father[i]
        #for i in range(cross, self._chromosome_size):
        #    father[i] = mother[i]
        return father, mother

    @log_method()
    def _mutation(self, chromosome):
        """
        Invert one random bit based on probability
        :param chromosome
        """
        #if np.random.choice([True, False], p=[0.1, 0.9]):
        #rnd = 0
        #chromosome[rnd] = abs(chromosome[rnd] - 1)
        return chromosome

    @log_method()
    def _choose_individuals_based_on_fitness(self, evaluation_data):
        fitness_max = evaluation_data.sort_objects().pop(0).fit
        chromosomes_reproducing = self._Individuals()
        best_individual = None

        for chromosome_data in evaluation_data.individuals:
            # best individual has 100% probability to reproduce
            # others probability is relative to his
            # weak individuals are replaced with new ones
            prob = chromosome_data.fit / fitness_max
            # retrieve best individual, others are randomly selected
            if int(prob) == 1 and best_individual is None:
                logger.info("BEST")
                best_individual = chromosome_data.chromosome
                chromosomes_reproducing.append_object(self._Individual(chromosome_data.fit,
                                                                       best_individual))
            elif np.random.choice([True, False], p=[prob, 1 - prob]):
                chromosomes_reproducing.append_object(self._Individual(chromosome_data.fit,
                                                                       chromosome_data.chromosome))
        return chromosomes_reproducing

    class _Individual(object):
        def __init__(self, fit, chromosome, value=''):
            self._fit = fit
            self._chromosome = chromosome
            self._value = value

        @property
        def fit(self):
            return self._fit

        @property
        def chromosome(self):
            return self._chromosome

        @property
        def value(self):
            return self._value

        def __str__(self):
            return "Fitness is " + str(self._fit) + " chromosome is " + str(self.chromosome)

        def __repr__(self):
            return self.__str__()

    class _Individuals(object):
        def __init__(self):
            self._objects = {}
            self._individuals = []

        @property
        def individuals(self):
            return self._individuals

        @property
        def objects(self):
            return self._objects

        def append_object(self, individual, source=None):
            self._individuals.append(individual)
            if source is None:
                return
            if source not in self._objects:
                self._objects[source] = self._NeighbourIndividuals(source)
            self._objects[source].add_individual(individual)

        def sort_objects(self):
            return sorted(self._individuals, key=lambda x: x.fit, reverse=True)

        def size_of_col(self, source):
            if int(source) not in self._objects:
                return 0
            return self._objects[int(source)].size()

        class _NeighbourIndividuals(object):
            def __init__(self, source):
                self._source = source
                self._individuals_per_source = []

            def add_individual(self, individual):
                self._individuals_per_source.append(individual)

            @property
            def individuals_per_source(self):
                return self._individuals_per_source

            @property
            def source(self):
                return self._source

            def size(self):
                return len(self._individuals_per_source)

            def __str__(self):
                return str(self._source) + " " + str(self._individuals_per_source)
