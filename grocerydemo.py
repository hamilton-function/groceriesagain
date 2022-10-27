'''
Readme

To install googlemaps library: pip install -U googlemaps

To install populartimes library: pip install --upgrade git+https://github.com/m-wrzr/populartimes

Set API_KEY variable with your own google api key

Set alljsonfilesarray variable to the path of your own timeline json file

Now you should be ready to go!
'''


import tkinter as tk
import tkinter.font as tkFont

location = ""
store_name = ""

root = tk.Tk()

#setting title
root.title("Doing Groceries Again...")
#setting window size
width=600
height=500
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
root.geometry(alignstr)
root.resizable(width=False, height=False)

GLabel_305=tk.Label(root)
ft = tkFont.Font(family='Times',size=10)
GLabel_305["font"] = ft
GLabel_305["fg"] = "#333333"
GLabel_305["justify"] = "center"
GLabel_305["text"] = "Grocery store brand"
GLabel_305.place(x=20,y=100,width=120,height=25)

GLabel_624=tk.Label(root)
ft = tkFont.Font(family='Times',size=10)
GLabel_624["font"] = ft
GLabel_624["fg"] = "#333333"
GLabel_624["justify"] = "center"
GLabel_624["text"] = "Near the location"
GLabel_624.place(x=20,y=180,width=120,height=25)

GLineEdit_890=tk.Entry(root)
GLineEdit_890["borderwidth"] = "1px"
ft = tkFont.Font(family='Times',size=10)
GLineEdit_890["font"] = ft
GLineEdit_890["fg"] = "#333333"
GLineEdit_890["justify"] = "center"
GLineEdit_890["text"] = "Entry1"
GLineEdit_890.place(x=140,y=100,width=382,height=30)

GLineEdit_145=tk.Entry(root)
GLineEdit_145["borderwidth"] = "1px"
ft = tkFont.Font(family='Times',size=10)
GLineEdit_145["font"] = ft
GLineEdit_145["fg"] = "#333333"
GLineEdit_145["justify"] = "center"
GLineEdit_145["text"] = "Entry2"
GLineEdit_145.place(x=140,y=180,width=381,height=30)



def submit():  # Callback function for SUBMIT Button
    global location, store_name
    location = GLineEdit_145.get()
    store_name = GLineEdit_890.get()
    root.destroy()

GButton_200=tk.Button(root)
GButton_200["bg"] = "#f0f0f0"
ft = tkFont.Font(family='Times',size=10)
GButton_200["font"] = ft
GButton_200["fg"] = "#000000"
GButton_200["justify"] = "center"
GButton_200["text"] = "Some magic happens..."
GButton_200.place(x=230,y=270,width=130,height=40)
GButton_200["command"] = submit

root.mainloop()

print(location, store_name)



'''
-------------------------------------------------------BEGINNING OF COMPUTATION-----------------------------------------
'''

import time
import googlemaps # pip install googlemaps
import pandas as pd # pip install pandas


API_KEY = 'INSERT YOUR GOOGLE API KEY HERE'
map_client = googlemaps.Client(API_KEY)

address = location
geocode = map_client.geocode(address=address)
(lat, lng) = map(geocode[0]['geometry']['location'].get, ('lat', 'lng'))


search_string = store_name
distance = 8000 #this represents the eps-range of the search query in meters
business_list = []

response = map_client.places_nearby(
    location=(lat, lng),
    keyword=search_string,
    radius=distance
)

business_list.extend(response.get('results'))
next_page_token = response.get('next_page_token')

while next_page_token:
    time.sleep(2)
    response = map_client.places_nearby(
        location=(lat, lng),
        keyword=search_string,
        radius=distance,
        page_token=next_page_token
    )
    business_list.extend(response.get('results'))
    next_page_token = response.get('next_page_token')

df = pd.DataFrame(business_list)
df['url'] = 'https://www.google.com/maps/place/?q=place_id:' + df['place_id']
#df.to_excel('{0}.xlsx'.format(search_string), index=False)



'''
Storing data within a dictionary of the following structure:
key: place_id
value: [lat, lng, dist]
'''

#convert to dictionary of structure sketched in the preembel of this cell (key:, ...,value:...)
def extractPID_Lat_Lon(pdframe):
  #init dictionary:
  candidate_loc_dic = {}
  pdframe = pdframe.reset_index()  # make sure indexes pair with number of rows
  for index, row in pdframe.iterrows():
    #extract lat, lng
    loc_lat = ((row['geometry'])['location'])['lat']
    loc_lng = ((row['geometry'])['location'])['lng']
    loc_id = row['place_id']
    candidate_loc_dic[loc_id] = [loc_lat, loc_lng]
  return candidate_loc_dic

