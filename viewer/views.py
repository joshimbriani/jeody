import operator
import random

from django.http import HttpResponse
from django.shortcuts import render
from nltk.corpus import stopwords

from models import Question


# Create your views here.

def index(request):
	return render(request, 'index.html', {})

def questionsIndex(request):
	qcount = Question.objects.all().count()
	rand = random.randint(0, qcount-11)
	tquestions = Question.objects.all()[rand:rand+10]
	return render(request, 'questions.html', {'questions': tquestions})

def questionDetail(request, qid):
	ques = Question.objects.get(id=qid)
	#Stubbed for similar questions and trend questions
	qcount = Question.objects.all().count()
	rand1 = random.randint(0, qcount-5)
	rand2 = random.randint(0, qcount-5)
	sQs = Question.objects.all()[rand1:rand1+5]
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
	for i in range(67):
		qs = Question.objects.filter(testClusterNum__exact = i)[:10]
		temp = []
		for j in qs:
			temp.append(j)
		cluster.append({'name': "Cluster: " + getMostCommonWord(i, temp), 'questions': temp})
	#rand1 = random.randint(0, qcount-5)
	#qs = Question.objects.all()[rand1:rand1+10]
	#for i in range(10):
	#	cluster.append({'name': str(i+1), 'questions': [qs[i]]})
	#print cluster
	return render(request, 'prepare.html', {'clusters': cluster})
