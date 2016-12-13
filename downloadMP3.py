# Enables to download songs from youtube using youtube-mp3.org
import sys
import re
import time
import requests , bs4
import json
from urllib.parse import quote,unquote
import colorama
from termcolor import *

colorama.init()

filename = ""
folder_path = ""
headers = {'content-type' : 'application/json'}
youtube = "https://www.youtube.com"

#Encoding Logic From youtube-mp3.org
def getSparam(url):
	url = url.lower()
	A = {
			"a": 870,
 			"b": 906,
			"c": 167,
			"d": 119,
			"e": 130,
			"f": 899,
			"g": 248,
			"h": 123,
			"i": 627,
			"j": 706,
			"k": 694,
			"l": 421,
			"m": 214,
			"n": 561,
			"o": 819,
			"p": 925,
			"q": 857,
			"r": 539,
			"s": 898,
			"t": 866,
			"u": 433,
			"v": 299,
			"w": 137,
			"x": 285,
			"y": 613,
			"z": 635,
			"_": 638,
			"&": 639,
			"-": 880,
			"/": 687,
 			"=": 721
	}
	r3 = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
	F = 1.51214
	N = 3219
	i = 0
	while i<len(url):
		Q = list(url)
		q = Q[i]
		if q in r3:
			q = int(q)
			N = N + (q*121*F)
		else:
			q = A.get(q,0)
			N = N + (q*F)
		N = N * 0.1
		i = i + 1
	
	N = round(N*1000)
	return str(N)


def handleAutoCorrect(soup,original):
	correction = soup.find_all("a",{"class":"yt-uix-sessionlink spell-correction-corrected-query       spf-link "})
	if correction:
		corrected = ""
		for i in correction:
			corrected = corrected + i.text
		
		cprint("Showing Results For %s" %corrected,"blue")
		cprint("Search Instead For Original Query %s? y/n" %original,"blue")
		
		ch = input()
		if ch in ['','y','Y','yes','Yes','YES']:
			redirect = soup.find_all("a",{"class":"yt-uix-sessionlink spell-correction-original-query       spf-link "})
			if not redirect:
				cprint("NEVER","yellow")
				return ""

			url = youtube + redirect[0]['href']
			soup = bs4.BeautifulSoup(requests.get(url).text,"html.parser")
		
	return soup


def getVideoID(search_query):
	global filename
	original = search_query
	
	search_query = search_query.strip()
	search_query = re.sub(r'\s+',' ',search_query)
	search_query = search_query.replace('+','%2B').replace(' ','+').replace('\\','%5C').replace('/','%2F').replace('\'','%27').replace('=','%3D').replace('!','%21').replace('(','%28').replace(')','%29').replace(',','%2C').replace('@','%40').replace('#','%23').replace('$','%24').replace('%','%25').replace('^','%5E').replace('&','%26').replace('*','%2A').replace('?','%3F').replace('|','%7C').replace(';','%3B').replace(':','%3A')
	searchYTB = youtube + "/results?search_query=" + search_query
	r = requests.get(searchYTB)

	soup = bs4.BeautifulSoup(r.text,"html.parser")
	
	soup = handleAutoCorrect(soup,original) #Will Send Either The Original soup or Non-AutoCorrected Soup

	main_container = soup.find_all("div",{"class" : "yt-lockup-dismissable yt-uix-tile"})
	if not main_container:
		cprint("Sorry! Couldn't Find A Satisfactory Result For You. Please Try Again With A Better Search Query!","blue")
		quit()
	
	href_list = []
	video_id = ""
	count = 0
	cprint("Results With Duration Greater Than 20 Minutes Cannot Be Converted. Therefore, Not Displayed.","yellow")
	cprint("You Can Choose Previous Result By Entering The Result Number","cyan")
	for container in main_container:
		if len(container.find_all("span",{"class" : "yt-badge ad-badge-byline yt-badge-ad"})):
			cprint("Ad Removed","yellow")
			continue
		
		#Video Time
		thumbnail = container.find_all("div",{"class" : "yt-lockup-thumbnail contains-addto"})
		if not thumbnail:
			continue #Means Playlist Entry
		time = thumbnail[0].find_all("span",{"class" : "video-time"})
		video_time = time[0].text
		
		time_components = video_time.split(':')

		if len(time_components) == 3:
			continue
		else:
			minutes,seconds = time_components
		if int(minutes) > 20:
			continue
		elif int(minutes) == 20 and int(seconds) > 0:
			continue

		#Content
		content_container = container.find_all("div",{"class" : "yt-lockup-content"})
		anchor = content_container[0].find_all("a",{"class" : "yt-uix-sessionlink yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2       spf-link "})
		
		if not anchor:
			cprint("Sorry! Couldn't Find A Satisfactory Result For You. Please Try Again With A Better Search Query!","blue")
			quit()
		
		chosen = False
		
		for a in anchor:
			if a['href'] and '&list' not in a['href']:
				cprint(str(count+1) + '\t' + a['title'] + "  " + video_time + " (y/n)","magenta")
				href_list.append(a)
				ch = input()
				if ch in ['','y','Y','yes','Yes','YES']:
					chosen = True
					video_id = a['href']
					if filename == "":
						filename = a['title']
					break
				else:
					try:
						if int(ch) > 0 and int(ch) <= len(href_list):
							chosen = True
							video_id = href_list[int(ch)-1]['href']
							if filename == "":
								filename = href_list[int(ch)-1]['title']
							break
						else:
							cprint("Invalid Number","blue")
					except:
						pass
		if chosen:
			break
		count = count + 1
	if video_id == "":
		cprint("Sorry, Couldn't Find A Satisfactory Result For You. Please Try Again With A Better Search Query!","blue")
		quit()
	return video_id