extracted_dict = extractPID_Lat_Lon(df)



'''
Code originally from: https://stackoverflow.com/questions/58053077/get-distance-from-google-cloud-maps-directions-api

also on shortest routes in google maps: https://stackoverflow.com/questions/18574496/google-distance-matrix-json-shortest-path-php

Input: takes two coordinates/locations
Output: the shortest path/distance from all possible routes between the two coordinates proposed by google
'''

# Import libraries
import googlemaps
from datetime import datetime
import numpy as np


def get_shortest_distance(coordStart, coordDestination):
  #transform format of coordinates (lat, lng) to 'lat,long'
  coords_0 = str(coordStart[0])+','+str(coordStart[1])
  coords_1 = str(coordDestination[0])+','+str(coordDestination[1])

  # Request directions
  now = datetime.now()
  directions_result = map_client.directions(coords_0, coords_1, mode="driving", departure_time=now, alternatives = True)

  #stores distances of all paths from start to destination
  distances_array = []

  for path in directions_result:
    # Get distance
    distance = 0
    legs = path.get("legs")
    for leg in legs:
      distance = (distance + leg.get("distance").get("value"))/1000.0
    distances_array.append(distance)
  mindist = np.min(distances_array)
  #print(distances_array)
  return mindist



'''
routine takes the dictionary with place_id as key and appends the shortest distance from a starting point to the destination in its value array: [lat, lng, dist]
'''

def append_shortest_distances_to_querydict(querydict, startpos):
  for key in querydict.keys():
    destpos = ((querydict[key])[0],(querydict[key])[1])
    shortestdist = get_shortest_distance(startpos, destpos)
    querydict[key].append(shortestdist)



'''
routine computes the duration of the /fastest/ path and returns the duration in minutes

Code originally from: https://stackoverflow.com/questions/14635926/google-maps-api-travel-time-with-current-traffic


Input: takes two coordinates/locations
Output: the fastest path from all possible routes between the two coordinates proposed by google
'''


# Import libraries
import googlemaps
from datetime import datetime
import numpy as np


def get_fastest_path_duration(coordStart, coordDestination):
  #transform format of coordinates (lat, lng) to 'lat,long'
  coords_0 = str(coordStart[0])+','+str(coordStart[1])
  coords_1 = str(coordDestination[0])+','+str(coordDestination[1])

  # Request directions
  now = datetime.now()
  directions_result = map_client.directions(coords_0, coords_1, mode="driving", departure_time=now, alternatives = True)

  #stores durations of all paths from start to destination
  durations_array = []

  for path in directions_result:
    # Get distance
    duration = 0
    legs = path.get("legs")
    for leg in legs:
      duration = (duration + leg.get("duration_in_traffic").get("value"))/60.0
    durations_array.append(duration)
  mindur = np.min(durations_array)
  #print(durations_array)
  return mindur




'''
routine takes the dictionary with place_id as key and appends the lowest driving duration from a starting point to the destination in its value array: [lat, lng, dur]
'''

def append_minduration_path_to_querydict(querydict, startpos):
  for key in querydict.keys():
    destpos = ((querydict[key])[0],(querydict[key])[1])
    mindurdist = get_fastest_path_duration(startpos, destpos)
    querydict[key].append(mindurdist)


'''
routine takes a place_id
it returns the current popularity "current_popularity" -> normalize by dividing the popular time value (i.e. 33) by the mean value on that particular week day (i.e. 28).
A value >1 indicates that this place is busier than "on average" at those week days, while a value close to 0 means that this place is barely visited right now contrary to the "average" busy time

get_id(api_key, place_id)
    retrieves the CURRENT popularity for a given place
    :param api_key:
    :param place_id:
    :return: see readme
'''

import populartimes
# for getting weekday
import datetime
import numpy


