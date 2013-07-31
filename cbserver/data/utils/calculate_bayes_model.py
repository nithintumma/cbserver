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
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB


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
DUMP_RECOMMENDATIONS_ATTR = "dumps/recommendation_attributes.p"

def calculate_rankings(user_id):
	
	product_attributes = pickle.load(open(DUMP_PRODUCTS, "rb"))
	attribute_list = pickle.load(open(DUMP_ATTR, "rb"))
	#recommendation_attributes = pickle.load(open(DUMP_RECOMMENDATIONS_ATTR,"rb"))
	
	user_rec = rec_collection.find_one({"userId": user_id})
	if (not user_rec):
		return False
	
	# list of ratings 	
	rec_list = []
	rated_product_attributes = []
	for product, rec in user_rec.iteritems():
		try:
			rated_product_attributes.append(product_attributes[str(product)])
			rec_list.append([rec])
		except:
			print product
			continue
	
	# matrix, rated products X attributes 
	X = np.array(rated_product_attributes)

	# vector, rated prdoucts X ranking 
	y = np.array(rec_list)
	print X.shape
	print y.shape
	Total = np.append(X, y, 1)
	print Total
	print Total.shape
	num_products, num_attributes = Total.shape	
	SortedTotal = Total[Total[:,(num_attributes - 1)].argsort()]
	print "Sorted: " 
	print SortedTotal
	
	X = SortedTotal[:, :-1]
	print X
	
	# discretize the array
	length = num_products
	good_index = int(length*0.25)
	average_index = int(length*0.50)
	ratings = []
	for i in range(length):
		if i >= good_index:
			ratings.append(3)
		elif i >= average_index:
			ratings.append(2)
		else:
			ratings.append(1)	
	print ratings
	y = np.array(ratings)
	
	mnb = MultinomialNB()
	mnb.fit(X, y)	
	# at this point we will predict the classifications of the recommendation vectors
	
	return "Done"
	# we need to resort the original list of product attributes based on the scores 
	# sort the output ratings
	
	y.sort()
	
	# normalize the ratings vector 
	y -= y.mean()
	X = sm.add_constant(X, prepend=False)

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
	#	scores.append(1.0)
		scores = np.array(scores)
		print scores 
		print coeffs
		to_update[str(rec)] = float(coeffs.dot(scores))
	
	model_rankings.update({"userId": user_id}, {"$set": to_update}, True)
	r_sq = model.rsquared
	to_insert = [(k, v, r_sq) for v, k in sorted([(v, k) for k, v in to_update.items()])]	
	return to_insert

print calculate_rankings("123")
