from __future__ import division

import json
import math
from collections import deque
import string

specialChars = [u'\xe0', u'\xe8', u'\xe9', u'\xf1', u'\xf6', u'\xfb', u'\xed', u'\xea', u'\xf3', u'\xf4', u'\xe1', u'\xd7', u'\xee', u'\xe7', u'\u2019', u'\xce', u'\xe4', u'\xe3', u'\xe6', u'\xfc', u'\xe2', u'\xeb', u'\xd6', u'\xfa', u'\xc8', u'\xc1', u'\xc9']

def jaccardDistance(str1, str2):
    intersect = set(str1).intersection(str2)
    union = set(str1).union(str2)
    return len(intersect)/len(union)

def getData(fileName):
    with open(fileName) as dataFile:
        data = json.load(dataFile)
        return data

def DBSCAN(data, epsilon, minPoints, distanceMeasure):
    NOISECLUSTER = 0
    clusterNum = 0
    visited = []
    pointToCluster = {}
    for question in data:
        print (len(visited) / len(data))*100, "% through the data."
        if question['pk'] in visited:
            continue
        visited.append(question['pk'])
        neighborPoints = getClosePoints(data, question['pk'], epsilon, distanceMeasure)
        if len(neighborPoints) < minPoints:
            pointToCluster[question["pk"]] = NOISECLUSTER
        else:
            clusterNum += 1
            expandCluster(question, neighborPoints, clusterNum, epsilon, minPoints, pointToCluster, visited, data, distanceMeasure)

    return pointToCluster

def expandCluster(point, neighboringPoints, clusterNumber, epsilon, minPoints, pointToCluster, visited, data, distanceMeasure):
    pointToCluster[point["pk"]] = clusterNumber
    itemQueue = deque()
    for newPoint in neighboringPoints:
        itemQueue.append(newPoint)
    while itemQueue:
        newPoint = itemQueue.pop()
        print "Size of Queue ", len(itemQueue)
        if newPoint not in visited:
            visited.append(newPoint)
            newNeighborPoints = getClosePoints(data, newPoint, epsilon, distanceMeasure)
            print (len(visited) / len(data))*100, "% through the data."
            print "Current number of clusters ", clusterNumber
            if len(newNeighborPoints) > minPoints:
                for item in newNeighborPoints:
                    if item not in visited:
                        itemQueue.append(item)
                #neighboringPoints.update(newNeighborPoints)
            if newPoint not in pointToCluster:
                pointToCluster[newPoint] = clusterNumber

def getClosePoints(data, pointPK, epsilon, distanceMeasure):
    if distanceMeasure == "cosine":
        distance = cosineDistance
    elif distanceMeasure == "jaccard":
        distance = jaccardDistance
    elif distanceMeasure == "euclidean":
        distance = euclideanDistance
    else:
         distance = hammingDistance
    for x in data:
        if x["pk"] == pointPK:
            point = x
            break
    neighbors = set()
    for question in data:
        if question != point:
            if distance(question['fields']['answer'], point['fields']['answer']) > epsilon:
                neighbors.add(question["pk"])

    return neighbors

def addToBothDicts(dict1, dict2, chars):
    for item in chars:
        dict1[item] = 0
        dict2[item] = 0

def cosineDistance(str1, str2):
    rep1 = {}
    rep2 = {}

    for char in string.printable:
        rep1[char] = 0
        rep2[char] = 0

    addToBothDicts(rep1, rep2, specialChars)

    for char in str1:
        rep1[char] += 1

    for char in str2:
        rep2[char] += 1 

    x2 = 0
    y2 = 0
    xy = 0
    for key in rep1:
        x = rep1[key]
        y = rep2[key]
        x2 += x**2
        y2 += y**2
        xy += x*y

    return xy/math.sqrt(x2*y2)

def hammingDistance(str1, str2):
    difference = 0
    for i in range(max([len(str1), len(str2)])):
        if i >= len(str1) or i >= len(str2) or str1[i] != str2[i]:
            difference += 1
    return 1 - (difference / max([len(str1), len(str2)]))

'''
def euclideanDistance(str1, str2):
    rep1 = {}
    rep2 = {}

    for char in string.printable:
        rep1[char] = 0
        rep2[char] = 0

    addToBothDicts(rep1, rep2, specialChars)

    for char in str1:
        rep1[char] += 1

    for char in str2:
        rep2[char] += 1 

    summed = 0
    for key in rep1:
        summed += (rep1[key] - rep2[key])**2
    return 1 - math.sqrt(summed)/max([len(str1), len(str2)])
'''

def euclideanDistance(str1, str2):
    rep1, rep2 = {}, {}

    for char in str1:
        if char not in rep1:
            rep1[char] = 0
        rep1[char] += 1

    for char in str2:
        if char not in rep2:
            rep2[char] = 0
        rep2[char] += 1

    summed = 0
    for key in rep1:
        if key not in rep2:
            rep2v = 0
        else:
            rep2v = rep2[key]
        summed += (rep1[key] - rep2v)**2

    for key in rep2:
        if key not in rep1:
            rep1v = 0
        else:
            rep1v = rep1[key]
        if key not in str1:
            summed += (rep1v - rep2[key])**2

    return 1 - math.sqrt(summed)/max([len(str1), len(str2)])

def addDictToItems(data, dic, name):
    for key in dic:
        for x in data:
            if x["pk"] == key:
                item = x
                break
        item["fields"][name] = dic[key]

def getMetrics(filename):
    data = getData("data.json")
    namesOfFields = ["DBSCANEuclideanDistance"]
    for i in namesOfFields:
        if i == "DBSCANJaccardDistance":
            distance = jaccardDistance
        elif i == "DBSCANHammingDistance":
            distance = hammingDistance
        elif i == "DBSCANCosineDistance":
            distance = cosineDistance
        else:
            distance = euclideanDistance
        seen = {}
        clusters = {}
        for item in data:
            if item["fields"][i] not in seen:
                seen[item["fields"][i]] = 0
                clusters[item["fields"][i]] = []
            seen[item["fields"][i]] += 1
            clusters[item["fields"][i]].append(item)

        print "The number of clusters for ", i, " is ", len(seen)
        total = 0
        for key in seen:
            total += seen[key] 
        print "The amount of items not in the clusters for ", i, " are ", seen[0]/total
        print "The average size of the clusters in ", i, " are ", total/len(seen)
        totalD = 0
        totalComparisons = 0
        for j in xrange(1, len(seen)):
            counter = 0
            for item in clusters[j]:
                for item2 in clusters[j]:
                    if item != item2:
                        totalD += distance(item["fields"]["answer"], item2["fields"]["answer"])
                        totalComparisons += 1
                counter += 1
        print "The average intracluster distance for ", i, " is ", totalD/totalComparisons



if __name__ == "__main__":
    #for item in [("euclidean", "DBSCANEuclideanDistance")]:
        #data = getData("data.json")
        #addDictToItems(data, DBSCAN(data, 0.90, 10, item[0]), item[1])
        #with open('data.json', 'w') as outfile:
           #json.dump(data, outfile)
    #data = getData("data.txt")
    #seen = set()
    #for item in data:
    #    if item["fields"]["testClusterNum"] not in seen:
    #        seen.add(item["fields"]["testClusterNum"])

    #print seen
    getMetrics("data.json")