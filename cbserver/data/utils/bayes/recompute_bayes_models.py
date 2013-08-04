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
from sklearn.naive_bayes import GaussianNB
from scipy import sparse
from cluster import get_feature_weights, get_feature_means
from sklearn.svm import LinearSVC

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

# get the best possible model for the user 
def determine_model(user_id):
	user = user_collection.find_one({"user_id": user_id})
	if user:
		# if we have enough data about the user
		if user["answer_count"] > 100:
			return "personal"

		# get the best model for the user 
		try:
			model = user["personality_model"]
		except:
			model = user["models"][0]
	
		# deal with user that has been reclassified to none
		if model != "none":
			return model
		else:
			return user["models"][0]

# for a given model return the top classified recommendations 
def get_rankings(model_name):
	model = models.find_one({"model_name": model_name})	
	if model:
		# we have a model
		recs = nb_models_recommendations.find_one({"model_name": model_name})
		if recs:		
			return recs["good_recs"]
		else:
			# had no data for the given model
			return []		
	else:
		# we don't have the requested model 
		return []


"""
Input length: returns a discrete list to represent classifications. Currently returns 1, 2, 3
based on percentile (i.e. top 25% are 1, top 50% are 2, bottom 50% are 3
"""
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
Input model name: returns void
Recomputes the Naive Bayes classifier for the given model based on the model's preference vector
e.g. input "global": 
reclassifies each recommendation for the global model based on the preference vector
"""
def recompute_model(model_name):
	def inner_map(x):
		if x == 0:
			return 3
		else:
			return x

	def map_replace(x_list):
		return map(inner_map, x_list)

	print "In recompute model"
	model = models.find_one({"model": model_name})
	if model:
		"""
		Schema is: {<model_name>, <product_id>: <rec_score> }
		"""

		print "Current model: "  
		print model

		# we need to recompute the model
		product_attributes = pickle.load(open(DUMP_PRODUCTS, "rb"))
		attribute_list = pickle.load(open(DUMP_ATTR, "rb"))
		recommendation_attributes = pickle.load(open(DUMP_RECOMMENDATIONS_ATTR,"rb"))
		model_scores = model["scores"]
		
		# list of ratings
		scores_list = []
		rated_product_attributes = []
		error_count = 0
		for product, score in model_scores.iteritems():
			#  <product_id>: <score>
			try:
				rating = map(inner_map, product_attributes[str(product)])
				print "Success: "
				print product
				rated_product_attributes.append(rating)
				scores_list.append([score])
			except:
				error_count +=1
				# error occurs if product is not in pickle dump of rated_product
				print "Error finding product attributes"
				print product
				continue
		print error_count
		print len(scores_list)
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
		print "Ratings"
		print ratings
		mnb = GaussianNB()
		mnb.fit(X, ratings)
		
		# get factors to cluster with 
		lcv = LinearSVC(dual=False)
		lcv.fit(X, ratings)
		coefs = lcv.coef_.tolist()[2]

		a_coefs = np.abs(np.array(coefs))	
		norm_coefs = a_coefs/np.mean(a_coefs)

		mean_list = get_feature_means(model_scores)
		
		recommendations = recommendation_attributes.keys()
		pre_proc =  [recommendation_attributes[rec] for rec in recommendations]
		print "Pre proc"
		print pre_proc
		test_data_list = map(map_replace, pre_proc)
		print test_data_list
		test_data = np.array(test_data_list)
		classification = mnb.predict(test_data).tolist()		
		print classification
		print "Getting params: "
		print mnb.get_params(True)
		print mnb.theta_
		print mnb.sigma_
		print mnb.class_prior_
		good_recs = []
		average_recs = []
		for i in range(len(classification)):
			if classification[i] == 3:
				good_recs.append(recommendations[i])
			elif classification[i] == 2:
				average_recs.append(recommendations[i])
			else:
				print recommendations[i]
		print "Good recs: " 
		print good_recs
		print "Average recs: " 
		print average_recs

		#empirical_log = mnb.coef_.flatten().tolist()
		empirical_log = [1, 2, 3]
		# update model with values 
		models.update({"_id": ObjectId(model["_id"])}, 
					{"$set": {"feature_means": mean_list,
						"feature_weights": norm_coefs.tolist(),
						"good_recs": good_recs,
						"average_recs": average_recs}})		

recompute_model("party_hardy")	
