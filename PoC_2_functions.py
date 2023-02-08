import sqlite3
import pandas as pd
import sklearn.metrics
from datetime import datetime
from flask import Flask, render_template, request
import math


app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

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


#Extracting data necessary for the operation of the application from the database
def sql_query():
    print("Execute query...")
    conn = sqlite3.connect("PoC_2_wroclaw_mpk.db")
    cur = conn.cursor()
    list_of_point = cur.execute("""
        SELECT 
            stop_lat AS x, 
            stop_lon AS y, 
            s.stop_id, 
            arrival_time AS arrival_time, 
            departure_time AS departure_time, 
            stop_name, 
            stop_sequence,
            t.trip_id,
            trip_headsign,
            direction_id, 
            lat_radians, 
            long_radians 
        FROM 'stop_times.csv' AS st 
        LEFT JOIN 'stops.csv' AS s 
            ON st.stop_id = s.stop_id 
        LEFT JOIN 'trips.csv' AS t 
            ON st.trip_id = t.trip_id""")
    return list_of_point  

earth_radius = 6271.0
degrees_to_radians = math.pi/180.0
radians_to_degrees = 180.0/math.pi

def change_in_latitude(kms):
    #"Given a distance north, return the change in latitude."
    return (kms/earth_radius)*radians_to_degrees

def change_in_longitude(latitude, kms):
    #"Given a latitude and a distance west, return the change in longitude."
    # Find the radius of a circle around the earth at given latitude.
    r = earth_radius*math.cos(latitude*degrees_to_radians)
    return (kms/r)*radians_to_degrees

def change_in_longitude_end_point(latitude_end_point, kms):
    #"Given a latitude and a distance west, return the change in longitude."
    # Find the radius of a circle around the earth at given latitude.
    r = earth_radius*math.cos(latitude_end_point*degrees_to_radians)
    return (kms/r)*radians_to_degrees


def create_squares():
    print("Create square with 5 km radius...")
    coordinates = user_answers()
    radius = 5
    slat = coordinates[2]+change_in_latitude(-radius)
    nlat = coordinates[2]+change_in_latitude(radius)
    wlon = coordinates[3]+change_in_longitude(coordinates[2],-radius)
    elon = coordinates[3]+change_in_longitude(coordinates[2], radius)

    slat_end_point = coordinates[4]+change_in_latitude(-radius)
    nlat_end_point = coordinates[4]+change_in_latitude(radius)
    wlon_end_point = coordinates[5]+change_in_longitude_end_point(coordinates[4],-radius)
    elon_end_point = coordinates[5]+change_in_longitude_end_point(coordinates[4], radius)

    bottom_left = (slat, wlon)
    top_right = (nlat, elon)

    bottom_left_end_point = (slat_end_point, wlon_end_point)
    top_right_end_point = (nlat_end_point, elon_end_point)
    print("End create square...")
    return(bottom_left, top_right, bottom_left_end_point, top_right_end_point)


def select_stops_radius():
    list_of_point = sql_query()
    corner = create_squares()
    print("Select stops within radius...")
    cols = ['x', 'y', 'stop_id', 'arrival_time', 'departure_time', 'stop_name', 'stop_sequence', 'trip_id', 'trip_headsign' ,'direction_id', 'lat_radians', 'long_radians']
    data = []
    for p in list_of_point:
        if (float(p[0]) > corner[0][0] and float(p[0]) < corner[1][0] and float(p[0]) > corner[0][1] and float(p[1]) < corner[1][1]) :
            data.append(p)
            continue
        elif (float(p[0]) > corner[2][0] and float(p[0]) < corner[3][0] and float(p[0]) > corner[2][1] and float(p[1]) < corner[3][1]) :
            data.append(p)
            continue
        else:
            continue
    data_within_radius = pd.DataFrame(data, columns=cols)
    print("End Select stops within radius...")
    return(data_within_radius)


def make_radian():
    print("Make radians from coordinates...")
    coordinates = user_answers()
    latitude_radian = math.radians(coordinates[2])
    longitude_radian = math.radians(coordinates[3])
    latitude_radian_end_point = math.radians(coordinates[4])
    longitude_radian_end_point = math.radians(coordinates[5])
    print("End Make radians from coordinates...")
    return latitude_radian, longitude_radian, latitude_radian_end_point, longitude_radian_end_point

