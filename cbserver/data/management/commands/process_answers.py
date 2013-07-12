# process_answers processes answer queues for recs and top friends

from django.core.management import BaseCommand, CommandError
from pymongo import MongoClient
from _process import calculate_elo_rank
import string
import random
import mimetypes
import math
import requests
from pymongo import MongoClient
from pymongo import DESCENDING

import pymongo as pm

from bson.objectid import ObjectId

class Command(BaseCommand):
		
	def sendTopFriends(self, user_ids):
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


	def updateDBTopFriends(self, user_id, friends_scores, send=False):	
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

	def handle(self, *args, **options):
		
		self.stdout.write("Starting")
		client = MongoClient()
		db = client.data
		answer_queue = db.answer_queue
		rec_collection = db.recs
		products_to_process = db.toprocess
		product_collection = db.processedproducts
		top_friends = db.top_friends

		mod_ids = []
		answer_records = answer_queue.find()
		for answer in answer_records:
			rec = rec_collection.find_one({"userId": answer["forFacebookId"]})
			user_id = answer["forFacebookId"]
			wrong_product = answer["wrongProduct"]
			chosen_product = answer["chosenProduct"]
			if rec:
				try:
					winning_score = rec[answer["chosenProduct"]]
				except:
					wining_score = 1600
				try:
					losing_score = rec[answer['wrongProduct']]
				except:
					losing_score = 1600
				new_chosen_score, new_wrong_score = calculate_elo_rank(winning_score, losing_score)
				rec_collection.update({"_id": ObjectId(rec['_id'])}, {'$set': {answer['chosenProduct']: new_chosen_score, answer['wrongProduct']: new_wrong_score}})
				self.stdout.write( "Found rec for user")
			else:
				new_chosen_score, new_wrong_score = calculate_elo_rank()
				self.stdout.write( new_chosen_score)
				self.stdout.write( new_wrong_score)
				rec_collection.insert({'userId': answer["forFacebookId"], str(answer["wrongProduct"]): new_wrong_score, str(answer["chosenProduct"]): new_chosen_score})
				self.stdout.write( "inserted new rec to database")
			products_to_process.insert({"product": chosen_product, "userId": user_id})
			products_to_process.insert({"product": wrong_product, "userId": user_id})	
			
			# update friends 
			scores_dict = self.updateDBTopFriends(answer["fromUser"], [[answer["forFacebookId"], 10]])
			mod_ids.append(answer["fromUser"])

			answer_queue.remove({"_id": ObjectId(answer["_id"])})
		self.sendTopFriends(mod_ids)
	
