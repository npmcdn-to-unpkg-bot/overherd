import Samsara as nyt_arts
import nytimes_comment_scraper as nyt_coms
import pdb

# returns something like {url => {article_url: []}}
def get_nytimes_comments(keyword, begin_date, end_date):
	nytimes_article_getter = nyt_arts.Samsara() 
	articles = nytimes_article_getter.search(keyword, begin_date, end_date) 
	comments = {}
	for article_json in articles:
		article_url = article_json['web_url']
		comments[article_url] = nyt_coms.nytimes_comments(article_url)

	return comments

if __name__ == "__main__":
	comments = get_nytimes_comments("virginia", "20150827", "20150827")
	# pdb.set_trace()