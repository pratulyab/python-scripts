"""
	This script searches the IMDB for a query to retrieve its rating.
	Also, I needed to update my movies' folders with their respective rating, for readability and classification.
	Generally, downloaded movies have weird names with them. Thus, the folder name is set to be overwrited by the imdb title.
	Eg. MovieFoo.720p.kjaf.asdfkj
	=>  7.2 MovieFoo (2008)
"""

import os, sys, shutil
import requests, bs4
import colorama
from termcolor import *

colorama.init()

def getRelevantURL(title):
	print('Searching for', ' ')
	cprint(title,'yellow')
	title = title.strip().lower()
	title = requests.utils.quote(title, safe=' ')
	title = title.replace(' ', '+')
	base_url = 'http://www.imdb.com'
	url = base_url + '/find?q=' + title
	#cprint("Searching At %s" % url, "yellow")
	try:
		headers = {'Accept-Language': 'en-US,en;q=0.8'} # To get the english title for foreign movies!
		r = requests.get(url, headers=headers)
	except:
		cprint('Error making request. Check internet connection.', 'red')
		exit()
	soup = bs4.BeautifulSoup(r.text, "html.parser")
	if soup.find_all('div', {'class': 'findNoResults'}):
		cprint('No results found.', 'red')
		return ''
	title_container = ''
	div_findSection = soup.find_all('div', {'class': 'findSection'})
	for chunk in div_findSection:
		if chunk.find('h3', {'class', 'findSectionHeader'}).text == 'Titles':
			title_container = chunk
			break
	if not title_container:
		cprint('No title results found.', 'red')
		return ''
	title_list = title_container.find('table', {'class': 'findList'}).find_all('tr', {'class': 'findResult'})[:5] # Restricting To Top 5 Results
	for tt in title_list:
		res = tt.select('td.result_text')[0]
		#cprint(res.select('a')[0].text + res.text, "magenta")
		cprint(res.text, 'magenta')
		ch = input()
		if ch in ['y','Y','yes','']:
			return (base_url + res.select('a')[0]['href'])
	cprint('Couldn\'t find satisfactory result.',"red")
	return ''

def getDetails(url):
	details = dict()
	if not url:
		details['rating'] = ''
		details['title'] = ''
		return details
	#cprint("Visiting Title Page At %s" % url, "yellow")
	try:
		headers = {'Accept-Language': 'en-US,en;q=0.8'} # To get the english title for foreign movies!
		r = requests.get(url, headers=headers)
	except:
		cprint('Error making request. Check internet connection.', 'red')
		exit()
	soup = bs4.BeautifulSoup(r.text, "html.parser")
	#details['rating'] = soup.select('div.title_block div.ratings_wrapper div.ratingValue span').text
	try:
		details['rating'] = soup.find('span', {'itemprop': 'ratingValue'}).text
	except:
		details['rating'] = ''
		cprint('Ratings N/A','red')
	try:
		details['title'] = soup.find('h1', {'itemprop': 'name'}).text
	except:
		details['title'] = ''
		cprint('Title N/A','red')
	return details

def getTitleRatings(title):
	return getDetails(getRelevantURL(title)).get('rating') #Assuming user is sensible enough to type correctly w/o writing title.name.in.dots or other gibberish

def getFolderRatings(folderpath):
	try:
		os.chdir(folderpath)
	except:
		cprint('Incorrect path provided.','red')
	failed_items = []
	for item in os.listdir():
		print('Continue search for', ' ')
		cprint(item, 'yellow')
		ch = input()
		if ch not in ['y', 'Y', 'yes', '']:
			continue
		rating = ''
		query = ''
		extension = ''
		
		if os.path.isdir(folderpath + '/' + item):
			old_rating = False
			try:
				float(item[:3]) # 8.4 Swades
				old_rating = True
				query = item[3:].split('(')[0].strip() # Removing discrepancies like 8.4 Swades (2014).. Now, Swades
			except ValueError: #File Doesn't Contain Any Previous Ratings..
				query = item.split('(')[0] # Eg. Swades (2004).. Now, Swades
		else:
			if item.lower().split('.')[-1] in ['mp4', 'avi', 'mkv']:
				extension = '.'+item.split('.')[-1]
				old_rating = False
				try:
					float(item[:3])
					old_rating = True
					query = (item[:len(item)-4])[3:].split('(')[0].strip()
				except ValueError:
					query = item[:len(item)-4].split('(')[0].strip()
		
		details = getDetails(getRelevantURL(query))
		rating = details.get('rating')
		if not rating: # Trying to get rating again but this time with only first 7 letters of the cleaned query Eg. Whiplash YIFY 720p
			cprint('Trying Again..', 'red')
			if len(query.split('.')):
				query = query.replace('.', ' ') #Eg. The.Big.Short.2015.DVDSCR.750MB.MkvCage 
			query = query[:10] #Eg. The Big Sh
			details = getDetails(getRelevantURL(query))
			rating = details.get('rating')
		if rating:
			print(rating)
			if rating not in item:
				if not old_rating:
					filename = details.get('title') or item
					filename = filename.strip()
					try:
						os.rename(item, rating + ' ' + filename + extension)
					except PermissionError:
						cprint('File couldn\'t be renamed (Locked)', 'red')
						failed_items.append(item)
				else:
					filename = details.get('title') or item[3:].strip()
					filename = filename.strip()
					try:
						os.rename(item, rating + ' ' + filename + extension) # Updating filename with new rating
					except PermissionError:
						cprint('Error renaming the file. (Locked)', 'red')
						failed_items.append(item)
			else:
				title = details.get('title')
				if title:
					os.rename(item, rating + ' ' + title + extension)
		else:
			failed_items.append(item)
	
	cprint('Couldn\'t get ratings for: ','yellow')
	for item in failed_items:
		cprint(item,'cyan')

def runscript():
	title = ''
	folderpath = ''
	if len(sys.argv) == 1:
		cprint("For help, try running the script with -help or --h", "yellow")
		title = input("\nEnter The Search Title: ")

	elif len(sys.argv) == 2:
		if sys.argv[1] in ['-help', '--h']:
			cprint("This script gets the IMDB rating", "magenta")
			cprint("1) For a whole folder, add --f=\"<Folder Path\" as argument", "blue")
			cprint("2) For individual query, just run the script w/o any arguments", "blue")
		elif sys.argv[1].split('=')[0] == '--f':
			folderpath = sys.argv[1].split('=')[-1]
	else:
		cprint("Invalid inputs. Seek help by running the script with -help or --h", "red")
	
	if folderpath != '':
		getFolderRatings(folderpath)
	elif title != '':
		print(getTitleRatings(title))
	else:
		cprint("Invalid inputs. Seek help by running the script with -help or --h", "red")

if __name__ == '__main__':
	runscript()