def compute_relative_popularTimes(place_id):
    # fetch current weekday as string
    weekdaymap = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    currweekday = weekdaymap[datetime.datetime.today().weekday()]

    if ('current_popularity' in populartimes.get_id(API_KEY, place_id).keys()):
        # current popularity of that place
        curr_pop = populartimes.get_id(API_KEY, place_id)['current_popularity']
        # average popularity on that day for that place
        day_avg_pop = []
        # fetch the array with the data of popular times for one location
        populartimesarray = populartimes.get_id(API_KEY, place_id)['populartimes']
        if populartimesarray:
            for day in populartimesarray:
                # fetch the data for the current weekday, returns an array of populartimes over each hour of the current weekday
                if day['name'] == currweekday:
                    day_avg_pop = day['data']

        # compute for the current weekday populartimes its average
        daily_avg_pop = None
        if day_avg_pop:
            daily_avg_pop = np.average(day_avg_pop)

        # get current hour
        now = datetime.datetime.now()
        currhour = now.hour + 1
        currhourpop = day_avg_pop[currhour]
        # compute relative current popularity by dividing the current popularity by the average popularity of the current day
        comp2avg_pop = None
        if (daily_avg_pop != None) and (curr_pop != None):
            comp2avg_pop = curr_pop / currhourpop

        return comp2avg_pop
    else:
        return numpy.inf



'''
routine takes the dictionary with place_id as key and appends the relative popular time of the day: [lat, lng, dur, relpop]
'''

def append_relpopularity_to_querydict(querydict):
  for key in querydict.keys():
    relpop = compute_relative_popularTimes(key)
    querydict[key].append(relpop)


'''
initial cell for timeline data analysis
data stored in google drive /timelinedata
json files for each month over year(s)
'''

import json
from datetime import date
import glob

#supermarket timeline dictionary
timelinedict = {'Aldi' : [],
                'Rewe' : [],
                'Lidl' : [],
                'Edeka' : [],
                'Famila' : [],
                'real' : [],
                'Netto' : [],
                'Norma' : [],
                'Rossmann' : [],
                'dm' : [],
                'Kaufland' : [],
                'Marktkauf' : [],
                'Action' : [],
                'Markant' : [],
                'Penny' : [],
                'V-Markt' : [],
                'Hit' : []}



'''
store in timeline-dictionary:

first access each file, iterate through and fetch per grocery store/supermarket (keys)
the confidence (should be 60% or above) then store the timestamp in an array (values).
through this we can cover:
(1) the overall frequency how often which supermarket was visited
(2) the recency, which supermarket was visited how many days ago

regarding (1) we cut later on the dictionary based on the top-k most frequently visited supermarkets
'''

#routine for a single json file in a folder of timeline data

def populateTimelineDict(singlejson):
  #json files in a folder named timelinedata of the form YEAR_MONTH.json, e.g. 2022_APRIL.json
  with open(singlejson, 'r') as f:
    data = json.load(f)

  for i in range(len(data['timelineObjects'])):
    if 'placeVisit' in data['timelineObjects'][i].keys():

      #check if location has a name...
      if 'name' in data['timelineObjects'][i]['placeVisit']['location'].keys():

        #timelineObjects --> entry index (0,1,2...,n) --> placeVisit --> location --> name
        #remark on name: check if name from supermarktlist is partially in the location name, e.g. aldi in list is in aldi kronshagen in timeline name; python substring/contains function
        locationname = data['timelineObjects'][i]['placeVisit']['location']['name']

        #timelineObjects --> entry index (0,1,2...,n) --> placeVisit --> location --> locationConfidence (should be >=60)
        locationconfidence = data['timelineObjects'][i]['placeVisit']['location']['locationConfidence']

        #timelineObjects --> entry index (0,1,2...,n) --> placeVisit --> duration --> endTimestamp (capture only YYYY-MM-DD)
        lasttimevisited = date.fromisoformat(data['timelineObjects'][i]['placeVisit']['duration']['endTimestamp'][:10])

        #check if name of supermarket is at least partially in any key of the timeline dictionary...
        for key in timelinedict.keys():
          #split locationname by whitespace and take first string, since that contains the supermarket name, make sure that cases don't matter
          #by making both, dictionary key and locationname to lowercase
          locnameadapted = ((locationname.split())[0]).lower()
          keyadapted = key.lower()
          if locnameadapted == keyadapted and locationconfidence >= 60:
            timelinedict[key].append(lasttimevisited)


'''
Routine to prune timeline dictionary to the top 5 / most frequently visited places
'''


def pruneTimelineDict(tldict, topk):
    # get first all frequencies sorted in descending order
    frequencyarray = []
    for key in tldict:
        freq = len(tldict[key])
        frequencyarray.append(freq)
    frequencyarray.sort(reverse=True)

    # then access at position topk-1 use that value for pruning
    pruningthreshold = frequencyarray[topk - 1]

    # start pruning for all entries in the tldict that have a value array length < pruningthreshold
    for key in list(tldict):
        if len(tldict[key]) < pruningthreshold:
            del tldict[key]


