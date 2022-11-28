import requests
from zipfile import ZipFile
import sqlite3
import pandas as pd
import numpy as np
import sklearn.metrics
import glob
import os
from datetime import datetime
from flask import Flask, render_template, request
import shutil
import math

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


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

#database creation and database connection
def database_name_function(database_name_):
  global database_name
  database_name = database_name_
  return database_name


def creating_database():
    print("Database creation...")
    conn = sqlite3.connect(database_name)
    c = conn.cursor()

# processing data and uploading them to the database
def load_write_data(path, trips_csv, stops_csv, stop_times_csv):
    print("Loading csv data into database...")
    conn = sqlite3.connect(database_name)
    trips_csv1 = pd.read_csv(path+"/"+trips_csv)
    stops_csv1 = pd.read_csv(path+"/"+stops_csv)
    stop_times_csv1 = pd.read_csv(path+"/"+stop_times_csv)

    stop_times_csv1['departure_time'] = stop_times_csv1['departure_time'].replace({'^24:': '00:', '^25:': '01:', '^26:': '02:', '^27:': '03:', '^28:': '04:', '^29:': '05:', '^30:': '06:'},  regex=True)
    stop_times_csv1['arrival_time'] = stop_times_csv1['arrival_time'].replace({'^24:': '00:', '^25:': '01:', '^26:': '02:', '^27:': '03:', '^28:': '04:', '^29:': '05:', '^30:': '06:'},  regex=True)

    # write the data to a sqlite table
    trips_csv1.to_sql(trips_csv, conn, if_exists='replace', index = False)
    stops_csv1.to_sql(stops_csv, conn, if_exists='replace', index = False)
    stop_times_csv1.to_sql(stop_times_csv, conn, if_exists='replace', index = False)


#Extracting data necessary for the operation of the application from the database
def sql_query(database_name):
    conn = sqlite3.connect(database_name)
    df_sql_query = pd.read_sql_query("select stop_lat as x, stop_lon as y, s.stop_id, arrival_time, departure_time, stop_name, stop_sequence,t.trip_id,trip_headsign,direction_id from 'stop_times.csv' as st left join 'stops.csv' as s on st.stop_id = s.stop_id left join 'trips.csv' as t on st.trip_id = t.trip_id ", conn)
    return(df_sql_query)

#print(df_sql_query.dtypes)

#user responses from the form
@app.route('/', methods=['GET'])
def user_answers():
    age = int(request.form['age'])
    now = datetime.now()
    current_hour = now.strftime("%H")
    current_minute = now.strftime("%M")

    #preparing of time. if user don't give value that return current time
    time_hour = request.form['time_hour']  
    if time_hour:
        time_hour = time_hour
    if not time_hour:
        time_hour = current_hour

    time_minute = request.form['time_minute']
    if time_minute:
        time_minute = time_minute
    if not time_minute:
        time_minute = current_minute

    departure_time_user = str(time_hour)+':'+str(time_minute) + ':00'
    departure_time_user = datetime.strptime(departure_time_user, '%H:%M:%S').time()

    latitude = float(request.form['start_x'])
    longitude = float(request.form['start_y'])

    latitude_end_point = float(request.form['end_x'])
    longitude_end_point = float(request.form['end_y'])

    return age, departure_time_user, latitude, longitude, latitude_end_point, longitude_end_point

def make_radian():
    coordinates = user_answers()
    latitude_radian = math.radians(coordinates[2])
    longitude_radian = math.radians(coordinates[3])
    latitude_radian_end_point = math.radians(coordinates[4])
    longitude_radian_end_point = math.radians(coordinates[5])
    return latitude_radian, longitude_radian, latitude_radian_end_point, longitude_radian_end_point

# Creating a dataframe from data from the database
def dataframe_data_from_db(database_name):
    df_sql_query = sql_query(database_name)
    #data frame data from db
    df_data_from_db = df_sql_query
    #Insert new columns with radians for lat-lon to dataframes using np.radians
    df_data_from_db[['lat_radians_Y','long_radians_Y']] = (np.radians(df_data_from_db.loc[:,['x','y']]))
    #df_data_from_db['arrival_time'] = pd.to_datetime(df_data_from_db['arrival_time'], format='%H:%M:%S').dt.time
    #df_data_from_db['departure_time'] = pd.to_datetime(df_data_from_db['departure_time'], format='%H:%M:%S').dt.time
    #df_data_from_db = df_data_from_db[df_data_from_db['departure_time']>= departure_time_user]
    return(df_data_from_db)


