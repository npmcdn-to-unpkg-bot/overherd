import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

import feelers.nytimes.nytimes_comments.py as nyt
import feelers.yahoo.yahoo_comments.py as yahoo

# create 
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')