'''
Function retrieves for -one- supermarket location in a 2 km radius other supermarkets (need to remove the supermarket location (start point) itself)
and stores their names in an array
'''


def getNearbySupermarkets(lat, lng):
    search_query = 'supermarket'
    distance = 2000  # this represents the eps-range of the search query in meters
    business_list = []

    response = map_client.places_nearby(
        location=(lat, lng),
        keyword=search_query,
        radius=distance
    )

    business_list.extend(response.get('results'))
    next_page_token = response.get('next_page_token')

    while next_page_token:
        time.sleep(2)
        response = map_client.places_nearby(
            location=(lat, lng),
            keyword=search_query,
            radius=distance,
            page_token=next_page_token
        )
        business_list.extend(response.get('results'))
        next_page_token = response.get('next_page_token')

    df = pd.DataFrame(business_list)
    df['url'] = 'https://www.google.com/maps/place/?q=place_id:' + df['place_id']

    # project dataframe down to column of the names of other supermarkets and convert it to a np array
    df_names = df['name'].values

    # remove names after the store, e.g. Aldi Nord --> remove 'Nord'
    singular_store_names = []
    for e in df_names:
        str_arr = e.split()
        singular_store_names.append(str_arr[0])

    # transform to set and back to remove duplicates
    nn_stores = list(set(singular_store_names))

    # remove original query / supermarket from array
    for e in nn_stores:
        if e.lower() == search_string.lower():
            nn_stores.remove(e)

    # now store only the supermarkets that are among the top-k ones based on the timeline
    final_popular_markets = []
    popularmarkets = timelinedict.keys()
    for e in nn_stores:
        for f in popularmarkets:
            if e.lower() == f.lower():
                final_popular_markets.append(e)

    return final_popular_markets


'''
aldilat = 54.3541912
aldilng = 10.1050172
aldinndf = getNearbySupermarkets(aldilat, aldilng)
print(aldinndf)
'''

'''
routine goes through all supermarkets locations (keys) of a particular brand and computes per supermarkt an array of in-viccinity supermarkets that are based on the personal timeline top-k visited (value)
'''


def getAllNearestSupermarketsPerSupermarktX(querydict):
    for key in querydict.keys():
        lat, lng, dist, dur, pop = querydict[key]
        popnnmarkets = getNearbySupermarkets(lat, lng)
        querydict[key].append(popnnmarkets)


'''
Routine computes the utility score based on the afore collected information
following things need to be weighted/are terms of the score:
(1) the number of other supermarkets in the neighborhood of radius = eps
(2) per supermarket in neighborhood the relative frequency e.g. 10x lidl / 91 supermarkt visits of the top-k
(3) per supermarket the number of days (until now) since last visit

how to incorporate these three facators?
invert (^-1) to get a 'utility distance' / meaning that the lower the better...?

Example:
query: aldi
in total 2 other supermarkets in radius of 1km:
* rewe; overall 45 times visited, last visit 20 days ago
* edeka; overall 22 times visited, last visit 1 day ago
'''

'''
routine to compute the utility score
call this function with a check in if-clause if viccinityarray is not zero. if it is, set score to zero since there is no 'utility' at all for that query supermarket
'''


