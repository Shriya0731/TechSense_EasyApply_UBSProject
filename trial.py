from flask import Flask, redirect, url_for, request

app = Flask(__name__)


@app.route('/success/<name>')
def success(name):
	return 'welcome %s' % name


@app.route('/login', methods=['GET'])
def login():
	if request.method == 'POST':
		user = request.form['nm']
		return 'Welcome'
	else:
		user = request.args.get('nm')
		return 'Welcome shriya'


if __name__ == '__main__':
	app.run(debug=True)
