import json

def getData(fileName):
    with open(fileName) as dataFile:
        data = json.load(dataFile)
        return data

data = getData('final2.json')
kclustercosine = getData('KClusteringOutput_cosineSimilarity.json')
kclusterhamming = getData('KClusteringOutput_hamming.json')
kclusterjaccard = getData('KClusteringOutput_jaccard.json')

for item in data:
    if item["fields"]["text"] in kclustercosine:
        item["fields"]["kclustercosine"] = kclustercosine[item["fields"]["text"]]
    else:
        item["fields"]["kclustercosine"] = -1
    if item["fields"]["text"] in kclusterhamming:
        item["fields"]["kclusterhamming"] = kclusterhamming[item["fields"]["text"]]
    else:
        item["fields"]["kclusterhamming"] = -1
    if item["fields"]["text"] in kclusterjaccard:
        item["fields"]["kclusterjaccard"] = kclusterjaccard[item["fields"]["text"]]
    else:
        item["fields"]["kclusterjaccard"] = -1

with open('final3.json', 'w') as outfile:
    json.dump(data, outfile)