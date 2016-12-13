import os, sys
import requests, bs4, re

def download(url, folder_path):
    r = requests.get(url);
    soup = bs4.BeautifulSoup(r.text, "html.parser"); #r.content does the same

    #HTML Images
    image_list = soup.find_all('img');
    for img in image_list:
        src = img['src']
        file_name = src.split('/')[-1];

        if(src[0:4] != "http"):
            src = url + src;

        img_response = requests.get(src);
        f = open(folder_path + '/' + file_name, 'w+b');
        f.write(img_response.content);
        f.close();
    #CSS Images
    style_list = soup.find_all('style');
    for style in style_list:
        styleText = style.string;
        pattern = "url\(.*?\)";
        URL = re.findall(pattern, styleText);
        for i in URL:
            URL_string = ''.join(i);
            ptrn = "\(.*?\)";
            URL_temp = re.findall(ptrn, URL_string);
            URL_string = ''.join(URL_temp);
            URL_final = URL_string[1 : len(URL_string)-1];
            file_name = URL_final.split('/')[-1];

            if(URL_final[0:4] != "http"):
                URL_final = url + URL_final;

            img_response = requests.get(URL_final);
            if(img_response):
                f = open(folder_path + '/' + file_name, 'w+b');
                f.write(img_response.content);
                f.close();

if (len(sys.argv) == 1 or sys.argv[1] == "--help"):
    print("This script takes a URL and a destination folder to download all images from the URL to the folder");
    print("To run the script, type: python downloadImages.py --u=URL --f=folder");
else:
    url = sys.argv[1].split('=')[-1];
    folder_path = sys.argv[2].split('=')[-1];
    download(url, folder_path);
