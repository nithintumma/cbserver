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


client = MongoClient()
db = client.data
dif_collection = db.difs
dif_matrix = {}
for dif in dif_collection.find():
	dif_matrix[(str(dif["product1"]),  str(dif["product2"]))] = (dif["dif"], dif["freq"])  
pickle.dump(dif_matrix, open("dumps/difs.p", "wb"))		
