import requests
import json
from bs4 import BeautifulSoup
import re
import psycopg2 
from datetime import datetime
# import pdb

try: 
	from db_settings import *
except:
	import os
	DB_ENDPOINT = os.environ['DB_ENDPOINT']
	DB_PORT = int(os.environ['DB_PORT'])
	DB_USERNAME = os.environ['DB_USERNAME']
	DB_PASSWORD = os.environ['DB_PASSWORD']
	DB_DATABASE = os.environ['DB_DATABASE']

YAHOO_NEWS_URLS = ["https://www.yahoo.com/news/"]
YAHOO_COMMENT_SERVICE_URL = 'https://www.yahoo.com/news/_td/api/resource/CommentsService.comments;count=100;publisher=news-en-US;sortBy=highestRated;uuid={}?bkt=Headline-Testing-Control&dev_info=0&device=desktop&intl=us&lang=en-US&partner=none&region=US&site=fp&tz=America%2FLos_Angeles&ver=2.0.1738001&returnMeta=true&offset={}'

def main():
	print "Getting UUIDs... "
	uuids = get_uuids(YAHOO_NEWS_URLS[0])
	print "Getting comments..."
	comments = get_yahoo_comments(uuids)
	print "Uploading to database..."
	upload_comments_to_database(comments)
	print "Completed!"

# take whatever is returned from 
# get_yahoo_comments(uuids) and format for database upload
# then upload to the database
def upload_comments_to_database(comments):
	# prepare comments for database 
	comments_for_database_upload = []
	for uuid in comments:
		article_comments_data = comments[uuid]['comments']['data']
		if "list" in article_comments_data:
			for comment_json in article_comments_data['list']:
				comment_for_upload = {}
				comment_for_upload['yahoo_uuid'] = uuid
				comment_for_upload['article_headline'] = comments[uuid]['article_headline'].replace("'", "''")
				comment_for_upload['article_url'] = comments[uuid]['article_url'].replace("'", "''")
				comment_for_upload['comment_text'] = comment_json['content'].replace("'", "''")
				comment_for_upload['reply_count'] = comment_json['replyCount']
				comment_for_upload['thumbs_up_count'] = comment_json['thumbsUpCount']
				comment_for_upload['thumbs_down_count'] = comment_json['thumbsDownCount']
				comment_for_upload['author'] = comment_json['creator']
				comment_for_upload['comment_id'] = comment_json['selfURI']
				comment_for_upload['created_on'] = datetime.utcfromtimestamp(comment_json['createTime'] / 1000).strftime("%Y%m%d") # unix time in milliseconds
				comments_for_database_upload.append(comment_for_upload)

	# need to do the "insert if" logic
	try:
		conn = psycopg2.connect("dbname='%s' user='%s' host='%s' port='%d' password='%s'" \
		 % (DB_DATABASE, DB_USERNAME, DB_ENDPOINT, DB_PORT, DB_PASSWORD))

	   	cursor = conn.cursor()
	   	print "Connected to database."

		sql_string = u"""
			INSERT INTO yahoo_comments 
			(comment_id,yahoo_uuid,article_headline,article_url,comment_text,reply_count,thumbs_up_count,thumbs_down_count,author,created_on) 
			VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}')"""
		sql_string += "ON CONFLICT (comment_id) DO NOTHING"

		for comment in comments_for_database_upload:
			query = sql_string.format(comment['comment_id'], comment['yahoo_uuid'], comment['article_headline'], comment['article_url'], comment['comment_text'], comment['reply_count'], comment['thumbs_up_count'], comment['thumbs_down_count'], comment['author'], comment['created_on']) 
			print "EXECUTING: " + comment['comment_id']
			cursor.execute(query)

		print "Processed %d comments." % len(comments_for_database_upload)

		# save shit
		cursor.close()
		conn.commit()
		conn.close()
	except:
		print "PROBLEMS CONNECTING TO DATABASE"


# GET COMMENTS FOR ARTICLES
# take in a dictionary of {uuid => {title, url}}
# return dictionary of {uuid => {"article_headline": headline, "url": url, "comments": comment_json}}
def get_yahoo_comments(uuids):
	comments = {}
	for uuid in uuids:
		comments_json = get_yahoo_comments_for_article(uuid)
		if ('data' in comments_json and \
			'list' in comments_json['data']):
			for i, comment in enumerate(comments_json['data']['list']):
				# for whatever reason it's given as an array from Yahoo if it has multiple paragraphs
				comments_json['data']['list'][i]['content'] = "\n".join(comment['content'])

		comments[uuid] = {
			"article_headline": uuids[uuid]['title'], 
			"article_url": uuids[uuid]['url'],
			"comments": comments_json
		}
		
	return comments

def get_yahoo_comments_for_article(uuid):
	first_req = requests.get(YAHOO_COMMENT_SERVICE_URL.format(uuid, 0))
	comment_json = json.loads(first_req.text)

	# go by 100s
	num_comments = comment_json['data']['count']
	if (num_comments):
		end = ((num_comments / 100) + 1) * 100
		for offset in range(100, end, 100):
			req = requests.get(YAHOO_COMMENT_SERVICE_URL.format(uuid, offset))
			next_comment_json = json.loads(req.text)
			comment_json['data']['list'].extend(next_comment_json['data']['list'])

		return comment_json
	else:
		return {}

# GET ARTICLE INFORMATION
def get_uuids(yahoo_link):
	# stream items have their own article id and have 
	# a list of storyline items which have their own article ids
	def get_stream_items(yahoo_json):
		stream_items = yahoo_json['context']['dispatcher']['stores']['StreamStore']['streams']
		stream_items = stream_items[stream_items.keys()[0]]
		stream_items = stream_items['data']['stream_items']
		return stream_items

	pattern = '({"context":.+});'
	r = requests.get(yahoo_link)
	match = re.findall(pattern, r.text)[0]
	yahoo_json = json.loads(match)
	stream_items = get_stream_items(yahoo_json)

	article_uuids = {}

	for stream_item in stream_items:
		if "id" in stream_item:
			article_uuids[stream_item['id']] = {"title": stream_item['title'], "url": stream_item['url']}

		if "storyline" in stream_item:
			for storyline in stream_item['storyline']:
				if "id" in storyline:
					article_uuids[storyline['id']] = {"title": storyline['title'], "url": storyline['url']}

	return article_uuids


if __name__ == "__main__":
	main()