#Calculating the distance from the starting point to the stops
def distance_start_point_to_stops():
    df_data_from_db = dataframe_data_from_db(database_name)
    #make_radian()
    radian = make_radian()
    print("Calculating the distance from the starting point to the stops...")
    #distance from starting point to stops
    dist = sklearn.metrics.DistanceMetric.get_metric('haversine')
    dist_matrix_start_point = (dist.pairwise
                ([(radian[0], radian[1])],
                df_data_from_db[['lat_radians_Y','long_radians_Y']])*6371)   

    print("dist_matrix_start_point")
    print(dist_matrix_start_point)
    #print(dist_matrix)
    df_dist_matrix_start_point = (pd.DataFrame(dist_matrix_start_point, columns=df_data_from_db['stop_id']))
    print(df_dist_matrix_start_point)
    # #unpivot dataframe
    df_dist_unpv_start_point = (pd.melt(df_dist_matrix_start_point.reset_index()))
    print(df_dist_unpv_start_point)
    # #Rename  column
    df_dist_unpv_start_point= df_dist_unpv_start_point.rename(columns={'value':'distance'})
    print("df_dist_unpv_start_point")
    print(df_dist_unpv_start_point)
    df_dist_unpv_start_point = df_dist_unpv_start_point[(df_dist_unpv_start_point['distance'] <= 5)]
    # #print(df_dist_unpv_start_point)
    df_with_distance_start_point = pd.merge(df_data_from_db, df_dist_unpv_start_point,  how='right', left_on=['stop_id'], right_on = ['stop_id'])
    print("df_with_distance_start_point")
    print(df_with_distance_start_point)
    # # changing_formats start point
    df_with_distance_start_point['departure_time'] = pd.to_datetime(df_with_distance_start_point['departure_time'], format='%H:%M:%S').dt.time
    #print(df_with_distance_start_point)
    return(df_with_distance_start_point)

#Calculating the distance from the end point to the stops
def distance_end_point_to_stops():
    df_data_from_db = dataframe_data_from_db(database_name)
    #make_radian()
    radian_end_point = make_radian()
    print("Calculating the distance from the end point to the nearest stop...")
    #odległosć punktu końcowego do najbliższego przystanku
    dist = sklearn.metrics.DistanceMetric.get_metric('haversine')
    print("tworzenie macierzy odległości")
    dist_matrix_end_point = (dist.pairwise
                ([(radian_end_point[2], radian_end_point[3])],
                df_data_from_db[['lat_radians_Y','long_radians_Y']])*6371)   
    print("tworzenie data frame z odlełościami")
    #print(dist_matrix)
    df_dist_matrix_end_point = (pd.DataFrame(dist_matrix_end_point, columns=df_data_from_db['stop_id']))
    #print(df_dist_matrix)
    print("unpivotowanie")
    #unpivot dataframe
    df_dist_unpv_end_point = (pd.melt(df_dist_matrix_end_point.reset_index()))
    #Rename  column 
    print("zmiana nazwy")
    df_dist_unpv_end_point= df_dist_unpv_end_point.rename(columns={'value':'distance_to_end_point'})
    print("selekcja dystansu:")
    df_dist_unpv_end_point = df_dist_unpv_end_point[(df_dist_unpv_end_point['distance_to_end_point'] <= 1)]
    print("mergowanie")
    df_with_distance_end_point = pd.merge(df_data_from_db, df_dist_unpv_end_point,  how='right', left_on=['stop_id'], right_on = ['stop_id'])
    
    # changing_formats end point   
    df_with_distance_end_point = df_with_distance_end_point[['x', 'y', 'stop_id', 'arrival_time', 'trip_id', 'stop_name', 'stop_sequence','direction_id', 'trip_headsign','distance_to_end_point']]
    #print(df_with_distance_end_point)
    #pd.DataFrame(df_with_distance_end_point).to_csv("C:/Users/apiaskow/Desktop/Python_codes/PoC_2/df_with_distance_end_point.csv")
    return(df_with_distance_end_point)

#Preparing information about if we are going in the right direction
def distance_start_end_direction():
    df_with_distance_start_point = distance_start_point_to_stops()
    df_with_distance_end_point = distance_end_point_to_stops()
    print("Preparation of the distance along with the direction of travel...")
    df_direction = pd.merge(df_with_distance_start_point, df_with_distance_end_point,  how='inner', left_on=['trip_id','direction_id'], right_on = ['trip_id','direction_id'])
    df_direction = df_direction.sort_values(by=['distance', 'departure_time', 'distance_to_end_point'])
    #pd.DataFrame(df_direction).to_csv("C:/Users/apiaskow/Desktop/Python_codes/PoC_2/df_direction.csv")
    #print(df_direction)
    return(df_direction)

#Creating a final table taking into account the criteria of age (distance from the starting point), departure time and the right direction
@app.route('/', methods=['POST'])
def table_with_routes():
    df_direction = distance_start_end_direction()
    data_form_user = user_answers()
    if 0 <= data_form_user[0] <= 15:
        allowed_distance = 1
    elif 16 <= data_form_user[0] <= 25:
        allowed_distance = 5
    elif 26 <= data_form_user[0] <= 35:
        allowed_distance = 2
    elif 36 <= data_form_user[0] <= 50:
        allowed_distance = 1
    elif 51 <= data_form_user[0] <= 65:
        allowed_distance = 0.5
    else:
        allowed_distance = 0.1
    df_filter_dist_time = df_direction[(df_direction['distance'] <= allowed_distance) & (df_direction['departure_time'] >= data_form_user[1]) & (df_direction['stop_sequence_x'] < df_direction['stop_sequence_y'] )]
    df_filter_dist_time = df_filter_dist_time.drop_duplicates(subset=['stop_id_x'])
    df_filter_dist_time = df_filter_dist_time[['stop_name_x', 'departure_time','distance', 'arrival_time_y', 'stop_name_y', 'distance_to_end_point']]
    df_filter_dist_time=df_filter_dist_time.iloc[:5]
    print("The end result is: ")
    print(df_filter_dist_time)
    #pd.DataFrame(df_filter_dist_time).to_csv("C:/Users/apiaskow/Desktop/Python_codes/PoC_2/mask.csv")
    return render_template('index.html', tables=[df_filter_dist_time.to_html(classes='data', header="true")])

def run_app():
    return app.run(debug=True)
