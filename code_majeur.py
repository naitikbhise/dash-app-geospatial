#Importing Libraries. Regex library for dealing with disturbing brackets and spaces and their removal
import re
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

#New-York state data. Geopandas way to fill the data into geographic DataFrame
file = gpd.read_file('./datasets/new_york/gis_osm_roads_free_1.shp')

#New York Dataset has a lot of big names involving characters other than alphabets and spaces like Braces(). We try to remove the braces and try to limit the amount of spaces between words. Between words, there should only be a small space.
def find_brac(word):
    a = word.split('(')
    if len(a)>1:
        b = word.split(')')
        if len(b)>1:
            word = a[0]+b[1]
        else:
            if a[0]=='':
                word = a[1]
            else:
                word = a[0]
    #Regex command for removing terminal spaces in a string
    word = re.sub(r"^\s+|\s+$", "", word)
    #Regex command for removing wider spaces in a string
    return re.sub('[ \t]+' , ' ', word)

#Takes each letter in a word and makes a 26 element array of freqencies of the alphabets. We only consider alphabets from a to z
def props(word):
    word = word.lower()
    lett_arr = np.zeros(26)
    for i in range(len(word)-1):
        cond1 = (ord(word[i])-ord('a'))<26 and (ord(word[i])-ord('a'))>=0
        if cond1:
            lett_arr[ord(word[i])-ord('a')] += 1
    return lett_arr.T

#Takes each letter and next alphabet(if present) in a word and makes a 26X26 element array of freqencies of the letter pairs. We only consider alphabets from a to z
def props_lp(word):
    word = word.lower()
    let_pair = np.zeros(shape=(26,26))
    for i in range(len(word)-1):
        cond1 = (ord(word[i])-ord('a'))<26 and (ord(word[i])-ord('a'))>=0
        cond2 = (ord(word[i+1])-ord('a'))<26 and (ord(word[i+1])-ord('a'))>=0
        if cond1 and cond2:
            let_pair[ord(word[i])-ord('a'),ord(word[i+1])-ord('a')] +=1
    return let_pair.flatten().T

#Here , we calculate the L2 norm distance between two points in a coordinate plane.
def distance(array1, array2):
    return np.sqrt(np.sum((array1-array2)**2))

#this is the main code for the extracting the results in dictionary form. The input arguments are the point
def resultat(point,radius):
    #Selecting the region of interest of radius r around the point
    a = file['geometry'].map(lambda x:point.distance(x)<radius)
    df = file[list(a)]
    #Cleaning the file for Unnamed roads
    none = np.sum(df.name.isnull())
    df =df.reset_index()
    df = df[df.name.isnull()==False]
    #Remove the Braces and unused spaces(keep single space between two words ina  string)
    df['name'] = df['name'].map(lambda x:find_brac(x))
    #Separate the types of the streets which is generally the last word of the string from the name string
    df['type'] = df['name'].map(lambda x:x.split(' ')[-1])
    df['name'] = df['name'].map(lambda x:' '.join(x.split(' ')[:-1]))
    #Extract the letter matrix for each name
    df['lett'] = df['name'].map(lambda x:props(x))
    #Extract the letter pair matrix for each name
    df['let_p'] = df['name'].map(lambda x:props_lp(x))
    #Pull the centroid of the 26 element matrices and take the distances of other matrices from them.First feature for the unusual names
    letter_avg = np.average(df['lett'])
    df['score_base'] = df['lett'].map(lambda x:distance(x,letter_avg))
    #Pull the centroid of the 26X26 element matrices and take the distances of other similar matrices for the matrices from the them.Second feature for the unusual names
    let_p_avg = np.average(df['let_p'])
    df['score_base'] += df['let_p'].map(lambda x:distance(x, let_p_avg))
    
    #Count the frequencies of different types of streets from the type feature and make a dictionary. 
    unique, counts = np.unique(df['type'], return_counts=True)
    mydict = dict(zip(unique, counts))
    mydict['Unknown'] = none
    a = sorted(mydict.items(), key=lambda kv: kv[1], reverse=True)
    
    #Count the frequencies of names of streets for most common name results
    unique_1, counts_1 = np.unique(df['name'], return_counts=True)
    mydict_1 = dict(zip(unique_1, counts_1))
    b = sorted(mydict_1.items(), key=lambda kv: kv[1], reverse=True)
    
    #20 most common names in the dictionary
    i,j = 0,0
    d = []
    while (i<=19 and j<len(b)):
        small = {}
        if b[j][0]=='':
            j+=1
        else:
            small['title'] = i+1
            small['name'] = b[j][0]
            i+=1
            j+=1
            d.append(small)
    
    #Take the top few upto 19 frequent types to display in the histogram. We can display the whole but the bar looks more neat with less types.
    c = {}
    j = 0
    while (j<=min(19,len(a)-1)):
        c[a[j][0]] = a[j][1]
        j+=1
    
    #Third feature. We try to add the score with the frequency of all the street name types like a tf-idf method but we weight it by 0.5
    length = len(df)
    df['score_base'] += 0.5*df['name'].map(lambda x:np.log(length/mydict_1[x]))
    
    #Top 20 unusual names taken after adding 3 feature scores by making a dictionary.
    mydict_2 = pd.Series(df.score_base.values,index=df.name).to_dict()
    load = sorted(mydict_2.items(), key=lambda kv: kv[1], reverse=True)
    e = []
    i = 0
    while (i<=20 and i<len(load)):
        small = {}
        small['score'] = load[i][1]
        small['name'] = load[i][0]
        i+=1
        e.append(small)
    
    return c,d,e