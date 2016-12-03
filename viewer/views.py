import operator
import random
import string

from django.http import HttpResponse
from django.shortcuts import render
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
		catCounts.append(dict({'cat' : cat, 'count' : Question.objects.filter(category = cat.id).count()}))
	#questions = Question.objects.all();
	#indices = random.sample(range(len(questions)), 20)
	#cats = [questions[i].category for i in indices]
	#cats = [q.category for q in Question.objects.all().order_by('category').distinct('category')]
	#rand = random.randint(0, cats.count()-11)
	#tcategories = cats[rand:rand+10]
	return render(request, 'categories.html', {'categories': catCounts})

def categoryDetail(request, catId):
	cat = QuestionCategory.objects.get(id=catId)
	ques = Question.objects.filter(category=catId)
	commonwords = trend(ques)
	qcount = len(ques)
	return render(request, 'categorydetail.html', {'cat': cat.category, 'questions': ques, 'words': commonwords})

def trend(ques):
	#stopwords = ['a', 'an', 'the', 'is', 'at', 'to']
	#ques.sort(key = lambda q: q.airDate)
	topics = []
	wordtopics = [] # which topic is responsible for which word (estimated)
	for q in ques:
		# preprocessing: remove punctuation and stopwords
		text = q.text.translate(string.punctuation)
		words = [word for word in q.text.split() if word.lower not in stopwords.words("english")]
		wordtopics += words
		#words += q.answer.split()
		#for (w in words):
			# random initialization
			
	return wordtopics
