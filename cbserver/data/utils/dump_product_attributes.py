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
product_attributes_collection = db.product_attributes

p_attribute_list = list(product_attributes_collection.find())
print p_attribute_list

unique_attributes = Set([])
for p_attribute in p_attribute_list:
	for attr in p_attribute["attributes"]:
		unique_attributes.add(attr)
unique_attributes = list(unique_attributes)
pickle.dump(unique_attributes, open("dumps/attributes.p", "wb"))

product_attributes_dict = {}
for product_attribute in p_attribute_list:
	print product_attribute
	product = product_attribute["product"]
	attributes = product_attribute["attributes"]
	to_add = []
	for attr in unique_attributes:
		try:
			to_add.append(attributes[attr])
		except:
			to_add.append(0)
	product_attributes_dict[product] = to_add
pickle.dump(product_attributes_dict, open("dumps/product_attributes.p", "wb"))
