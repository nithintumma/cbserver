import string
import random
import mimetypes
import math

from pymongo import MongoClient
from pymongo import DESCENDING

import pymongo as pm

from bson.objectid import ObjectId

client = MongoClient()
db = client.data
answer_queue = db.answer_queue
rec_collection = db.recs
dif_collection = db.difs
products_to_process = db.toprocess
calc_recs = db.calcrecs
product_collection = db.processedproducts
PLAYER_A = 1
PLAYER_B = 2

def processAnswerQueue():
	answer_records = answer_queue.find()
	for answer in answer_records:
		print "For Facebook Id"
		print answer["forFacebookId"]
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
			print "Found rec for user"
		else:
			new_chosen_score, new_wrong_score = calculate_elo_rank()
			print new_chosen_score
			print new_wrong_score
			rec_collection.insert({'userId': answer["forFacebookId"], str(answer["wrongProduct"]): new_wrong_score, str(answer["chosenProduct"]): new_chosen_score})
			print "inserted new rec to database"
		products_to_process.insert({"product": chosen_product, "userId": user_id})
		products_to_process.insert({"product": wrong_product, "userId": user_id})	
		answer_queue.remove({"_id": ObjectId(answer["_id"])})

def processProductQueue():
	product_records = products_to_process.find()
	for product_r in product_records:
		user_id = product_r["userId"]
		product_id = product_r["product"]
		user_rec = rec_collection.find_one({"userId": user_id})
		if (not user_rec):
			print "Not a user rec"
			return 
		for product, rating in user_rec.iteritems():
			if (not (product == "userId" or product == "_id" or product == product_id)):
				product_1 = product_id
				product_2 = product
				if (int(product_id) > int(product)):
					product_1 = product
					product_2 = product_id
				dif = user_rec[product_1] - user_rec[product_2]
				dif_collection.update({"product1": product_1, "product2": product_2}, {"$inc": {"freq": 1, "dif": dif}}, True)
		products_to_process.remove({"_id": ObjectId(product_r["_id"])})				 			

# update the list of products
def updateUniqueProducts():
	# these are the productss that we are running the rec algorithm on
	product_list_1 = dif_collection.distinct("product1")
	product_list_2 = dif_collection.distinct("product2")
	products = list(set(product_list_1).union(set(product_list_2)))
	products = [{"product": id} for id in products]
	print products
	if (products.count > 0):
		product_collection.remove() 
		product_collection.insert(products)

		
# need to have a list of users to run this on every time
def generateCalculatedRatings(user_id):
	to_update = {}
	for product_r in product_collection.find():
		product_id = product_r["product"]
		# what to do here
		user_rec = rec_collection.find_one({"userId": user_id})
		if (not user_rec):
			return
		calc_rating = 0 
		calc_weight = 0
		for product, rating in user_rec.iteritems():
			if (not (product == "userId" or product == "_id")):
				# determine if the new product was in the			
				#calc_rating += (rating + dif_collection.find_one()				
				product_1 = product_id
				product_2 = product
				if (int(product_id) > int(product)):
					product_1 = product
					product_2 = product_id
				dif_doc = dif_collection.find_one({"product1": product_1, "product2": product_2})
				if(dif_doc):
					calc_rating += (rating + dif_doc["dif"]) * dif_doc["freq"]
					calc_weight += dif_doc["freq"]
		# update user calc_rec vector for given product
		to_update[product_id] = calc_rating/calc_weight
	print to_update
	calc_recs.update({"userId": user_id}, {"$set": to_update}, True)


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

#main code
#processAnswerQueue()
#processProductQueue()
#updateUniqueProducts()
#generateCalculatedRatings("551733910")
