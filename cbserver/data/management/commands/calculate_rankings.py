from django.core.management.base import BaseCommand, CommandError
import string
import random
import mimetypes
import math

from pymongo import MongoClient
from pymongo import DESCENDING

import pymongo as pm

from bson.objectid import ObjectId

# needs a user id
class Command(BaseCommand):
	def handle(self, *args, **options):	
		user_id = "551733910"
		client = MongoClient()
		db = client.data
		answer_queue = db.answer_queue
		rec_collection = db.recs
		dif_collection = db.difs
		products_to_process = db.toprocess
		calc_recs = db.calcrecs
		product_collection = db.processedproducts

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


