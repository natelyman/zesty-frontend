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
amznsellers = db.amazon_sellers

cats = amzncats.find()

for category in cats:
	
	cat = category["node_id"]

	url = "http://www.amazon.com/gp/search/other/?rh=n%3A1055398%2Cn%3A%211063498%2Cn%3A{CAT_ID}&bbn={CAT_ID}&pickerToList=enc-merchantbin&ie=UTF8"

	seller_url = "http://www.amazon.com/gp/aag/details/ref=aag_m_ss?ie=UTF8&asin=&isAmazonFulfilled=&isCBA=&marketplaceID=ATVPDKIKX0DER&seller=A1Q4A7YXTO45KY#aag_detailsAbout";

	req_url = str(re.sub("\{CAT_ID\}",str(cat),url))

	try:

		request = urllib2.Request(req_url)
		request.add_header("User-Agent","Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")

		res = urllib2.urlopen(request);

		content = res.read()

		soup = BeautifulSoup(content)

		test = soup.find_all(attrs={"class":"refList"})

		for t in test:
			sellers = t.find_all("a")

			for seller in sellers:
				try:
					link = seller["href"];

					pos = link.find("%3A",10)
					seller_id = None
					if(pos > 0):
						pos += 3
						seller_id = link[pos:]

					if seller_id is not None:

						span = seller.find_all("span")

						if(len(span) > 1):
							seller_name = span[0].text
							seller_cnt = int(re.sub("[,\(\)]","",span[1].text))


							print "Category: %i Seller: %s Counts: %i ID: %s" % (cat,seller_name,seller_cnt, seller_id)

							amznsellers.insert({"seller_id":seller_id,"category_id":cat,"category_name":category["category"],"seller_name":seller_name,"number_or_products":seller_cnt})
					#print seller
				except Exception:
					print "Problem with Seller"
					print "++++++++++++"
				print "============="
	except Exception:
		print "Problem With this category"
		print "---------------"




