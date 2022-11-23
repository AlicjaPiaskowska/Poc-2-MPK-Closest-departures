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
    # write the data to a sqlite table
    trips_csv1.to_sql(trips_csv, conn, if_exists='replace', index = False)
    stops_csv1.to_sql(stops_csv, conn, if_exists='replace', index = False)
    stop_times_csv1.to_sql(stop_times_csv, conn, if_exists='replace', index = False)


#Extracting data necessary for the operation of the application from the database
def sql_query(database_name):
    global df_sql_query
    database_name =database_name
    conn = sqlite3.connect(database_name)
    df_sql_query = pd.read_sql_query("select stop_lat as x, stop_lon as y, s.stop_id, arrival_time, departure_time, stop_name, stop_sequence,t.trip_id,trip_headsign,direction_id from 'stop_times.csv' as st left join 'stops.csv' as s on st.stop_id = s.stop_id left join 'trips.csv' as t on st.trip_id = t.trip_id ", conn)
    return(df_sql_query, database_name)
#print(df_sql_query.dtypes)

#user responses from the form
#@app.route('/', methods=['GET', 'POST'])
def user_answers():
    global age
    global data_start_point
    global data_end_point
    global departure_time_user
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
    # today = datetime.time.today()

    x = float(request.form['start_x'])
    y = float(request.form['start_y'])
    data_start_point = [[1, x, y]]
    x_end = float(request.form['end_x'])
    y_end = float(request.form['end_y'])
    data_end_point = [[1, x_end, y_end]]
    return age, departure_time_user, data_start_point, data_end_point


#Creating a data frame from a user-specified starting point
def dataframe_start_point():
    user_answers()
    global df_input_data_start_point
    #data frame start point
    df_input_data_start_point = pd.DataFrame(data_start_point, columns = ['id', 'x', 'y'])
    #Insert new columns with radians for lat-lon to dataframes using np.radians
    df_input_data_start_point[['lat_radians_X_start_point','long_radians_X_start_point']] = (np.radians(df_input_data_start_point.loc[:,['x','y']]))
    #return(df_input_data_start_point, df_data_from_db)
    #print(str(df_input_data_start_point))
    return(df_input_data_start_point)

#Creating a data frame from a user-specified endpoint
def dataframe_end_point():
    user_answers()
    global df_input_data_end_point
    #data frame end point
    df_input_data_end_point = pd.DataFrame(data_end_point, columns = ['id', 'x_end', 'y_end'])
    #Insert new columns with radians for lat-lon to dataframes using np.radians
    df_input_data_end_point[['lat_radians_X_end_point','long_radians_X_end_point']] = (np.radians(df_input_data_end_point.loc[:,['x_end','y_end']]))
    #return(df_input_data_end_point, df_data_from_db)
    #print(df_input_data_end_point)
    return(df_input_data_end_point)

# Creating a dataframe from data from the database
def dataframe_data_from_db(database_name):
    sql_query(database_name)
    global df_data_from_db
    #data frame data from db
    df_data_from_db = df_sql_query
    #Insert new columns with radians for lat-lon to dataframes using np.radians
    df_data_from_db[['lat_radians_Y','long_radians_Y']] = (np.radians(df_data_from_db.loc[:,['x','y']]))
    return(df_data_from_db)


#Calculating the distance from the starting point to the stops
def distance_start_point_to_stops():
    dataframe_start_point()
    dataframe_data_from_db(database_name)
    print("Calculating the distance from the starting point to the stops...")
    global df_with_distance_start_point
    #distance from starting point to stops
    dist = sklearn.metrics.DistanceMetric.get_metric('haversine')
    dist_matrix_start_point = (dist.pairwise
                (df_input_data_start_point[['lat_radians_X_start_point','long_radians_X_start_point']],
                df_data_from_db[['lat_radians_Y','long_radians_Y']])*6371)   

    #print(dist_matrix)
    df_dist_matrix_start_point = (pd.DataFrame(dist_matrix_start_point,index=df_input_data_start_point['id'], columns=df_data_from_db['stop_id']))
    #print(df_dist_matrix)
    #unpivot dataframe
    df_dist_unpv_start_point = (pd.melt(df_dist_matrix_start_point.reset_index(),id_vars='id'))
    #Rename  column
    df_dist_unpv_start_point= df_dist_unpv_start_point.rename(columns={'value':'distance'})
    df_dist_unpv_start_point = df_dist_unpv_start_point[(df_dist_unpv_start_point['distance'] <= 5)]
    #print(df_dist_unpv_start_point)
    df_with_distance_start_point = pd.merge(df_data_from_db, df_dist_unpv_start_point,  how='right', left_on=['stop_id'], right_on = ['stop_id'])
    # changing_formats start point
    df_with_distance_start_point['departure_time'] = df_with_distance_start_point['departure_time'].replace({'^24:': '00:', '^25:': '01:', '^26:': '02:', '^27:': '03:', '^28:': '04:', '^29:': '05:', '^30:': '06:'},  regex=True)
    df_with_distance_start_point['departure_time'] = pd.to_datetime(df_with_distance_start_point['departure_time'], format='%H:%M:%S').dt.time
    #df_with_distance_start_point = df_with_distance_start_point.sort_values(by=['distance', 'departure_time'])
    #pd.DataFrame(df_with_distance_start_point).to_csv("C:/Users/apiaskow/Desktop/Python_codes/PoC_2/df_with_distance_start_point.csv")
    return(df_with_distance_start_point)

