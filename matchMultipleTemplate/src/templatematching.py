# -*- coding: utf-8 -*-
"""
    This was inspired by the following collab:
    https://colab.research.google.com/github/learn-ai-python/OpenCV-Tutorials/blob/main/Template_Matching/How_to_use_template_matching_with_OpenCV%3F_%7C_Python.ipynb
"""

import os
import itertools
import cv2
import numpy as np
from matplotlib import pyplot as plt

__DELETE_FILES__ = False

from .geneticalgorithm.geneticalgorithm import genetic_algorithm
from .geneticalgorithm.tsp import TSP
from .logger import SingletonLogger


def remove_coordinates_close(input_list, threshold=(10, 10)):
    combos = itertools.combinations(input_list, 2)
    points_to_remove = [point2
                        for point1, point2 in combos
                        if
                        abs(point1[0] - point2[0]) <= threshold[0] and abs(point1[1] - point2[1]) <= threshold[1]]
    points_to_keep = [point for point in input_list if point not in points_to_remove]
    return points_to_keep


def draw_path(problem, permutation, shortestHamPath=True):
    coords = []

    splitPermutation = permutation.index(len(permutation) - 1)
    firstHalf = permutation[:splitPermutation]
    secondHalf = permutation[splitPermutation:]
    permutation = secondHalf + firstHalf
    for i in permutation:
        if problem.coords[i] != [-1, -1]:
            coords.append(problem.coords[i])
    if not shortestHamPath:
        coords.append(problem.coords[permutation[0]])
    xs, ys = zip(*coords)  # create lists of x and y values
    plt.plot(xs, ys, marker='o')


def match_template(fileName, dir_name, original_file_name):
    logger = SingletonLogger()
    logger.log("Matching template", "VERBOSE")
    img = cv2.imread(dir_name + original_file_name)
    # convert it from BGR to RGB
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # and convert it from BGR to GRAY
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    template = cv2.imread(dir_name + "/templates/" + fileName, 0)

    # then we get the shape of the template
    w, h = template.shape[::-1]

    # So, we take our image, our template and the template matching method
    res = cv2.matchTemplate(imgGray,
                            template,
                            cv2.TM_CCOEFF_NORMED)

    threshold = 0.9
    # then we get the locations, that have values bigger, than our threshold
    loc = np.where(res >= threshold)

    logger.log("DONE -- Matching template", "VERBOSE")
    # remove points too close to each other, likely the same image matched twice
    newPoints = remove_coordinates_close(list(zip(*loc[::-1])))

    tspFileName = "teste.tsp"
    f = open(tspFileName, "w")

    f.write("NAME: " + fileName + '\n')
    f.write("TYPE: TSP" + '\n')
    f.write("DIMENSION: " + str(len(newPoints)) + '\n')
    f.write("EDGE_WEIGHT_TYPE: EUC_2D" + '\n')
    f.write("NODE_COORD_SECTION" + '\n')
    index = 1
    for pt in newPoints:
        f.write(" ".join([str(index), str(pt[0] + w / 2), str(pt[1] + h / 2)]) + '\n')
        index += 1
        cv2.rectangle(imgRGB,
                      pt,
                      (pt[0] + w, pt[1] + h),
                      (230, 0, 255),
                      1)
    f.write("EOF" + '\n')
    f.close()
    problem = TSP(tspFileName)

    logger.log("Calculating path", "VERBOSE")
    path, history = genetic_algorithm(problem)
    logger.log("DONE -- Calculating path", "VERBOSE")

    fig = plt.figure(figsize=(10, 10))
    plt.imshow(imgRGB, alpha=0.4)
    draw_path(problem, path)
    plt.savefig(dir_name + '/paths/' + fileName)
    plt.close('all')
    os.remove(tspFileName)


def template_matching(directory, file_name):
    entries = os.listdir(directory + "/templates/")

    if not os.path.isdir(directory + "/paths/"):
        os.makedirs(directory + "/paths/")
    files = os.listdir(directory + "/paths/")

    if __DELETE_FILES__:
        for f in files:
            os.remove(directory + "/paths/" + f)

    for entry in entries:
        match_template(entry, directory, file_name)