#!/usr/bin/python

import string
import random
import mimetypes
import math
import time
from pymongo import MongoClient
from pymongo import DESCENDING
import cPickle as pickle
import pymongo as pm

from bson.objectid import ObjectId
from sets import Set

client = MongoClient()
db = client.data
recommendation_attributes_collection = db.products_to_rec
r_attribute_list = list(recommendation_attributes_collection.find())

# read in unique attributes
unique_attributes = pickle.load(open("attributes.p", "rb"))

# format the recommendation dictionary for this shit 
recommendation_attributes_dict = {}
for r_attribute in recommendation_attribute_list:
	rec = r_attribute["rec"]
	attributes = r_attribute["attributes"]
	to_add = []
	for attr in unique_attributes:
		try:
			to_add.append(attributes[attr])
		except:
			to_add.append(0)
	recommendation_attributes_dict[product] = to_add
pickle.dump(recommendation_attributes_dict, open("dumps/recommendation_attributes.p", "wb"))
