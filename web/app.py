from flask import Flask, jsonify, abort,render_template, Response
from flask.ext.pymongo import PyMongo


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'bizdev'

mongo = PyMongo(app)

def renderTemplate(contents=None,title="",referrer=None):
	return render_template("index.html",title=title,content=contents,referrer=referrer)

def renderAmazonCategories():
	categories = uniqueAmazonCategories()
	return render_template("amazon.html",categories=categories)

@app.route("/")
def index():
	return renderTemplate(contents="<h3>Select a Site to view its sellers.</h3>",title="Home")

@app.route("/amazon")
def amazon():
	categories = renderAmazonCategories()
	contents = categories
	return renderTemplate(contents=contents,title="Amazon",referrer="amazon")

@app.route("/amazon/sellers/<int:category>")
def amazonSellers(category):
	if category is 0:
		abort(400)
	
	cats = mongo.db.amazon_sellers.find({"category_id":category}).sort("number_or_products",-1)
	out = []
	title = None
	for cat in cats:
		if title is None:
			title = cat["category_name"]
		
		out.append({"name":cat["seller_name"],"number_of_products":cat["number_or_products"],"seller_id":cat["seller_id"]})

	categories = renderAmazonCategories()
	template = render_template("seller_table.html",sellers=out,title=title)	
	contents = categories + template
	return renderTemplate(contents=contents, title=title,referrer="amazon")

@app.route("/amazon/download/sellers")
def amazonDownload():
	sellers = mongo.db.amazon_sellers.find()
	group = {}

	for seller in sellers:
		seller_id = seller["seller_id"]
		if seller_id not in group.keys():
			temp = {"seller_id":seller_id,"number_of_products":0,"seller_name":seller["seller_name"],"categories":[],"url":"http://www.amazon.com/gp/aag/details/ref=aag_m_ss?ie=UTF8&asin=&isAmazonFulfilled=&isCBA=&marketplaceID=ATVPDKIKX0DER&seller={0}#aag_detailsAbout".format(seller_id)}
			group[seller_id] = temp

		group[seller_id]["categories"].append(seller["category_name"])
		group[seller_id]["number_of_products"] += seller["number_or_products"]

	out = []
	for key, value in group.iteritems():
		out.append(value)

	out = sorted(out,key=lambda seller:seller["number_of_products"],reverse=True)

	contents = []
	contents.append("STORE\tNUMBER_OF_PRODUCTS\tSTORE_URL\tCATEGORIES")
	for o in out:
		name = o["seller_name"].encode('utf-8')
		products = o["number_of_products"]
		link = o["url"]
		categories = ", ".join(o["categories"]).encode('utf-8')
		contents.append("{0}\t{1}\t{2}\t{3}".format(name,products,link,categories))

	amzn_content = "\n".join(contents)
	return Response(amzn_content, mimetype="text/plain", headers={"Content-Disposition":"attachment;filename=amazon.tsv"})


@app.route("/etsy")
def etsy():
	return etsyPage(0)

@app.route("/etsy/page/<int:page>")
def etsyPage(page=0):
	skip = page*20
	sellers = mongo.db.etsy_sellers.find(skip=skip).sort("number_of_products",-1).limit(20)

	out = []
	for seller in sellers:
		name = seller["seller_name"]
		owner = seller["owner"]
		products = seller["number_of_products"]
		link = seller["url"]
		out.append({"name":name,"number_of_products":products,"url":link,"owner":owner})

	has_more = len(out) == 20
	contents = render_template("etsy.html",title="Etsy Sellers",sellers=out,current_page=page,has_more=has_more)
	return renderTemplate(contents=contents,title="Etsy",referrer="etsy")

@app.route("/etsy/download/sellers")
def etsyDownloadSellers():
	sellers = mongo.db.etsy_sellers.find().sort("number_of_products",-1)
	out = []
	out.append("STORE\tOWNER\tNUMBER_OF_PRODUCTS\tSTORE_URL\tOWNER_URL")
	for seller in sellers:
		name = seller["seller_name"].encode('utf-8')
		owner = seller["owner"].encode('utf-8')
		products = seller["number_of_products"]
		link = seller["url"]
		out.append("{0}\t{1}\t{2}\thttp://www.etsy.com/shop/{3}\t{4}".format(name,owner,products,name,link))

	etsy_content = "\n".join(out)
	return Response(etsy_content, mimetype="text/plain", headers={"Content-Disposition":"attachment;filename=etsy.tsv"})


def uniqueAmazonCategories():
	blacklist = ["Appstore for Android"," Kindle Fire Tablets"," Kindle E-readers","MP3s & Cloud Player","Books & Audible","Unlimited Instant Videos"]
	cats = mongo.db.amazon_categories.find()
       	out = {}
	for cat in cats:
		name = cat['parent_category']
		node = cat['node_id']
		category = cat['category']
		if name in blacklist:
			continue;
		if name not in out.keys():
			out[name] = {"parent":name,"subcategories":[]}
		
		subcats = out[name]["subcategories"]
		subcats.append({"id":node,"name":category})
		out[name]["subcategories"] = subcats
	
	dictlist = []
	for key, value in out.iteritems():
		subcats = value["subcategories"]
		subcats = sorted(subcats, key=lambda category:category["name"])
		value["subcategories"] = subcats
    		dictlist.append(value)
	
	dictlist = sorted(dictlist, key=lambda category:category["parent"])
	return dictlist

if  __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=3031)

