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

etsy_sellers = db.etsy_sellers

url = "http://www.etsy.com/search/shops?order=alphabetical&page={0}"

i = 1250

while i <= 99999:
	print "Trying page {0}".format(i)
	req_url = url.format(i)
	request = urllib2.Request(req_url)
	request.add_header("User-Agent","Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")

	res = urllib2.urlopen(request);

	content = res.read()
	soup = BeautifulSoup(content)

	shops = soup.find_all(attrs={"class":"shop"})

	for shop in shops:
		name = shop.find(attrs={"class":"shopname"})
		name = name.find("a").text.strip()
		
		owner = shop.find(attrs={"class":"real-name"})
		owner = owner.find("a")

		owner_url = owner["href"]	
		owner = owner.text

		count = shop.find(attrs={"class":"count-number"});
		count = count.text.strip()

		insert = {"url":owner_url,"owner":owner,"seller_name":name,"number_of_products":count}
		etsy_sellers.insert(insert)
		print owner_url, owner, name, count

	print "Page %s" % str(i)
	print "====================================="


	i = i + 1

