import operator
import random
import string
from collections import defaultdict

from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Count
from nltk.corpus import stopwords

from models import Question, QuestionCategory


# Create your views here.

def index(request):
	return render(request, 'index.html', {})

def questionsIndex(request):
	qcount = Question.objects.all().count()
	rand = random.randint(0, qcount-21)
	tquestions = Question.objects.all()[rand:rand+20]
	return render(request, 'questions.html', {'questions': tquestions, 'count': qcount})

def questionDetail(request, qid):
	ques = Question.objects.get(id=qid)
	#Stubbed for similar questions and trend questions
	qcount = Question.objects.filter(kclustercosine__exact = ques.kclustercosine).count()
	rand1 = random.randint(0, qcount-5)
	rand2 = random.randint(0, qcount-5)
	sQs = Question.objects.filter(kclustercosine__exact = ques.kclustercosine)[rand1:rand1+5]
	tQs = Question.objects.all()[rand2:rand2+5]
	return render(request, 'questiondetail.html', {'question': ques, 'similarquestions': sQs, 'trendquestions': tQs})

def getMostCommonWord(i, cluster):
	if i == 0:
		return "Noise"
	wordCounts = {}
	for question in cluster:
		for word in [ i for i in question.answer.split(" ") if i not in stopwords.words("english")]:
			if word not in wordCounts:
				wordCounts[word] = 0
			wordCounts[word] += 1
	return max(wordCounts.iteritems(), key=operator.itemgetter(1))[0]

def prepare(request):
	cluster = []
	#qcount = Question.objects.all().count()
	method = request.GET.get('method', 'DBSCANJaccardDistance')
	if method == "DBSCANJaccardDistance":
		for i in range(67):
			qs = Question.objects.filter(DBSCANJaccardDistance__exact = i)[:10]
			temp = []
			for j in qs:
				temp.append(j)
			cluster.append({'name': "Cluster: " + getMostCommonWord(i, temp), 'questions': temp})
	elif method == "DBSCANEuclideanDistance":
		for i in range(64):
			qs = Question.objects.filter(DBSCANEuclideanDistance__exact = i)[:10]
			temp = []
			for j in qs:
				temp.append(j)
			cluster.append({'name': "Cluster: " + getMostCommonWord(i, temp), 'questions': temp})
	elif method == "DBSCANCosineDistance":
		for i in range(127):
			qs = Question.objects.filter(DBSCANCosineDistance__exact = i)[:10]
			temp = []
			for j in qs:
				temp.append(j)
			cluster.append({'name': "Cluster: " + getMostCommonWord(i, temp), 'questions': temp})
	elif method == "DBSCANHammingDistance":
		for i in range(63):
			qs = Question.objects.filter(DBSCANHammingDistance__exact = i)[:10]
			temp = []
			for j in qs:
				temp.append(j)
			cluster.append({'name': "Cluster: " + getMostCommonWord(i, temp), 'questions': temp})

	return render(request, 'prepare.html', {'clusters': cluster, 'method': method})

def categoriesIndex(request):
	cats = QuestionCategory.objects.all()
	catCounts = []
	for cat in cats:
		count = Question.objects.filter(category = cat.id).count()
		if count > 5:
			catCounts.append(dict({'cat' : cat, 'count' : count}))
			
	catCounts.sort(key = lambda c: c['count'], reverse = True)
	
	return render(request, 'categories.html', {'categories': catCounts})

def categoryDetail(request, catId):
	cat = QuestionCategory.objects.get(id=catId)
	ques = Question.objects.filter(category=catId).order_by('airDate')
	qcount = len(ques)
	return render(request, 'categorydetail.html', {'cat': cat.category, 'questions': ques})

# stub trends view
def trends(request):
	# Each show is a "basket" of items (questions)
	# Find frequent itemsets across shows, treating questions in the same cluster as equal
	
	# Build list of show ids
	shows = [q['showNumber'] for q in Question.objects.values("showNumber").annotate(n = Count("pk"))]
	
	trends = apriori(shows, 0.1)

	exampleQs = []

	for key in trends:
		qcount = Question.objects.filter(kclustercosine__exact = key).count()
		rand1 = random.randint(0, qcount-5)
		exampleQs.append(Question.objects.filter(kclustercosine__exact = key)[rand1])
	
	#import pdb; pdb.set_trace()

	return render(request, 'trends.html', {'trends': trends, 'exampleQuestion': exampleQs})
	
# Apriori algorithm implementation
def apriori(shows, threshold):
	minSupport = int(len(shows)*threshold)
	
	counts = defaultdict(int)
	frequent = {}	# dict of (sorted itemset tuple) -> frequency
	
	# count 1-itemsets
	for id in shows:
		for q in Question.objects.filter(showNumber = id):
			cluster = q.kclustercosine
			counts[cluster] += 1
	
	# save frequent 1-itemsets
	frequent[1] = { (k,):v for k, v in counts.items() if v > minSupport }
	
	# increment k until no frequent itemsets are generated
	for k in range(2, 100):
		# generate candidate k-itemsets from the frequent (k-1)-itemsets
		candidates = genCandidates(frequent[k-1].keys(), k)
		candidateCounts = defaultdict(int)
		
		# test each candidate's support
		for show in shows:
			# collect all cluster ids from the show
			showClusters = set([q['kclustercosine'] for q in Question.objects.filter(showNumber = show).values('kclustercosine').annotate(n = Count("pk"))])
			
			for candidate in candidates:
				# test if show contains all cluster ids in the candidate
				if showClusters.issuperset(candidate):
					candidateCounts[tuple(candidate)] += 1
					
		# prune unsupported candidates and add to the list of frequent sets
		# itemsets are sorted before adding to simplify candidate generation on subsequent iterations
		freq = {}
		for key, val in candidateCounts.items():
			if val > minSupport:
				itemset = list(key)
				itemset.sort()
				freq[tuple(itemset)] = val
		
		if len(freq) == 0:
			break
		else:
			frequent[k] = freq
				
		#frequent[k] = { k:v for k, v in candidateCounts.items() if v > minSupport }
	
	return frequent
	
# Uses the F(k-1) x F(k-1) method to generate a list of unordered candidate itemsets of the given size, given a list of sorted frequent itemsets of length size-1
def genCandidates(frequent, size):
	candidates = []
	
	# Generate potential itemsets by joining two nearly-equal itemsets
	for i in range(len(frequent)):
		first = frequent[i]
		
		for j in range(i+1, len(frequent)):
			second = frequent[j]
			
			if len(first) != len(second):	# should not happen
				import pdb; pdb.set_trace()
				
			# Both sets must be equal up to the final element
			if nearlyEqual(first, second):
				newCandidate = set(first)
				newCandidate.add(second[-1])
				candidates.append(newCandidate)
			
	return candidates
	
# Tests two sorted lists of the same size to see if they are equal up to the final element, which must be different
def nearlyEqual(first, second):
	size = len(first)
	
	if size != len(second):	# should not happen
		raise ValueError('Lists are of different lengths - cannot compare them')
	
	for k in range(size - 1):
		if first[k] != second[k]:
			return False
	
	return first[-1] != second[-1]
