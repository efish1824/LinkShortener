from flask import Flask, render_template, request, abort, redirect
import hashlib, json, random, validators, requests
bad = [400, 404, 410, 419, 423, 451]
app = Flask(__name__)
@app.route('/', methods = ['GET'])
def index():
	return render_template('index.html', status='')
@app.route('/newLink', methods = ['GET', 'POST'])
def newLink():
	if request.method == 'GET':
		abort(404)
	link = request.form.get('link')
	if not validators.url(link):
		return render_template('index.html', status='Invalid link (include http or https)')
	try:
		if requests.get(link, timeout = 10).status_code in bad:
			return render_template('index.html', status="This link does not exist.")
	except requests.exceptions.ConnectionError:
		return render_template('index.html', status="This link does not exist")
	except requests.exceptions.ReadTimeout:
		return render_template('index.html', status = "Link has timed out")
	with open('links.json', 'r+') as links:
		data = json.load(links)
		if link in data.values():
			endoff = list(data.keys())[list(data.values()).index(link)]
			return render_template('index.html', status='This link has already been created. It is: https://LinkShortener.efish.repl.co/' + endoff)
		linkTemp = hashlib.sha256(link.encode('utf-8')).hexdigest()
		print(linkTemp)
		r = random.randint(0, len(linkTemp)-8)
		linkNew = linkTemp[r:r+7]
		while linkNew in data.keys():
			linkNew = linkTemp[r+1:r+8]
			if not linkNew:
				return render_template('index.html', status="Error: Please try again")
		data[linkNew] = link
		links.seek(0)
		json.dump(data, links, indent=2)
		links.truncate()
		return render_template('index.html', status='Link created! Your link is: https://LinkShortener.efish.repl.co/'+linkNew)
@app.route('/<goto>', methods = ['GET'])
def link(goto):
	if not goto:
		abort(404)
	with open('links.json', 'r+') as links:
		data = json.load(links)
		if goto not in data.keys():
			abort(404)
		linkNew = data[goto]
		return redirect(linkNew)
@app.errorhandler(404)
def notfound(err):
	return render_template('404.html')
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