#Calculating the distance from the end point to the stops
def distance_end_point_to_stops():
    dataframe_end_point()
    print("Calculating the distance from the end point to the nearest stop...")
    global df_with_distance_end_point
    #odległosć punktu końcowego do najbliższego przystanku
    dist = sklearn.metrics.DistanceMetric.get_metric('haversine')
    dist_matrix_end_point = (dist.pairwise
                (df_input_data_end_point[['lat_radians_X_end_point','long_radians_X_end_point']],
                df_data_from_db[['lat_radians_Y','long_radians_Y']])*6371)   

    #print(dist_matrix)
    df_dist_matrix_end_point = (pd.DataFrame(dist_matrix_end_point,index=df_input_data_end_point['id'], columns=df_data_from_db['stop_id']))
    #print(df_dist_matrix)
    #unpivot dataframe
    df_dist_unpv_end_point = (pd.melt(df_dist_matrix_end_point.reset_index(),id_vars='id'))
    #Rename  column 
    df_dist_unpv_end_point= df_dist_unpv_end_point.rename(columns={'value':'distance_to_end_point'})
    df_dist_unpv_end_point = df_dist_unpv_end_point[(df_dist_unpv_end_point['distance_to_end_point'] <= 1)]
    df_with_distance_end_point = pd.merge(df_data_from_db, df_dist_unpv_end_point,  how='right', left_on=['stop_id'], right_on = ['stop_id'])
    
    # changing_formats end point   
    df_with_distance_end_point['arrival_time'] = df_with_distance_end_point['arrival_time'].replace({'^24:': '00:', '^25:': '01:', '^26:': '02:', '^27:': '03:', '^28:': '04:', '^29:': '05:', '^30:': '06:'},  regex=True)
    df_with_distance_end_point['arrival_time'] = pd.to_datetime(df_with_distance_end_point['arrival_time'], format='%H:%M:%S').dt.time
    #df_with_distance_end_point = df_with_distance_end_point.sort_values(by=['distance_to_end_point', 'arrival_time'])
    df_with_distance_end_point = df_with_distance_end_point[['x', 'y', 'stop_id', 'arrival_time', 'trip_id', 'stop_name', 'stop_sequence','direction_id', 'trip_headsign','distance_to_end_point']]
    #print(df_with_distance_end_point)
    #pd.DataFrame(df_with_distance_end_point).to_csv("C:/Users/apiaskow/Desktop/Python_codes/PoC_2/df_with_distance_end_point.csv")
    return(df_with_distance_end_point)

#Preparing information about if we are going in the right direction
def distance_start_end_direction():
    distance_start_point_to_stops()
    distance_end_point_to_stops()
    print("Preparation of the distance along with the direction of travel...")
    global df_direction
    # end_stop_and_direction(df_with_distance):
    df_direction = pd.merge(df_with_distance_start_point, df_with_distance_end_point,  how='inner', left_on=['trip_id','direction_id'], right_on = ['trip_id','direction_id'])
    df_direction = df_direction.sort_values(by=['distance', 'departure_time', 'distance_to_end_point'])
    #pd.DataFrame(df_direction).to_csv("C:/Users/apiaskow/Desktop/Python_codes/PoC_2/df_direction.csv")
    #print(df_direction)
    return(df_direction)

