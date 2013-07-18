import string
import random
import math
import time
from pymongo import MongoClient
from pymongo import DESCENDING
import pymongo as pm
from bson.objectid import ObjectId
import cPickle as pickle


client = MongoClient()
db = client.data

answer_queue = db.answer_queue
rec_collection = db.recs
dif_collection = db.difs
products_to_process = db.toprocess
calc_recs = db.calcrecs
user_collection = db.users_to_update
product_collection = db.processedproducts

DUMP = "dumps/difs.p"

def calculate_rankings(user_id):
	dif_matrix = pickle.load(open(DUMP, "rb"))
	to_update = {}
	user_rec = rec_collection.find_one({"userId": user_id})
	if (not user_rec):
		return False
	for product_r in product_collection.find():
		product_id = product_r["product"]
		# what to do here
		if (not user_rec):
			return
		calc_rating = 0 
		calc_weight = 1
		for product, rating in user_rec.iteritems():
			if (not (product == "userId" or product == "_id")):
				# determine if the new product was in the			
				#calc_rating += (rating + dif_collection.find_one()				
				product_1 = product_id
				product_2 = product
				if (int(product_id) > int(product)):
					product_1 = product
					product_2 = product_id
				#dif_doc = dif_collection.find_one({"product1": product_1, "product2": product_2})
				try:	
					dif_doc = dif_matrix[str(product_1)][str(product_2)]
					calc_rating += (rating + dif_doc[0]) * dif_doc[1]
					calc_weight += dif_doc[1]
				except:
					continue
				# update user calc_rec vector for given product
		to_update[str(product_id)] = calc_rating/calc_weight
	calc_recs.update({"userId": user_id}, {"$set": to_update}, True)
	return True
#print calculate_rankings("10150153748568313")
