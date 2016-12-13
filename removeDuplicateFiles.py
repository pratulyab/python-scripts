import os,sys
import shutil
import re
from termcolor import *
import colorama

allDups = []

def findDups(folder,suffix=''):
	os.chdir(folder)
	folder_list = os.listdir()
	
	for item in folder_list:

		if item == 'Duplicate' + suffix:
			colorama.init();
			cprint('A Folder Named \'Duplicate' + suffix +'\' Already Exists. Please Provide An Appropriate Suffix','red');
			return


	if ' copy' in folder.split('/')[-1]:
		allDups.append(folder)
		return;
	
	for item in folder_list:
		if(os.path.isdir(folder+'/'+item)):
			findDups(folder+'/'+item);
			continue;
		else:
			if(bool(re.search(' copy \d*',item)) or bool(re.search(' copy.',item)) ):
				allDups.append(folder+'/'+item)
		os.chdir('..');


def moveDups(folder,suffix=''):
	os.chdir(folder)
	newF = 'Duplicate'+suffix
	os.makedirs(newF)
	dest = folder+'/'+newF

	for copied in allDups:
		shutil.move(copied,dest + '/' + copied.split('/')[-1]);


if(len(sys.argv)==1 or sys.argv[1] == "--help"):
	print("This script takes source folder path and creates a subfolder named 'Duplicate' and moves duplicate files to it");
	print("To run the script, type: python3 removeDuplicateFiles.py --f=\'folderpath\'");
	colorama.init();
	cprint(r"If There Already Exists A Folder Named 'Duplicate' In The Folder Provided, Please Ensure To Provide An Additional Argument As --s='Desired Suffix'","red");
elif(len(sys.argv)==2 and sys.argv[1].split('=')[0] == '--f'):
	folder = sys.argv[1].split('=')[-1];
	findDups(folder,'');
	if(allDups):
		moveDups(folder);
else:	
	folder = sys.argv[1].split('=')[-1];
	suffix = sys.argv[2].split('=')[-1];
	findDups(folder,suffix);
	if(allDups):
		moveDups(folder,suffix);
