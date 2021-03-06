# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, request
from firstapp import app
from firstapp.forms import LinkForm
from firstapp.model_stuff.checking_string import do_things
from firstapp.comments_parser import parseinst
import json

import crochet
crochet.setup() 
from firstapp.instspider.spiders.comment_spider import QuotesSpider
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher

ind = 0
output_data = []
crawl_runner = CrawlerRunner()

@app.route('/')
def route():
	return redirect('/home')

@app.route('/home', methods=['GET', 'POST'])
def home():
	return render_template('home.html', title='Home')

@app.route('/go')
def go():
	return redirect('/links')

@app.route('/links', methods=['GET', 'POST'])
def link():
	form = LinkForm()
	if form.validate_on_submit():
		scrape_with_crochet(form.link.data)
		if (len(output_data) == ind) and (output_data[len(output_data)-1] != 'error'):
			answer_tuple = do_things(parseinst(output_data[len(output_data)-1]['idstr']))
			flash('{} of toxic comments'.format(answer_tuple[0]))
			if answer_tuple[1] == 1:
				flash('{} toxic comment'.format(answer_tuple[1]))
			else:
				flash('{} toxic comments'.format(answer_tuple[1]))
			if answer_tuple[2] == 1:
				flash('{} normal comment'.format(answer_tuple[2]))
			else:
				flash('{} normal comments'.format(answer_tuple[2]))
			comments = 'Toxic comments: '
			for comment in answer_tuple[3]:
				comments += '\'' + comment + '\', '
				if len(comments) > 90:
					flash(comments[:-2] + ',')
					comments = ''
			flash(comments[:-2] + '.')
			
			return redirect('/index')
		else:
			flash('Incorrect input!')
			return redirect('/links')
	return render_template('links.html', title='Enter your link', form=form)

@crochet.wait_for(timeout=60.0)
def scrape_with_crochet(link):
    # signal fires when single item is processed
    # and calls _crawler_result to append that item
    global ind
    ind = len(output_data) + 1
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    eventual = crawl_runner.crawl(QuotesSpider, link = link)#'https://www.instagram.com/p/B3rxYQ6IBWL/')
    return eventual  
    
def _crawler_result(item, response, spider):
	#output_data = []
	if len(dict(item)) == 0:
		output_data.append('error')
	else:
		output_data.append(dict(item))
	
@app.route('/index')
def index():

	return render_template('index.html', title='Results')


