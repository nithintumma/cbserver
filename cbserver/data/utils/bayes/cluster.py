import string
import random
import math
import time
from pymongo import MongoClient
from pymongo import DESCENDING
from bson.objectid import ObjectId
import cPickle as pickle
import numpy as np
from sklearn.svm import LinearSVC
from scipy.spatial.distance import euclidean 
import operator

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
models = db.models
nb_models_recommendations = db.nb_calculated_recs


DUMP_PRODUCTS = "/home/ubuntu/srv/cbserver/data/utils/dumps/product_attributes.p"
DUMP_ATTR =  "/home/ubuntu/srv/cbserver/data/utils/dumps/attributes.p"
DUMP_RECOMMENDATIONS_ATTR = "/home/ubuntu/srv/cbserver/data/utils/dumps/recommendation_attributes.p"

PERSONALITIES = ["artsy", "party_hardy"]
THRESHOLD = 100.0

#LOAD IN THE FILES ONCE
product_attributes = pickle.load(open(DUMP_PRODUCTS, "rb"))
attribute_list = pickle.load(open(DUMP_ATTR, "rb"))

def discreteClasses(length):
	good_index = int(length*0.75)
	average_index = int(length*0.50)
	ratings = []
	for i in range(length):
		if i >= good_index:
			ratings.append(3)
		elif i >= average_index:
			ratings.append(2)
		else:
			ratings.append(1)	
	return ratings

"""
Given a product, returns the attributes for which that product is rated 
"""
def get_attributes(product):
	try:
		attr_scores = product_attributes[product]
	except:
		print "Error with product: " + product
		return []
	attributes = []
	i = 0
	for attr in attribute_list:
		score = attr_scores[i]
		if (not score == 0):
			attributes.append(attr)	
		i+=1
	return attributes

def get_feature_weights(scores):
	def inner_map(x):
		if x == 0:
			return 3
		else:
			return x

	def map_replace(x_list):
		return map(inner_map, x_list)

	
	# list of ratings
	scores_list = []
	rated_product_attributes = []
	for product, score in scores.iteritems():
		#  <product_id>: <score>
		try:
			rating = map(inner_map, product_attributes[str(product)])
			rated_product_attributes.append(rating)
			scores_list.append([score])
		except:
			# error occurs if product is not in pickle dump of rated_product
			print "Error finding product attributes"
			print product
			continue

	# matrix, rated products X attributes 
	X = np.array(rated_product_attributes)
	
	# vector, includes all of the scores  
	y = np.array(scores_list)
	Total = np.append(X, y, 1)
	num_products, num_attributes = Total.shape	
	SortedTotal = Total[Total[:,(num_attributes - 1)].argsort()]
	print SortedTotal
	X = SortedTotal[:, :-1]
	
	ratings = discreteClasses(num_products)

	lcv = LinearSVC(dual=False)
	lcv.fit(X, ratings)
	print lcv.classes_
	# coefficients in order of attribute list for good recs predictor
	return lcv.coef_.tolist()[2]

"""
small util function
"""
def get_index(attribute):
	return attribute_list.index(unicode(attribute))


def get_feature_means(scores):
	sums = {}
	for product, score in scores.iteritems():
		if score > 1600:
			# find the relevant attributes
			attributes = get_attributes(product)
			for attr in attributes:
				try:
					sums[attr][0] += product_attributes[product][get_index(attr)] 
					sums[attr][1] += 1
				except KeyError:
					# first time attribute has appeared 
					print "Error with product: " + product
					sums[attr] = [product_attributes[product][get_index(attr)], 1]
	
	means = {}
	for attr, sum_tuple in sums.iteritems():
		means[attr] = float(sum_tuple[0]) / float(sum_tuple[1])
	print means
		
	# get the ordering of the attributes
	mean_list = []
	for attr in attribute_list:
		try:
			mean = means[attr]
		except KeyError:
			mean = 3
		mean_list.append(mean)
	print "Mean list"
	print mean_list
	return mean_list

# for a given user, put them in the closests 
def cluster_user(user_id):
	
	rec = rec_collection.find_one({"userId": user_id})
	scores = rec["scores"]
	
	mean_list = get_feature_means(scores)
	coefs = get_feature_weights(scores)	
	print "Coefs"
	print coefs

	# CLUSTER
	# scale the coefficients 
	a_coefs = np.abs(np.array(coefs))	
	norm_coefs = a_coefs/np.mean(a_coefs)
	print norm_coefs

	scaled_means = np.array(mean_list) * norm_coefs
	
	# now we must cluster against all of the models to find the best one
	for model in models.find():
		name = model["model"]
		if name in PERSONALITIES:
			scaled_model_features = np.array(model["feature_means"]) * np.array(model["feature_weights"])
			dist = euclidean(scaled_model_features, scaled_means)
			distances[name] = dist
	
	sorted_distances = sorted(distances.iteritems(), key=operator.itemgetter(1))	
	user = user_collection.find_one({"user_id": user_id})
	if sorted_distances[0][1] < THRESHOLD:
		user_collection.update({"_id": ObjectId(user["_id"])}, 
					{"$set": {"models": [sorted_distances[0][0], "global"], "feature_means": mean_list, "feature_weights": norm_coefs.tolist()}})	
	else:
		# too far away from nearest cluster, don't use personality
		user_collection.update({"_id": ObjectId(user["_id"])}, {"$set": {"models": ["global"], "feature_means": mean_list, "feature_weights": norm_coefs.tolist()}})	

	return True

					
# general clustering of all users
def cluster():
	return False
	
if __name__ == "__main__":
	print "About to cluster user"
	cluster_user("551733910")