#Creating a final table taking into account the criteria of age (distance from the starting point), departure time and the right direction
@app.route('/', methods=['GET', 'POST'])
def table_with_routes():
    distance_start_end_direction()
    user_answers()
    if 0 <= age <= 15:
        df_filter_dist_time = df_direction[(df_direction['distance'] <= 1) & (df_direction['departure_time'] >= departure_time_user) & (df_direction['stop_sequence_x'] < df_direction['stop_sequence_y'] )]
        df_filter_dist_time = df_filter_dist_time.drop_duplicates(subset=['stop_id_x'])
        df_filter_dist_time = df_filter_dist_time[['stop_name_x', 'departure_time','distance', 'arrival_time_y', 'stop_name_y', 'distance_to_end_point']]
        df_filter_dist_time=df_filter_dist_time.iloc[:5]
        print("The end result is: ")
        print(df_filter_dist_time)
        #pd.DataFrame(df_filter_dist_time).to_csv("C:/Users/apiaskow/Desktop/Python_codes/PoC_2/mask.csv")
        return render_template('index.html', tables=[df_filter_dist_time.to_html(classes='data', header="true")])
    elif 16 <= age <= 25:
        df_filter_dist_time = df_direction[(df_direction['distance'] <= 5) & (df_direction['departure_time'] >= departure_time_user) & (df_direction['stop_sequence_x'] < df_direction['stop_sequence_y'])]
        df_filter_dist_time = df_filter_dist_time.drop_duplicates(subset=['stop_id_x'])
        df_filter_dist_time = df_filter_dist_time[['stop_name_x', 'departure_time','distance','stop_name_y', 'arrival_time_y', 'distance_to_end_point']]
        df_filter_dist_time.columns = ['closest start stop', 'departure time', 'distance [km]', 'closest end stop', 'arrival time', 'distance to end point [km]']
        df_filter_dist_time=df_filter_dist_time.iloc[:5]
        #pd.DataFrame(df_filter_dist_time).to_csv("C:/Users/apiaskow/Desktop/Python_codes/PoC_2/mask_24.csv")
        print("The end result is: ")
        print(df_filter_dist_time)
        return render_template('index.html', tables=[df_filter_dist_time.to_html(classes='data', header="true")])
        #return(df_filter_dist_time)
        #return render_template('index.html',output=df_filter_dist_time)
    elif 26 <= age <= 35:
        df_filter_dist_time = df_direction[(df_direction['distance'] <= 2) & (df_direction['departure_time'] >= departure_time_user) & (df_direction['stop_sequence_x'] < df_direction['stop_sequence_y'] )]
        df_filter_dist_time = df_filter_dist_time.drop_duplicates(subset=['stop_id_x'])
        df_filter_dist_time = df_filter_dist_time[['stop_name_x', 'departure_time','distance', 'arrival_time_y', 'stop_name_y', 'distance_to_end_point']]
        df_filter_dist_time=df_filter_dist_time.iloc[:5]
        print("The end result is: ")
        print(df_filter_dist_time)
        return render_template('index.html', tables=[df_filter_dist_time.to_html(classes='data', header="true")])  
        #pd.DataFrame(df_filter_dist_time).to_csv("C:/Users/apiaskow/Desktop/Python_codes/PoC_2/mask.csv")
    elif 36 <= age <= 50:
        df_filter_dist_time = df_direction[(df_direction['distance'] <= 1) & (df_direction['departure_time'] >= departure_time_user) & (df_direction['stop_sequence_x'] < df_direction['stop_sequence_y'] )]
        df_filter_dist_time = df_filter_dist_time.drop_duplicates(subset=['stop_id_x'])
        df_filter_dist_time = df_filter_dist_time[['stop_name_x', 'departure_time','distance', 'arrival_time_y', 'stop_name_y', 'distance_to_end_point']]
        df_filter_dist_time=df_filter_dist_time.iloc[:5]
        print("The end result is: ")       
        print(df_filter_dist_time)
        return render_template('index.html', tables=[df_filter_dist_time.to_html(classes='data', header="true")])
        #pd.DataFrame(df_filter_dist_time).to_csv("C:/Users/apiaskow/Desktop/Python_codes/PoC_2/mask.csv")
    elif 51 <= age <= 65:
        df_filter_dist_time = df_direction[(df_direction['distance'] <= 0.5) & (df_direction['departure_time'] >= departure_time_user) & (df_direction['stop_sequence_x'] < df_direction['stop_sequence_y'] )]
        df_filter_dist_time = df_filter_dist_time.drop_duplicates(subset=['stop_id_x'])
        df_filter_dist_time = df_filter_dist_time[['stop_name_x', 'departure_time','distance', 'arrival_time_y', 'stop_name_y', 'distance_to_end_point']]
        df_filter_dist_time=df_filter_dist_time.iloc[:5]
        print("The end result is: ")
        print(df_filter_dist_time)
        return render_template('index.html', tables=[df_filter_dist_time.to_html(classes='data', header="true")])
        #pd.DataFrame(df_filter_dist_time).to_csv("C:/Users/apiaskow/Desktop/Python_codes/PoC_2/mask.csv")
    else:
        df_filter_dist_time = df_direction[(df_direction['distance'] <= 0.1) & (df_direction['departure_time'] >= departure_time_user) & (df_direction['stop_sequence_x'] < df_direction['stop_sequence_y'] )]
        df_filter_dist_time = df_filter_dist_time.drop_duplicates(subset=['stop_id_x'])
        df_filter_dist_time = df_filter_dist_time[['stop_name_x', 'departure_time','distance', 'arrival_time_y', 'stop_name_y', 'distance_to_end_point']]
        df_filter_dist_time=df_filter_dist_time.iloc[:5]
        print("The end result is: ")
        print(df_filter_dist_time)
        return render_template('index.html', tables=[df_filter_dist_time.to_html(classes='data', header="true")])



def run_app():
    return app.run(debug=True)
