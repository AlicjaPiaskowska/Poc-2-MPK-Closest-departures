import requests
from zipfile import ZipFile
import sqlite3
import pandas as pd
import glob
import os
import shutil
import numpy as np

def delateing_folder_with_data_if_exists(path_data):
    if os.path.exists(path_data):
        shutil.rmtree(path_data)
    else:
        return None

def download_data(URL,fileName,path):
    print("Downloading data from the MPK Wrocław website...")
    # download the data
    response = requests.get(URL)
    # Open the response into a new file called "OtwartyWroclaw_rozklad_jazdy_GTFS.zip"
    open(fileName, "wb").write(response.content)
    # Extract all the files of the zip into a specified location.
    with ZipFile(fileName, "r") as zip_ref:
        zip_ref.extractall(path)
    return(URL)

#convert txt to csv
def replace_txt_to_csv(txt_file_path=""):
    print("Preparation of .csv files...")
    for file_path in glob.glob(txt_file_path):
        new_path = file_path.replace('.txt', '.csv')
        os.rename(file_path, new_path)
    return(file_path)

 
# processing data and uploading them to the database
def load_write_data(path, trips_csv, stops_csv, stop_times_csv, database_name):
    print("Loading csv data into database...")
    conn = sqlite3.connect(database_name)
    trips_csv1 = pd.read_csv(path+"/"+trips_csv)
    stops_csv1 = pd.read_csv(path+"/"+stops_csv)
    stop_times_csv1 = pd.read_csv(path+"/"+stop_times_csv)

    #stop_times_csv1['departure_time'] = stop_times_csv1['departure_time'].replace({'^24:': '00:', '^25:': '01:', '^26:': '02:', '^27:': '03:', '^28:': '04:', '^29:': '05:', '^30:': '06:'},  regex=True)
    #stop_times_csv1['arrival_time'] = stop_times_csv1['arrival_time'].replace({'^24:': '00:', '^25:': '01:', '^26:': '02:', '^27:': '03:', '^28:': '04:', '^29:': '05:', '^30:': '06:'},  regex=True)

    stop_times_csv1['departure_time_MM:SS'] = [x[3:] for x in stop_times_csv1['departure_time']]
    stop_times_csv1['departure_time'] = [int(x[:2])%24 for x in stop_times_csv1['departure_time']]
    stop_times_csv1['departure_time'] = stop_times_csv1['departure_time'].map(str) + ":" + stop_times_csv1['departure_time_MM:SS'].map(str)

    stop_times_csv1['arrival_time_MM:SS'] = [x[3:] for x in stop_times_csv1['arrival_time']]
    stop_times_csv1['arrival_time'] = [int(x[:2])%24 for x in stop_times_csv1['arrival_time']]
    stop_times_csv1['arrival_time'] = stop_times_csv1['arrival_time'].map(str) + ":" + stop_times_csv1['arrival_time_MM:SS'].map(str)

    stops_csv1[['lat_radians','long_radians']] = np.radians(stops_csv1.loc[:,['stop_lat','stop_lon']])
 
    # write the data to a sqlite table
    trips_csv1.to_sql(trips_csv, conn, if_exists='replace', index = False)
    stops_csv1.to_sql(stops_csv, conn, if_exists='replace', index = False)
    stop_times_csv1.to_sql(stop_times_csv, conn, if_exists='replace', index = False)

