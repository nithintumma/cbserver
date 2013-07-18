import string
import random
import math
import time
from pymongo import MongoClient
from pymongo import DESCENDING
import pymongo as pm
from bson.objectid import ObjectId
import cPickle as pickle
import numpy as np
import statsmodels.api as sm


client = MongoClient()
db = client.data

answer_queue = db.answer_queue
rec_collection = db.recs
dif_collection = db.difs
products_to_process = db.toprocess
calc_recs = db.calcrecs
user_collection = db.users_to_update
product_collection = db.processedproducts
to_recommend = db.products_to_rec
model_rankings = db.calc_model_rankings

DUMP_PRODUCTS = "dumps/product_attributes.p"
DUMP_ATTR = "dumps/attributes.p"

	

def calculate_rankings(user_id):
	
	product_attributes = pickle.load(open(DUMP_PRODUCTS, "rb"))
	attribute_list = pickle.load(open(DUMP_ATTR, "rb"))
	print attribute_list
	
	user_rec = rec_collection.find_one({"userId": user_id})
	if (not user_rec):
		return False
	
	rec_list = []
	rated_product_attributes = []
	for product, rec in user_rec.iteritems():
		try:
			rated_product_attributes.append(product_attributes[str(product)])
			rec_list.append(rec)
		except:
			continue
	X = np.array(rated_product_attributes)
	y = np.array(rec_list)
	y -= y.mean()
	X = sm.add_constant(X, prepend=False)
	print  X
	print  y

	model = sm.OLS(y, X).fit()
	coeffs = model.params	
	
	to_update = {}
	for rec_attr in to_recommend.find():
		rec = rec_attr["rec"]
		attributes = rec_attr["attributes"]
		scores = []
		for attr in attribute_list:
			try:
				scores.append(attributes[attr])
			except:
				scores.append(0.0)
		scores.append(1.0)
		scores = np.array(scores)
		print scores 
		print coeffs
		to_update[str(rec)] = float(coeffs.dot(scores))
	
	model_rankings.update({"userId": user_id}, {"$set": to_update}, True)
	return to_update

print calculate_rankings("48947135361")