def computeUtilityPerQueryLocation(viccinityarray):
    # preliminary: compute total number of visits of top-k supermarkets
    freq_totalvisits = 0
    for supermarket in timelinedict:
        freq_totalvisits = freq_totalvisits + len(timelinedict[supermarket])

    # first term: compute ratio of number of top-k popular supermarkets in viccinity of a query supermarket to the total number (top-k) supermarkets
    # +1 is since we account for the query supermarket contributing to the utility of a place
    term1_topkamount = float(len(viccinityarray) + 1) / float(len(timelinedict.keys()))

    # second term: compute sum over relations of frequencies per top-k supermarket occuring in viccinity of a query supermarket
    term2_relationsfreq = 0
    for supermarket in viccinityarray:
        # to match supermarket name to the key of timelinedict
        supermarketcaseopt = ''
        for key in timelinedict.keys():
            if supermarket.lower() == key.lower():
                supermarketcaseopt = key

        freq_supermarket = len(timelinedict[supermarketcaseopt])
        term2_relationsfreq = term2_relationsfreq + (float(freq_supermarket) / float(freq_totalvisits))
    # add the own query supermarket to the term
    term2_relationsfreq = term2_relationsfreq + (float(len(timelinedict[search_string])) / float(freq_totalvisits))

    # third term: The sum over the inverse of number of days since last visited per supermarket in the viccinity of the query supermarket
    term3_dayssinceratio = 0
    for supermarket in viccinityarray:
        # to match supermarket name to the key of timelinedict
        supermarketcaseopt = ''
        for key in timelinedict.keys():
            if supermarket.lower() == key.lower():
                supermarketcaseopt = key

        # get latest date since last visited a particular supermarket 'type'
        lasttime = sorted(timelinedict[supermarketcaseopt])[-1]
        # get number of days between last time visited and today (current day)
        currtime_raw = datetime.datetime.now()
        # truncate currtime_raw by removing time
        currtime = datetime.date(currtime_raw.year, currtime_raw.month, currtime_raw.day)
        deltadays = (currtime - lasttime).days
        term3_dayssinceratio = term3_dayssinceratio + (float(1) / float(deltadays))

    utilityscore = term1_topkamount + term2_relationsfreq + term3_dayssinceratio
    # inverted score, because we want to have the lower values the better, since we also aim for lowest traffic time and lowest distance
    # facilitates later on the computation of the pareto front
    inverted_score = len(timelinedict.keys()) + 2 - utilityscore
    return inverted_score



'''
routine takes the dictionary with place_id as key and appends the utility of that location: [lat, lng, dist, dur, poptimes, history, util]
'''

def append_utility_to_querydict(querydict):
  for key in querydict.keys():
    neighborhood_list = querydict[key][5]
    if neighborhood_list:
      util = computeUtilityPerQueryLocation(neighborhood_list)
      querydict[key].append(util)
    else:
      #for the case that no other supermarket is in viccinity of query supermarket --> penalize with highest score possible
      maxscore = len(timelinedict.keys())+2
      querydict[key].append(maxscore)



#computation of lat,lng coors, shortest distance, minimum traffic duration, relative populartimes

from datetime import datetime

startcoor = (lat, lng)

append_shortest_distances_to_querydict(extracted_dict, startcoor)

append_minduration_path_to_querydict(extracted_dict, startcoor)

import datetime

append_relpopularity_to_querydict(extracted_dict)


alljsonfilesarray = glob.glob('INSERT PATH TO GOOGLE TIMELINE DATA HERE')

for jsonfile in alljsonfilesarray:
  populateTimelineDict(jsonfile)

pruneTimelineDict(timelinedict, 5)

getAllNearestSupermarketsPerSupermarktX(extracted_dict)

append_utility_to_querydict(extracted_dict)
for key in extracted_dict:
  print('key: ', key, ' val: ',extracted_dict[key])

print(extracted_dict)



#project down to columns containing place_id and vicinity for label information in the plot
df_projected = df[['place_id', 'vicinity']]

df_projected.head()

df_dict = df_projected.set_index('place_id').T.to_dict('list')

df_dict



'''
-------------------------------------------------BEGINNING OF OUTPUT/VISUALIZATION--------------------------------------
'''


'''
Routine to plot results with pareto-optimal supermarkets of a query
'''

from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import numpy as np

# for drawing the pareto front
import matplotlib.tri as mtri


'''
Pareto Source Code from: 
https://stackoverflow.com/questions/37000488/how-to-plot-multi-objectives-pareto-frontier-with-deap-in-python
'''


def simple_cull(inputPoints, dominates):
    paretoPoints = set()
    candidateRowNr = 0
    dominatedPoints = set()
    while True:
        candidateRow = inputPoints[candidateRowNr]
        inputPoints.remove(candidateRow)
        rowNr = 0
        nonDominated = True
        while len(inputPoints) != 0 and rowNr < len(inputPoints):
            row = inputPoints[rowNr]
            if dominates(candidateRow, row):
                # If it is worse on all features remove the row from the array
                inputPoints.remove(row)
                dominatedPoints.add(tuple(row))
            elif dominates(row, candidateRow):
                nonDominated = False
                dominatedPoints.add(tuple(candidateRow))
                rowNr += 1
            else:
                rowNr += 1

        if nonDominated:
            # add the non-dominated point to the Pareto frontier
            paretoPoints.add(tuple(candidateRow))

        if len(inputPoints) == 0:
            break
    return paretoPoints, dominatedPoints


