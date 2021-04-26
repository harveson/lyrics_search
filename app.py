from flask import Flask, render_template, request, redirect, url_for
from elasticsearch import Elasticsearch
from indexer import *

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
@app.route('/reload_index', methods=['GET'])
def reload_index():
    build_index()
    return render_template('index.htm')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.htm')

@app.route('/index_query', methods=['POST'])
def index_query():
    if request.form['querytext'] == '':
        return render_template('error.html', text=request.form['querytext'])
    try:
        query_data = request.form['querytext']
        res = query_index(query_data)
    except Exception as e:
        return render_template('error.html', text=request.form['querytext'])
    if not res or len(res) == 0:
        return render_template('error.html', text=request.form['querytext'])
    rtn = res[:min(50, len(res))]
    return render_template('serp.htm', text=rtn, query=request.form['querytext'])

