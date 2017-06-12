# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 11:15:35 2014

@author: user
"""
import urllib
import re


# link를 파일로 저장
# Question 1
def saveFile(link, outfile):
    # downloads html file "link"
    htmlFile = urllib.urlopen(link)

    # opens the file "outFile"
    fout = open(outfile, "w")
    # writes every line in "link" to "outFile"
    for line in htmlFile.read():
        fout.write(line)
    fout.close()


# question 2
# the link we are crawling (frenchPastry book.)
url = open("url.txt", "r")
for line in url:
    rootUrl = line;
    # my working path. You should change it to yours.
    path = "//Users/jihyunson/PycharmProjects/crawlIngredients/"
    # the name of the output file I am saving the amazon page.
    # id = line.split("8723Illuminate/","/reviews.htm?for")
    outFile = "ingredients.html";
    # calls the "saveFile" function. Uncoment it to run.
    saveFile(rootUrl, outFile)