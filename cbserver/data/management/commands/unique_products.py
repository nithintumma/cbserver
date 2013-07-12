from django.core.management import BaseCommand, CommandError
from pymongo import MongoClient
from _process import calculate_elo_rank
import string
import random
import mimetypes
import math

from pymongo import MongoClient
from pymongo import DESCENDING

import pymongo as pm

from bson.objectid import ObjectId

class Command(BaseCommand):
		
	def handle(self, *args, **options):
		
		self.stdout.write("Starting")
		client = MongoClient()
		db = client.data
		answer_queue = db.answer_queue
		rec_collection = db.recs
		products_to_process = db.toprocess
		product_collection = db.processedproducts
		dif_collection = db.difs
		
		# unique products 
		product_list_1 = dif_collection.distinct("product1")
		product_list_2 = dif_collection.distinct("product2")
		products = list(set(product_list_1).union(set(product_list_2)))
		products = [{"product": id} for id in products]
		
		if (len(products) > 0):
			product_collection.remove() 
			product_collection.insert(products)
		
	
