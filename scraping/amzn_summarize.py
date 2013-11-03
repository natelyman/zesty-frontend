import os
import re
import datetime
from pymongo import MongoClient
config = {}
config["dbname"] = "bizdev"
config["host"] = "localhost"
config["port"] = "27017"

client = MongoClient(config["host"],int(config["port"]))

db = client[config["dbname"]]

amzncats = db.amazon_categories
amznsellers = db.amazon_sellers
amznsummary = db.amazon_summary

all_cats = amzncats.find()

cache = {}

for cat in all_cats:
	parent = cat['parent_category']
	
	if parent not in cache:
		cache[parent] = []


	scats = amznsellers.find({"category_id":cat['node_id']});

	sellers = []
	for scat in scats:
		sellers.append(scat)

	
	cat['sellers'] = sellers


	cache[parent].append(cat)

	amznsummary.insert(cache);
	cache = {}


print cache