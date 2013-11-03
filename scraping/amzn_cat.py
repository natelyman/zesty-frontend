from bs4 import BeautifulSoup
import urllib2
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

url = "http://www.amazon.com/gp/site-directory/ref=sa_menu_top_fullstore"

request = urllib2.Request(url)
request.add_header("User-Agent","Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")

res = urllib2.urlopen(request);

content = res.read()

soup = BeautifulSoup(content)

cats = soup.find_all(attrs={"class":"popover-grouping"})

for cat in cats:
	h2 = cat.find("h2");
	parent = h2.text

	a = cat.find_all("a")
	for link in a:
		href = link["href"];

		pos = href.find("node")
		if(pos >= 0):
			pos = pos + 5
			node_id = int(href[pos:])
			category = link.text

			print "Parent %s CAT: %s NODE: %i" % (parent,category,node_id)
			amzncats.insert({"node_id":node_id,"category":category,"parent_category":parent})
