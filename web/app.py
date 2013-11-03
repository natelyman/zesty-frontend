from flask import Flask, jsonify, abort,render_template
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
	contents="<h3>Select a Category to view sellers.</h3>"
	categories = renderAmazonCategories()
	contents = contents + categories
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

@app.route("/etsy")
def etsy():
	return "Hi"

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

