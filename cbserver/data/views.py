import string
import random
import mimetypes
import cStringIO as StringIO
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from pymongo import MongoClient 
from pymongo import DESCENDING
import pymongo
import math

# open up 
client = MongoClient()
db = client.data
answer_collection = db.answers
rec_collection = db.recs

def uploadAnswers(request):
	if request.method == 'POST':
		# get the array of answers and loop through them and insert them to the
		request.POST['']
	return HttpResponse('Done')

def getRecVector(request, userId)
	return HttpResponse('sup')

#def updateRecVector(userId, )

class elo_core:
	def getExpectation(rating_1, rating_2):
		calc = (1.0 /(1.0 + pow(10, ((rating_2 - rating_1) / 400))))
		return calc

	def modifyRating(rating, expected, result, kfactor):
		calc = (rating + kfactor * (result - expected))
		return calc  