def pushItem(ID):
	ID = "https://www.youtube.com" + ID
	url = "http://www.youtube-mp3.org/a/pushItem/?item=" + quote(ID) + "&el=na&bf=false&r=" + str(int(round(time.time()*1000)))
	url = url + "&s=" + getSparam(url)
#	print(url)
	return requests.get(url,headers=headers).text


def getInfo(ID):
	url = "http://www.youtube-mp3.org/a/itemInfo/?video_id=" + ID + "&ac=www&t=grp&r=" + str(int(round(time.time()*1000)))
	url = url + "&s=" + getSparam(url)
#	print(url)
	r = requests.get(url,headers=headers).text #info dictionary
	try:
	#	info = json.loads(r.split(';')[0].split(' = ')[-1])
	#	Removing this because we've assumed only the end semicolon info = {};.. But error occurs when there is a semicolon in the dictionary E.G. &amp; (escape characters).. Therefore, checking whether or not last char is ; and removing it
		if r[len(r) - 1] == ';':
			r = r[:len(r)-1]
		info = json.loads(r.split(' = ')[-1]) # info = {}
	except:
		cprint("Sorry, Couldn't Convert The Requested Link Because Of Copyright Issues","red")
		exit()
	return info


def downloadMP3(query):
	global filename,folder_path
	ID = getVideoID(query) #Of Format /watch?....
	ID = pushItem(ID) #has only the id
	info = getInfo(ID)
	download_url = "http://www.youtube-mp3.org/get?video_id=" + ID + "&ts_create=" + str(info['ts_create']) + "&r=" + quote(info['r'],safe='') + "&h2=" + (info['h2'])
	download_url = download_url + "&s=" + getSparam(download_url)
#	print(download_url)
	cprint("\n======== DOWNLOADING " + filename + " ==========\n","blue")
	audiofile = requests.get(download_url)
	cprint("\n--------------------------Download Complete----------------------------","blue")
	
	if ".mp3" not in filename:
		filename = filename + ".mp3"
	if folder_path:
		if not folder_path[len(folder_path)-1]=='/':
			folder_path = folder_path + '/'
	try:
		f = open(folder_path+filename,'w+b')
		f.write(audiofile.content)
		f.close()
		cprint("File Saved At " + folder_path + filename,"yellow")
	except:
		cprint("Error Saving The File. Please Make Sure You've Provided A Valid Path",'red')
		exit()

if len(sys.argv)==2 and sys.argv[1] in ['--help','--h']:
	cprint("This Script Allows You To Download A MP3 Song By Taking Input A Related Search Query","magenta")
	cprint("--f\t\tFileName\n--p\t\tFolder Path\n--h\t\tHelp")
	cprint("To Run This Script:\n1)With Argument(s):\tType python3 <scriptname> --f=<filename> --p=<Folder Path>\n2)W/O Arguments: \tType python3 <scriptname>","cyan")
	exit()
elif len(sys.argv)==2:
	if sys.argv[1].split('=')[0] == "--f":
		filename = " ".join(sys.argv[1].split('=')[1:])
	elif sys.argv[1].split('=')[0] == "--p":
		folder_path = " ".join(sys.argv[1].split('=')[1:])
	else:
		cprint("Not A Valid Argument. Try Running Script With --h for help","red")
		exit()
elif len(sys.argv)==3:
	for i in range(1,3):
		if sys.argv[i].split('=')[0] == "--f":
			filename = " ".join(sys.argv[i].split('=')[1:])
		elif sys.argv[i].split('=')[0] == "--p":
			folder_path = " ".join(sys.argv[i].split('=')[1:])
		else:
			cprint("Not A Valid Argument. However, continuing..","red")
elif len(sys.argv) > 3:
	cprint("Invalid Number Of Arguments Given. Try Running Script With --h for help","red")
	exit()
else:
	print("For Help, Provide --h argument")

search = input("\nSearch: ")
if search != "":
	downloadMP3(search)
