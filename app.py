import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

import feelers.nytimes.nytimes_comments as nyt
import feelers.yahoo.yahoo_comments as yahoo

# create 
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/samsara')
def get_all_comments():
	keywords = request.args.get('keywords')
	begin_date = request.args.get('begin_date')
	end_date = request.args.get('end_date')

if __name__ == '__main__':
    app.run(debug=False)
