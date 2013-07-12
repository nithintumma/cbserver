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
import json
from django.views.decorators.csrf import csrf_exempt
import requests

# open up 
client = MongoClient()
db = client.data
answer_queue = db.answer_queue
rec_collection = db.recs
top_friends = db.top_friends


def updateDBTopFriends(user_id, friends_scores, send=False):	
	scores = top_friends.find_one({"userId": user_id})
	if not scores:
		return {}
	scores_dict = scores["top_friends_scores"]
	if not scores_dict:
		scores_dict = {}

	for friend in friends_scores:
		try:
			scores_dict[str(friend[0])] += float(friend[1])
		except KeyError:
			scores_dict[str(friend[0])] = float(friend[1])
	if scores:	
		top_friends.update({"_id": ObjectId(scores["_id"])}, {"$set": {"top_friends_scores": scores_dict}})
	else:
		top_friends.insert({"userId": user_id, "top_friends_scores": scores_dict})	
	return scores_dict
	
@csrf_exempt
def updateTopFriends(request, user_id):
	friend_scores = json.loads(request.POST["data"])
	score_dict = updateDBTopFriends(user_id, friends_scores)
	response = HttpResponse(json.dumps({"all": scores_dict}))
	response["Access-Control-Allow-Origin"] = "*"
	response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
	response["Access-Control-Max-Age"] = "1000"
	response["Access-Control-Allow-Headers"] = "*"
	return response

@csrf_exempt
def uploadAnswers(request):	
	response =  HttpResponse(str(json.dumps(request.POST)))
	response["Access-Control-Allow-Origin"] = "*"
	response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
	response["Access-Control-Max-Age"] = "1000"
	response["Access-Control-Allow-Headers"] = "*"
	if request.method == 'POST':
		# get the array of answers and loop through them and insert them to the
		allAnswers = json.loads(request.POST['data'])
		to_insert = []
		for current_row in allAnswers:
			to_insert.append({
					"fromUser": current_row["fromUser"], 
					"forFacebookId": current_row["forFacebookId"], 
					"chosenProduct": current_row["chosenProduct"], 
					"wrongProduct": current_row["wrongProduct"]
			})
		if (len(to_insert) > 0):
			answer_queue.insert(to_insert)			
		return processAnswerQueue()
		return HttpResponse('Inserted into answer queue')
	return HttpResponse("Not a POST request")

def getRecVector(request, userId):
	return HttpResponse('sup')

# for a list of users, send sorted list of top friends to the production
def sendTopFriends(user_ids):
	for user_id in user_ids:
		scores = top_friends.find_one({"userId": user_id})
		if not scores:
			continue
		
		scores_dict = scores["top_friends_scores"]
		
		# send the new list in order to the server
		top_friends_list = [fb_id for fb_id, score in sorted(scores_dict.iteritems(), key=lambda x:x[1], reverse = True)]
		top_friends_list.remove(user_id)
		data = json.dumps(top_friends_list)
		#url = "http://ec2-54-245-213-191.us-west-2.compute.amazonaws.com/data/updatetopfriends/" + str(user_id) + "/"
		url = "http://54.244.251.104/data/updatetopfriends/" + str(user_id) + "/"
		r = requests.post(url, data={"top_friends": data})
		return HttpResponse(r.text)
	return HttpResponse("mod_ids is empty %d" % len(user_ids))
		
def processAnswerQueue():
	# group the answers
	#answer_queue.group()	
	answer_records = answer_queue.find()
	mod_ids = []
	for answer in answer_records:
		# find the rec for that user
		# if it does not exist create it
		rec = rec_collection.find_one({"userId": answer["forFacebookId"]})
		if rec:
			try:
				winning_score = rec[answer["chosenProduct"]]
			except:
				winning_score = 1600
			try:
				losing_score = rec[["answer.wrongProduct"]]
			except:
				losing_score = 1600
			# calculate elo scores
			new_chosen_score, new_wrong_score = calculate_elo_rank(winning_score, losing_score)
			rec_collection.update({'_id': ObjectId(rec["_id"])}, {"$set": {str(answer["chosenProduct"]): new_chosen_score, str(answer["wrongProduct"]): new_wrong_score}})	
			
		else:
			new_chosen_score, new_wrong_score = calculate_elo_rank()
			# create
			rec_collection.insert({"userId": answer["forFacebookId"], str(answer["wrongProduct"]): new_wrong_score, str(answer["chosenProduct"]): new_chosen_score})
		# update Top Friends
		updateDBTopFriends(answer["fromUser"], [[answer["forFacebookId"], 10]])
		mod_ids.append(answer["fromUser"])
		answer_queue.remove({"_id": ObjectId(answer["_id"])})	
		
	return sendTopFriends(list(set(mod_ids)))
	return HttpResponse("Completed updating")


# ------- ELO RANKING SORES
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
