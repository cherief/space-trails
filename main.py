"""
Script to get ISS pass notifications using Pushover.
"""

__author__ = "cherief"
__version__ = "1.0"

from bs4 import BeautifulSoup
import numpy as np
import requests
import pandas as pd
import datetime as dt
import datefinder
import httplib, urllib
import os


if __name__ == "__main__":

    path = ""

    # get url
    url_iss = "http://heavens-above.com/PassSummary.aspx?satid=25544&lat=-35.282&lng=149.1287&loc=Canberra&alt=577&tz=AEST"

    r = requests.get(url_iss)

    soup = BeautifulSoup(r.text)

    table_class = "standardTable"

    data = soup.find_all('tr',{'class':"clickableRow"})
    
    # create empty lists
    date,magnitude,start_time,highest_time,highest_altitude,end_time = [],[],[],[],[],[]

    for d in data:

        # 0 date
        tmp_date = d.contents[0].get_text().encode('utf8')
        date.append(tmp_date)
        
        # 1 magnitude
        magnitude.append(float(d.contents[1].get_text().encode('utf8')))

        # 2
        tmp = d.contents[2].get_text().encode('utf8')
        tmp = tmp_date + " " + tmp
        matches = datefinder.find_dates(tmp)
        for match in matches:
            tmp = match
        start_time.append(tmp)

        # 3

        # 4

        # 5 time of highest altitude
        tmp = d.contents[5].get_text().encode('utf8')
        tmp = tmp_date + " " + tmp
        matches = datefinder.find_dates(tmp)
        for match in matches:
            tmp = match
        highest_time.append(tmp)

        # 6 highest altitude
        highest_altitude.append(float(d.contents[6].get_text().encode('utf8')[:-2]))

        # 7 end time
        tmp = d.contents[8].get_text().encode('utf8')
        tmp = tmp_date + " " + tmp
        matches = datefinder.find_dates(tmp)
        for match in matches:
            tmp = match        
        end_time.append(tmp)

    # create table
    columns = {'date': date, 'magnitude': magnitude, 'start_time': start_time, 'highest_time': highest_time, 'highest_altitude': highest_altitude,'end_time': end_time}

    # add table to pandas dataframe
    df = pd.DataFrame(columns)

    # don't make columns wrap in terminal
    pd.set_option('expand_frame_repr', False)

    # filter ISS passes by magnitude and highest altitude
    results = df.query('magnitude < 4.5 and highest_altitude > 40')

    # get today's date
    today = dt.date.today()

    # find date of first pass listed
    s = results['date']
    matches = datefinder.find_dates(s.iloc[0])

    for m,match in enumerate(matches):
        # find pass date that matches today's date and is after 5pm
        if (match.day == today.day) and (match.month == today.month) and (results['highest_time'].iloc[m].hour > 17): # must be a better way of doing this
            # create message for Pushover to send
            message = "ISS will pass over today at {1}:{2} with a magnitude of {0}.".format(results['magnitude'].iloc[m],results['highest_time'].iloc[m].hour,results['highest_time'].iloc[m].minute)
        else:
            message = "No ISS passes are visible this evening."

    # load token and user for Pushover
    token,user = np.loadtxt(os.path.join(path,"pushover"),dtype="str",unpack=True) 

    # send pushover notification of new ISS pass
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.urlencode({
        "token": token,
        "user": user,
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()







