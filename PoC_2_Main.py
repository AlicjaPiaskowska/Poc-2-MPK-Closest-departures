import PoC_2_functions as f

#https://stackoverflow.com/questions/11994325/how-to-divide-flask-app-into-multiple-py-files
# https://code.visualstudio.com/docs/python/tutorial-flask 


URL = "https://www.wroclaw.pl/open-data/87b09b32-f076-4475-8ec9-6020ed1f9ac0/OtwartyWroclaw_rozklad_jazdy_GTFS.zip"
fileName = "./OtwartyWroclaw_rozklad_jazdy_GTFS.zip"
path_data = "./OtwartyWroclaw_rozklad_jazdy_GTFS"
txt_file_path = "./OtwartyWroclaw_rozklad_jazdy_GTFS/*.txt"

database_name_ = "PoC_2_wroclaw_mpk.db"

trips_csv = "trips.csv"
stops_csv = "stops.csv"
stop_times_csv = "stop_times.csv"


#Recall of functions
# downloading data and uploading them to the database

f.delateing_folder_with_data_if_exists(path_data)
f.download_data(URL, fileName, path_data)
f.replace_txt_to_csv(txt_file_path)

f.database_name_function(database_name_)

f.creating_database()
f.load_write_data(path_data, trips_csv, stops_csv, stop_times_csv)

## Collecting user responses
print("Please go to http link")
f.run_app()
f.user_answers()

## Calculating the distance and providing a table with the final results
f.sql_query()
f.dataframe_start_point()
f.dataframe_end_point()
f.dataframe_data_from_db()
f.distance_start_point_to_stops()
f.distance_end_point_to_stops()
f.distance_start_end_direction()
f.table_with_routes()