#def distance_matrix():
def end_start_point_dist():
    print("Create distance to stops...")
    data_within_radius = select_stops_radius()
    radian = make_radian()

    column_name = ['x', 'y', 'stop_id', 'arrival_time', 'departure_time', 'stop_name', 'stop_sequence', 'trip_id', 'trip_headsign' ,'direction_id','lat_radians', 'long_radians']

    dist = sklearn.metrics.DistanceMetric.get_metric('haversine')

    dist_matrix_start_point = (dist.pairwise
                ([(radian[0], radian[1])],
                data_within_radius[['lat_radians', 'long_radians']])*6371)   

    dist_matrix_end_point = (dist.pairwise
                ([(radian[2], radian[3])],
                data_within_radius[['lat_radians', 'long_radians']])*6371)
    
    
    print("Create data frame with distance...")
    df_dist_matrix_start_point = (pd.DataFrame(dist_matrix_start_point, columns=data_within_radius[column_name]))
    df_dist_matrix_end_point = (pd.DataFrame(dist_matrix_end_point, columns=data_within_radius[column_name]))

    # #unpivot dataframe
    df_dist_unpv_start_point = (pd.melt(df_dist_matrix_start_point).reset_index())
    df_dist_unpv_end_point = (pd.melt(df_dist_matrix_end_point).reset_index())

    # #Rename column
    print("Rename columns...")
    df_dist_unpv_start_point= df_dist_unpv_start_point.rename(columns={'value':'distance'})
    df_dist_unpv_end_point= df_dist_unpv_end_point.rename(columns={'value':'distance_to_end_point'})

    #selection distance 
    df_dist_unpv_start_point = df_dist_unpv_start_point[(df_dist_unpv_start_point['distance'] <= 5)]
    df_dist_unpv_end_point = df_dist_unpv_end_point[(df_dist_unpv_end_point['distance_to_end_point'] <= 5)]
    
    print("Change value to list...")
    #print(df_dist_unpv_start_point)
    df_dist_unpv_start_point[column_name] = pd.DataFrame(df_dist_unpv_start_point['variable'].values.tolist(), index=df_dist_unpv_start_point.index)
    df_dist_unpv_end_point[column_name] = pd.DataFrame(df_dist_unpv_end_point['variable'].values.tolist(), index=df_dist_unpv_end_point.index)
    print("Change time format...")
    df_dist_unpv_start_point['departure_time'] = pd.to_datetime(df_dist_unpv_start_point['departure_time'], format='%H:%M:%S').dt.time
    df_dist_unpv_end_point['arrival_time'] = pd.to_datetime(df_dist_unpv_end_point['arrival_time'], format='%H:%M:%S').dt.time

    return(df_dist_unpv_start_point, df_dist_unpv_end_point)

#def end_start_point_dist():


#Preparing information about if we are going in the right direction
def distance_start_end_direction():
    # start_end = end_start_point_dist()
    distance = end_start_point_dist()
    print("Prepare distance along with the direction of travel...")
    df_direction = pd.merge(distance[0], distance[1],  how='inner', left_on=['trip_id','direction_id'], right_on = ['trip_id','direction_id'])
    #print(df_direction)
    #print(df_direction)
    df_direction = df_direction.sort_values(by=['distance', 'departure_time_x', 'distance_to_end_point'])
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
    
    df_filter_dist_time = (df_direction[(df_direction['distance'] <= allowed_distance) 
                            & (df_direction['departure_time_x'] >= data_form_user[1]) 
                            & (df_direction['stop_sequence_x'] < df_direction['stop_sequence_y'] )])
                            
    df_filter_dist_time = df_filter_dist_time.drop_duplicates(subset=['stop_id_x'])
    df_filter_dist_time = df_filter_dist_time[['stop_name_x', 'departure_time_x','distance', 'arrival_time_y', 'stop_name_y', 'distance_to_end_point']]
    df_filter_dist_time=df_filter_dist_time.iloc[:5]
    print("Final result in the screen...")
    return render_template('index.html', tables=[df_filter_dist_time.to_html(classes='data', header="true")])

def run_app():
    return app.run(debug=True)