def dominates(row, candidateRow):
    return sum([row[x] < candidateRow[x] for x in range(len(row))]) == len(row)


'''
data extracted from GMapsSIGSPATIAL.ipynb (to avoid costly recomputation, since those cost actually real money...)
for demo purposes the both dictionaries (map_placeid_loc , resdict) will be forwarded and not explicitly hard-coded like here
'''

map_placeid_loc = df_dict

resdict = extracted_dict


arr_locations = []
arr_distances = []
arr_durations = []
arr_utility = []
arr_poptimes = []

keyslist = resdict.keys()

for key in keyslist:
    lat, lng, dist, dur, pop, vicc, util = resdict[key]
    arr_locations.append(key)
    arr_distances.append(dist)
    arr_durations.append(dur)
    arr_utility.append(util)
    arr_poptimes.append(pop)

arr_labels = []
for e in arr_locations:
    address = map_placeid_loc[e]
    arr_labels.append(address)

inputPoints = list(zip(arr_distances, arr_durations, arr_utility))
inputVectArr = list(zip(arr_distances, arr_durations, arr_utility))

paretoPoints, dominatedPoints = simple_cull(inputPoints, dominates)

# populate dictionary with dominating objects with storelocation code as keys
fusiondict = {}
for dominate in paretoPoints:
    for i in range(len(keyslist)):
        if dominate == inputVectArr[i]:
            fusiondict[list(keyslist)[i]] = [dominate]

# now we need to determine by which feature/pair of features each pareto component dominates (min. values)
# (distance, duration, utility etc.)
from operator import itemgetter

mindistvec = [min(paretoPoints, key=itemgetter(0)), 'Store with shortest distance: ']
mindurvec = [min(paretoPoints, key=itemgetter(1)), 'Store with shortest traffic duration: ']
minutilvec = [min(paretoPoints, key=itemgetter(2)), 'Store with best utility: ']

# enrich fusiondict with min-solutions:
for key in fusiondict.keys():
    if fusiondict[key][0] == mindistvec[0]:
        fusiondict[key].append(mindistvec[1])
    elif fusiondict[key][0] == mindurvec[0]:
        fusiondict[key].append(mindurvec[1])
    elif fusiondict[key][0] == minutilvec[0]:
        fusiondict[key].append(minutilvec[1])
    else:
        fusiondict[key].append('Trade-off solution from the skyline: ')

'''
the following output can be shown in a nice listing (website or app)
here we have a rudimentary printout so far
'''

from tkinter import *

root = Tk()
root.title("Skyline results")

label = Label(root, text='>>>Recommended stores in your vicinity based on different criteria<<\n')
for key in fusiondict.keys():
    label = Label(root, text= 'Street: '+str(map_placeid_loc[key][0])+'\n'
                  +'Distance [km]: '+str("%.2f" % resdict[key][2])+'\n'
                  +'Duration [min]: '+str("%.2f" % resdict[key][3])+'\n'
                  +'Utility Score: '+str("%.2f" % resdict[key][6])+'\n'
                  +'Other stores in 2km airline: '+str(resdict[key][5])+'\n'
                  +'Popular times factor: '+str("%.2f" % resdict[key][4])+'\n'
                  +'Link to Google Maps: '+str('https://www.google.com/maps/search/?api=1&query=' + str(resdict[key][0]) + ',' + str(resdict[key][1]))+'\n'
                  +'------------------------------------------------\n')
    # this creates x as a new label to the GUI
    label.pack()


root.mainloop()


fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('Distances [km]')
ax.set_ylabel('Traffic Durations [min]')
ax.set_zlabel('Utility')

volume = (5 * np.asarray(arr_poptimes)) ** 4

dp = np.array(list(dominatedPoints))
pp = np.array(list(paretoPoints))

ax.scatter(dp[:, 0], dp[:, 1], dp[:, 2], color='green')
ax.scatter(pp[:, 0], pp[:, 1], pp[:, 2], color='red')

triang = mtri.Triangulation(pp[:, 0], pp[:, 1])
ax.plot_trisurf(triang, pp[:, 2], color='red', alpha=0.5)

for i in range(len(arr_labels)):  # plot each point + it's index as text above
    ax.scatter(arr_distances[i], arr_durations[i], arr_utility[i], s=volume[i], alpha=0.5)
    ax.text(arr_distances[i], arr_durations[i], arr_utility[i], '%s' % (arr_labels[i][0]), size=8, zorder=1, color='k')

plt.show()