import requests, bs4
import sys, os, subprocess
import tempfile
from termcolor import *
from urllib.parse import quote
from time import sleep

BASE_URL = "http://www.allitebooks.com/"

def send_request(url):
	try:
		r = requests.get(url)
		r.raise_for_status()
		return r
	except requests.exceptions.ConnectionError:
		cprint("Connection Error Occurred", 'red')
	except requests.exceptions.HTTPError:
		cprint(str(r.status_code) + ' Error', 'red')

def download_and_save_pdf(title_h2):
	title_text = title_h2.find('a').text
	cprint('Downloading ' + title_text, 'green')
	anchor = title_h2.find('a')['href']
	r = send_request(anchor)
	soup = bs4.BeautifulSoup(r.text, 'html.parser')
	dwnld_link = soup.find_all('span', {'class': 'download-links'})[0].find('a')['href']
	r = send_request(dwnld_link)
	f = open(title_text + '.pdf', 'wb')
	f.write(r.content)
	f.close()
	cprint('File %s has been saved in the current directory' % (title_text + '.pdf'), 'green')

def view_thumbnail(filepath):
	cprint('Opening thumbnail..', 'yellow')
	cprint('The thumbnail will be deleted automatically', 'blue')
	if sys.platform.startswith('darwin'):
		subprocess.call(('open', filepath))
	elif os.name == 'nt':
		os.startfile(filepath)
	elif os.name == 'posix':
		subprocess.call(('xdg-open', filepath))
	sleep(1) # So that the application gets time to launch and load the temp photo before the code exectus further and deletes it

def save_thumbnail(article):
	thumb = article.find('div', attrs={'class': 'entry-thumbnail'})
	src = thumb.find('img')['src']
	suffix = '.' + src.split('.')[-1]
	temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
	try:
		r = send_request(src)
		temp.write(r.content)
		temp.close()
	except:
		cprint('Sorry, error occurred while saving thumbnail', 'red')
		os.remove(temp.name)
	return temp.name # filepath

def catalogue(soup):
	main = soup.find('main', attrs={'id': 'main-content'})
	articles = main.find_all('article')
	books = []
	for article in articles:
		title = article.find('h2', attrs={'class': 'entry-title'})
		authors = article.find('h5', attrs={'class': 'entry-author'})
		description = article.select('div.entry-summary > p')[0]
		print('\n')
		cprint(title.find('a').text, 'cyan')
		cprint('By: ' + ', '.join([a.text for a in authors.find_all('a')]), 'yellow')
		cprint(description.text, 'magenta')
		
		inp = input('Save this PDF? (To view its thumbnail photo, enter \'p\') (y/n/p):  ').lower()
		if inp.startswith('y'):
			download_and_save_pdf(title)
			exit(0)
		elif inp.startswith('p'):
			filepath = save_thumbnail(article)
			try:
				view_thumbnail(filepath)
			finally:
				os.remove(filepath)
			inp = input('Save this PDF? (y/n): ').lower()
			if inp.startswith('y'):
				download_and_save_pdf(title)
				exit(0)
		
		info = {'title': title, 'authors': authors, 'description': description}
		books.append(info)

def paginate(page_soup, query):
	paginator = page_soup.find('div', {'class': 'pagination'})
	last_page_number = 1
	if paginator:
		page_range = paginator.find('span', {'class': 'pages'}).get_text()
		last_page_number = int(page_range.split('/')[-1].strip()[0])
	for i in range(last_page_number):
		if i != 0: # Because the soup for the first page is passed in
			cprint('\nRetrieving Page No. %s' % str(i+1), 'blue')
			url = BASE_URL + ('page/%s/?s=' % str(i+1)) + query
			print(url)
			r = send_request(url)
			page_soup = bs4.BeautifulSoup(r.text, 'html.parser')
		catalogue(page_soup)
	cprint('Sorry, couldn\'t find a relevant book', 'red')

if __name__ == '__main__':
	query = quote(input('Enter Search Query: '), safe='')
	url = BASE_URL + '?s=' + query
	r = send_request(url)
	soup = bs4.BeautifulSoup(r.text, 'html.parser')
	paginate(soup, query)
