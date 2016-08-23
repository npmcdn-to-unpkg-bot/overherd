from settings import *
import Samsara as nyt_arts

import requests
import json

NYTIMES_COMMENTS_API = "http://api.nytimes.com/svc/community/v3/user-content/url.json"

# each comment may have replies, be careful for that
def get_nytimes_comments_for_article(url):
	url_params = {"api-key": NYT_API_KEY, "url": url, "sort": "newest", "offset": 0}
	r = requests.get(NYTIMES_COMMENTS_API, params=url_params)
	first_page_json = json.loads(r.text)['results']

	comments = []
	comments = comments + (first_page_json['comments'])

	num_total_comments = first_page_json['totalCommentsFound']
	for i in range(25, num_total_comments, 25):
		url_params['offset'] = i
		r = requests.get(NYTIMES_COMMENTS_API, params=url_params)
		curr_page_json = json.loads(r.text)['results']
		comments = comments + curr_page_json['comments']
	
	all_ids = [ comm['commentID'] for comm in comments ] 
	unique_comments = [ comments[ all_ids.index(_id) ] for _id in set(all_ids) ]
	return comments

# returns something like {url => {article_url: []}}
def get_nytimes_comments(keyword, begin_date, end_date):
	# get articles first
	nytimes_article_getter = nyt_arts.Samsara() 
	articles = nytimes_article_getter.search(keyword, begin_date, end_date) 

	# then get comments
	comments = {}
	for article_json in articles:
		article_url = article_json['web_url']
		comments[article_url] = get_nytimes_comments_for_article(article_url)

	return comments

if __name__ == "__main__":
	# comments = get_nytimes_comments("virginia", "20150827", "20150827")
	get_nytimes_comments_for_article("http://opinionator.blogs.nytimes.com/2012/04/17/whos-afraid-of-greater-luxembourg/")