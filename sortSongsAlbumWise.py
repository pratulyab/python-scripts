"""
	Task specific script. Not reusable.
	Had to sort over 1000+ songs in a directory according to the Band, and the corresponding album.
	Eg.
		Sweet child o' mine
		Thunderstruck
		..
	=>  DIR[Guns 'n' Roses] => AlbumDir[Blah] => Sweet child o' mine
	=>  DIR[AC/DC] => AlbumDir[Blah] => Thunderstruck
"""
import os,sys
import bs4,requests,re
import shutil
from termcolor import *
import colorama
import urllib.request

colorama.init()

artists_list = {
["GNR","Guns 'n' Roses","gnr","guns \'n\' roses"] : "",
["ABBA"] : "",
["AC/DC","AC-DC","ac/dc","ac-dc"] : "",
["Metallica"] : "",
["Coldplay"] : "",
["Earth,Wind And Fire","Earth, Wind And Fire", "Earth,Wind & Fire", "Earth, Wind & Fire","earth,wind & fire","earth,wind and fire","earth, wind & fire","earth, wind and fire"] : "",
["Adele","adele"] : "",
["Imagine Dragons","imagine dragons"] : ""
}

def sortSongsAlbumWise(folder,artist):
	os.chdir(folder);
	files_list = os.listdir();
#base_url = "https://www.azlyrics.com/lyrics";
	base_url = "http://www.metrolyrics.com"

	songs_list = list();
	album_set = set();
	description = dict();
	for soundtrack in files_list:
		if soundtrack.split('.')[-1] == "mp3" :
			songs_list.append(soundtrack);
			song = soundtrack.split('.')[1].lower()
			
			song = song.replace("\'","");
			song = song.replace("!","");
#song = song.replace("-","");
			song = song.replace(".","");
			song = song.replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","");
			song = song.split(' ')
			p = '-'
			p = p.join(song[1:])
			song = p
			
			print("Song = " + song + "\n");
			
#artist = artist.replace(" ","-").lower()
#url = base_url + '/' + artist + '/' + song + '.html?'
			url = base_url + '/' + song + '-lyrics-' + artist + '.html?'
			print(url)
			r = requests.get(url);
			
			if r:
				soup = bs4.BeautifulSoup(r.text, "html.parser")
				
#reqd_class = soup.find("div", {"class" : "panel album-panel noprint"})
				reqd_class = soup.find("div" , {"class" : "lyrics"})
#album = reqd_class.select('a')[0].text
				album = reqd_class.select("header > p > em > a")[0].text
				print("Extract From a = " + album + "\n")
#album = album.split('\"');
#				album_final_name = ""
#				album_final_name = album_final_name.join(album);
#				print("Album = " + album_final_name + "\n")
#				album_set.add(album_final_name)
				
#				description[soundtrack] = album_final_name;
				print("Album = " + album + "\n")
				album_set.add(album)
				description[soundtrack] = album
			else:
				cprint("Error in Response\n\n","red")
				continue;
		
		else :
			continue

	for album in album_set:
		if not os.path.exists(album) : os.makedirs(album)
	
	for song in songs_list:
		shutil.move(song,description[song]+'/'+song)


if (len(sys.argv) == 1 or sys.argv[1] == "--help" or sys.argv[1] == "-h"):
	cprint("This Script Takes A Folder Path, Into Which The Songs Are Sorted Accoring To Their Respective Albums\n","green");
	cprint("To Run The Script, If:\n1.Folder Name Contains Only The Name Of The Artist\n2.The Folder Name Contains Some Other Text Also\n","red")
	cprint("Then Type Either Of The Following According To The Correct Option:\n","red")
	cprint("1. python3 sortSongsAlbumWise.py --f=\"<folder-path>\"\n2. python3 sortSongsAlbumWise.py --f=\"<folder-path\" --a=\"<artist-name>\"\n","yellow");

elif len(sys.argv) == 2 and sys.argv[1].split('=')[0] == '--f':
	folder = sys.argv[1].split('=')[-1];
	artist = folder.split('/')[-1].replace(" ", "").lower();
	sortSongsAlbumWise(folder, artist);
else:
	folder = sys.argv[1].split('=')[-1];
	artist = sys.argv[2].split('=')[-1].replace(" ", "").lower();
	sortSongsAlbumWise(folder, artist);

