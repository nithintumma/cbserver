# process_productss.py Processes products in queu 
from django.core.management.base import BaseCommand, CommandError
import string
import random
import mimetypes
import math

from pymongo import MongoClient
from pymongo import DESCENDING

import pymongo as pm

from bson.objectid import ObjectId
import time

class Command(BaseCommand):

	def handle(self, *args, **options):
		client = MongoClient()
		db = client.data
		answer_queue = db.answer_queue
		rec_collection = db.recs
		dif_collection = db.difs
		products_to_process = db.toprocess
		calc_recs = db.calcrecs
		product_collection = db.processedproducts
		users_to_update_collection = db.users_to_update

		product_records = products_to_process.find()
		for product_r in product_records:
			start = time.time()
			user_id = product_r["userId"]
			product_id = product_r["product"]
			
			# set up user queue
			user = users_to_update_collection.find_one({"user_id": user_id})
			if (not user):
				users_to_update_collection.insert({"user_id": user_id})
			
			user_rec = rec_collection.find_one({"userId": user_id})
			if (not user_rec):
				self.stdout.write("Not a user_rec")
				continue 

			for product, rating in user_rec.iteritems():
				if (not (product == "userId" or product == "_id" or product == product_id)):
					product_1 = product_id
					product_2 = product
					if (int(product_id) > int(product)):
						product_1 = product
						product_2 = product_id
					dif = user_rec[str(product_1)] - user_rec[str(product_2)]
					dif_collection.update({"product1": product_1, "product2": product_2}, {"$inc": {"freq": 1, "dif": dif}}, True)
			products_to_process.remove({"_id": ObjectId(product_r["_id"])})	
			end = time.time()
			elapsed = end - start
			self.stdout.write(str(elapsed))
		
