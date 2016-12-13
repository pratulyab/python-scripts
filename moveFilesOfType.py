import os,sys
import shutil

def moveFilesOfType(source,dest,file_type):

    os.chdir(source)
    folder_list = os.listdir()

    for item in folder_list:
        if(os.path.isdir(source+'/'+item)):
            moveFilesOfType(source+'/'+item,dest,file_type)
            continue
        name_split = item.split('.')
        if(len(name_split) > 1 and name_split[-1] == file_type):
            shutil.move(source+'/'+item, dest+'/'+item)
    os.chdir('..')

if (len(sys.argv) == 1 or sys.argv[1] == "--help"):
    print("This module takes source path, destination path and type of the file to be moved from source path to destination path");
    print("To run this module, type: moveFilesOfType.py --s=source path --d=destination path --t=type");
else:
    source = sys.argv[1].split('=')[-1];
    dest = sys.argv[2].split('=')[-1];
    file_type = sys.argv[3].split('=')[-1];
    moveFilesOfType(source,dest,file_type);
