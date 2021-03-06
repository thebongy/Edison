from bottle import Bottle, route, request, run, get, static_file, post    # Importing Bottle
import json,os

data = {}
instruction = {}

app = Bottle()

@app.route('/')
def home():
	error_paths = []
	file_paths = ['templates','templates/index.html','templates/candidates.html','static','static/js','static/css','static/css/bootstrap.min.css','static/css/jumbotron-narrow.css','static/js/bootstrap.min.js','static/js/poll.js','candidates.json','candidateimages','candidateimages/default.gif']
	for paths in file_paths:
		if os.path.exists(paths):
			print paths + ' .................OK'
		else:
			print paths + '.................. NOT FOUND'
			error_paths.append(paths)
	print '---------------------------'
	if len(error_paths) != 0:
		print 'SOME FILES DO NOT EXIST OR WEREN\'T FOUND:'
		for paths in error_paths:
			print paths
	else:
		print 'ALL FILES WERE FOUND. YOU ARE GOOD TO GO!'
	print '---------------------------'
	return open('templates/index.html').read()

@app.get('/getcandidates')
def getcandidates():
	with open('candidates.json') as json_file:
		json_data = json.load(json_file)
	return json_data

@app.get('/static/css/<filename>')
def returncss(filename):
	return static_file(filename, root='static/css')

@app.get('/static/js/<filename>')
def returnjs(filename):
	return static_file(filename, root='static/js')

@app.get('/static/fonts/<filename>')
def returnfonts(filename):
	return static_file(filename, root='static/fonts')

@app.get('/static/images/<filename>')
def returnimages(filename):
	return static_file(filename, root='static/images')

@app.get('/savedimages/<filename>')
def returncimages(filename):
	return static_file(filename, root='savedimages')

@app.get('/customize')
def candidate():
	return open('templates/candidates.html').read()

@app.get('/elections')
def elections():
	return open('templates/elections.html').read()

@app.post('/uploadimage')
def uploadimage():
	image = request.files.get('file')
	name, ext = os.path.splitext(image.filename)
	if ext not in ('.png','.jpg','.jpeg','.gif'):
		return 'File extension not allowed.'
	save_path = 'savedimages/'
	full_path = '/savedimages/' + str(image.filename)
	new_name = os.path.join(save_path,name + ext)
	if os.path.exists(new_name):
		i = 1
		while True:
			new_name = os.path.join(save_path,name + "_" + str(i) + ext)
			if os.path.exists(new_name):
				i += 1
			else:
				break
	image.save(new_name)
	return "/" + new_name

def delete_image(img_path):
	try:
		os.remove(img_path[1:])
	except OSError:
		print "File for deletion wasn't found. Ignoring deletion"

@app.post('/candidateAction')
def candidateAction():
	instruction = request.json
	
	with open('candidates.json', 'r') as data_file:
		action = instruction['action']
		pollIndex = instruction['pollIndex']
		candidateIndex = instruction['candidateIndex']
		
		try:
			update = instruction['update']
			value = instruction['value']
		except KeyError:
			pass
		
		data = json.load(data_file)
		
		if action == 'delete':
			delete_image(data['polls'][pollIndex]['candidates'][candidateIndex]['image'])
			del data['polls'][pollIndex]['candidates'][candidateIndex]
				
		elif action == 'update':
			data['polls'][pollIndex]['candidates'][candidateIndex][update] = value
		
	with open('candidates.json', 'w') as data_file:
		data_file.write(json.dumps(data))

@app.post('/pollAction')
def pollAction():
	instruction = request.json
	
	with open('candidates.json', 'r') as data_file:
		action = instruction['action']
		
		try:
			pollIndex = instruction['pollIndex']
		except KeyError:
			pass
		
		try:
			value = instruction['value']
			update = instruction['update']
		except KeyError:
			pass
		
		data = json.load(data_file)
		
		if action == 'createCandidate':
			data['polls'][pollIndex]['candidates'].append(value)
			
		elif action == 'update':
			data['polls'][pollIndex][update] = value
			
		elif action == 'delete':
			for candidate in data['polls'][pollIndex]['candidates']:
				delete_image(candidate['image'])
			del data['polls'][pollIndex]
		
		elif action == 'create':
			data['polls'].append(value)
	
	with open('candidates.json', 'w') as data_file:
		data_file.write(json.dumps(data))

@app.post('/electionAction')
def electionAction():
	instruction = request.json
	
	with open('candidates.json', 'r') as data_file:
		try:
			update = instruction['update']
			value = instruction['value']
		except KeyError:
			pass
		
		data = json.load(data_file)
		data[update] = value
		
	with open('candidates.json', 'w') as data_file:
		data_file.write(json.dumps(data))

@app.post('/resetVotes')
def resetVotes():
	with open('candidates.json','r') as data_file:
		data = json.load(data_file)
		for poll in data['polls']:
			poll['ended'] = False
			for candidate in poll['candidates']:
				candidate['votes'] = 0
	
	with open('candidates.json', 'w') as data_file:
		data_file.write(json.dumps(data))

@app.post('/exit')
def exit():
	data = {}
	candidateIndex = 0
	pollIndex = 0
	
	with open('candidates.json', 'r') as data_file:
		data = json.load(data_file)
	
	while pollIndex < len(data['polls']):
		if data['polls'][pollIndex]['name'] == '':
			del data['polls'][pollIndex]
		pollIndex += 1
		
	for pollIndex in range(len(data['polls'])):
		while candidateIndex < len(data['polls'][pollIndex]['candidates']):
			if data['polls'][pollIndex]['candidates'][candidateIndex]['name'] == '':
				del data['polls'][pollIndex]['candidates'][candidateIndex]
			candidateIndex += 1
	
	with open('candidates.json', 'w') as data_file:
		data_file.write(json.dumps(data))


run(app, host='localhost', port=8080)