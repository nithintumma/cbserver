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
from bson.objectid import ObjectId

# open up 
client = MongoClient()
db = client.data
answer_queue = db.answer_queue
rec_collection = db.recs

def uploadAnswers(request):
	if request.method == 'POST':
		# get the array of answers and loop through them and insert them to the
		request.POST['']
	return HttpResponse('Done')

def getRecVector(request, userId)
	return HttpResponse('sup')

#def updateRecVector(userId, )


def processAnswerQueue(request):
	# group the answers
	#answer_queue.group()	
	answer_records = answer_queue.find()
	for answer in answer_records:
		# find the rec for that user
		# if it does not exist create it
		rec = rec_collection.find_one({userId: answer.forFacebookId})
		if rec:
			try:
				winning_score = rec[answer.chosenProduct]
			except:
				winning_score = 1600
			try:
				losing_score = rec[answer.wrongProduct]
			except:
				losing_score = 1600
			# calculate elo scores
			new_chosen_score, new_wrong_score = calculate_elo_rank(winning_score, losing_score)
			rec_collection.update({'_id': ObjectId(rec._id)}, {"$set": {answer.chosenProduct: new_chosen_score, answer.wrongProduct: new_wrong_score}})	
			
		else:
			new_chosen_score, new_wrong_score = calculate_elo_rank()
			# create
			rec_collection.insert({"userId": answer.forFacebookId, answer.wrongProduct: new_wrong_score, answer.chosenProduct: new_chosen_score})
			
	return HttpResponse()


class elo_core:
	def getExpectation(rating_1, rating_2):
		calc = (1.0 /(1.0 + pow(10, ((rating_2 - rating_1) / 400))))
		return calc

	def modifyRating(rating, expected, result, kfactor):
		calc = (rating + kfactor * (result - expected))
		return calc



PLAYER_A = 1
PLAYER_B = 2

def calculate_elo_rank(player_a_rank=1600, player_b_rank=1600, winner=PLAYER_A, penalize_loser=True):
    if winner is PLAYER_A:
        winner_rank, loser_rank = player_a_rank, player_b_rank
    else:
        winner_rank, loser_rank = player_b_rank, player_a_rank
    rank_diff = winner_rank - loser_rank
    exp = (rank_diff * -1) / 400
    odds = 1 / (1 + math.pow(10, exp))
    if winner_rank < 2100:
        k = 32
    elif winner_rank >= 2100 and winner_rank < 2400:
        k = 24
    else:
        k = 16
    new_winner_rank = round(winner_rank + (k * (1 - odds)))
    if penalize_loser:
        new_rank_diff = new_winner_rank - winner_rank
        new_loser_rank = loser_rank - new_rank_diff
    else:
        new_loser_rank = loser_rank
    if new_loser_rank < 1:
        new_loser_rank = 1
    if winner is PLAYER_A:
        return (new_winner_rank, new_loser_rank)
    return (new_loser_rank, new_winner_rank)  
