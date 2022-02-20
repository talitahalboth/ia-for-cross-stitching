import random

import utils
from EAX import eax
from individual import Individual
from tsp import TSP
# from EAX import eax
from tournamentSelection import tournamentSelection

random.seed(120)





def random_population(problem, pop_size):
    population = []
    for _ in range(pop_size):
        permutation = problem.random_path()
        fitness = problem.evaluate(permutation)
        population.append(Individual(permutation, fitness))
    return population


'''
  _  _                    _ _        
 | \| |___ _ _ _ __  __ _| (_)______ 
 | .` / _ \ '_| '  \/ _` | | |_ / -_)
 |_|\_\___/_| |_|_|_\__,_|_|_/__\___|
                                     
'''


def normalizeFitness(problem, population):
    # normalizes fitness so that they sum to 1.0. Smaller paths -> higher fitness

    fitnessArray = []
    for i in range(len(population)):
        # invert the fitness, so a longer path becomes a smaller fitness
        fitnessArray.append(1 / problem.evaluate(population[i].permutation))
        population[i].fitness = 1 / problem.evaluate(population[i].permutation)
    soma2 = 0.0
    for individual in population:
        soma2 += individual.fitness
    res = 0.0

    for i in range(len(population)):
        fitnessArray[i] = fitnessArray[i] / soma2
        population[i].fitness = fitnessArray[i]
        res += population[i].fitness


'''
  ___                  _     ___      _        _   _          
 | _ \__ _ _ _ ___ _ _| |_  / __| ___| |___ __| |_(_)___ _ _  
 |  _/ _` | '_/ -_) ' \  _| \__ \/ -_) / -_) _|  _| / _ \ ' \ 
 |_| \__,_|_| \___|_||_\__| |___/\___|_\___\__|\__|_\___/_||_|
                                                                                           
'''




def parentSelection(problem, population):
    return tournamentSelection(problem, population, min(int(len(population[0].permutation) / 10), 1))


'''
   ___                                
  / __|_ _ ___ ______ _____ _____ _ _ 
 | (__| '_/ _ (_-<_-</ _ \ V / -_) '_|
  \___|_| \___/__/__/\___/\_/\___|_|  
                                      
'''


def crossover(a, b, problem):
    children = [[], []]
    # generates 2 children with the same parent and returns them
    children[0] = eax(a, b, problem)
    children[1] = eax(a, b, problem)
    return children


'''
  __  __      _        _   _          
 |  \/  |_  _| |_ __ _| |_(_)___ _ _  
 | |\/| | || |  _/ _` |  _| / _ \ ' \ 
 |_|  |_|\_,_|\__\__,_|\__|_\___/_||_|
                                      
'''


def mutate(permutation, mutationRate=0.01):
    val = random.random()
    # elements in the permutation are randomly swaped 
    # probability of being swaped is based on mutation rate, which is a number between 0 and 1
    while (val <= mutationRate):
        ixa = random.choice(permutation)
        ixb = random.choice(permutation)
        tmpElem = permutation[ixa]
        permutation[ixa] = permutation[ixb]
        permutation[ixb] = tmpElem
        val = random.random()
    return permutation


'''
  _  _         _      ___            ___      _        _   _          
 | \| |_____ _| |_   / __|___ _ _   / __| ___| |___ __| |_(_)___ _ _  
 | .` / -_) \ /  _| | (_ / -_) ' \  \__ \/ -_) / -_) _|  _| / _ \ ' \ 
 |_|\_\___/_\_\\__|  \___\___|_||_| |___/\___|_\___\__|\__|_\___/_||_|
                                                                      
'''


def selectionBaseOnAptitude(problem, populationA, populationB, populationSize):
    # rate parent and children population based on fitness, 
    populationTmp = []
    for individual in populationA:
        individual.fitness = problem.evaluate(individual.permutation)
        populationTmp.append(individual)
    for individual in populationB:
        individual.fitness = problem.evaluate(individual.permutation)
        populationTmp.append(individual)
    populationTmp.sort()
    newPopulation = []
    for i in range(0, populationSize):
        newPopulation.append(populationTmp[i])
    normalizeFitness(problem, newPopulation)
    return newPopulation


def nextGenSelection(problem, populationA, populationB, populationSize):
    return selectionBaseOnAptitude(problem, populationA, populationB, populationSize)


def new_generation(problem, population):
    children = []
    for _ in range(len(population)):
        parentA = parentSelection(problem, population)
        parentB = parentSelection(problem, population)

        [newIndividual, newIndividual1] = crossover(parentA, parentB, problem)

        mutate(newIndividual.permutation)
        mutate(newIndividual1.permutation)

        children.append(newIndividual)
        children.append(newIndividual1)

    nextGen = nextGenSelection(problem, population, children, len(population))
    return nextGen
    pass


def genetic_algorithm(problem, pop_size=50, max_gen=2000):
    population = random_population(problem, pop_size)
    fitness_history = []
    best_permutation = None
    # SUA IMPLEMENTACAO AQUI

    normalizeFitness(problem, population)

    bestFitness = problem.evaluate(population[0].permutation)
    best_permutation = population[0].permutation
    fitness_history.append(bestFitness)
    lastBestGen = 1

    # finds the best fitness of the initial population
    for individual in population:
        if (problem.evaluate(individual.permutation) <= bestFitness):
            bestFitness = problem.evaluate(individual.permutation)
            best_permutation = individual.permutation
    generations = 1
    utils.drawTour(problem, best_permutation, bestFitness, 1)
    bestGens = []
    bestGens.append(0)
    while (generations < max_gen) and (generations) < lastBestGen * 5:
        newGen = new_generation(problem, population)
        normalizeFitness(problem, newGen)
        population = newGen
        lastBest = bestFitness
        bestThis = problem.evaluate(population[0].permutation)
        for individual in population:
            curr = problem.evaluate(individual.permutation)
            if (curr <= bestThis):
                bestThis = curr
            if (curr <= bestFitness):
                bestFitness = curr
                best_permutation = individual.permutation

        if (bestFitness != lastBest):
            utils.drawTour(problem, best_permutation, bestFitness, generations)
            lastBestGen = generations

            bestGens.append(generations)
        generations += 1

        fitness_history.append(bestThis)
    return best_permutation, fitness_history


if __name__ == "__main__":
    problem = TSP('instances/eli51.tsp')
    best_solution, fitness_history = genetic_algorithm(problem, 50, 2000)
    print(best_solution, problem.evaluate(best_solution))
