import PoC_2_functions as f
from flask import Flask

#https://stackoverflow.com/questions/11994325/how-to-divide-flask-app-into-multiple-py-files
#


URL = "https://www.wroclaw.pl/open-data/87b09b32-f076-4475-8ec9-6020ed1f9ac0/OtwartyWroclaw_rozklad_jazdy_GTFS.zip"
fileName = "./OtwartyWroclaw_rozklad_jazdy_GTFS.zip"
path = "./OtwartyWroclaw_rozklad_jazdy_GTFS"
txt_file_path = "./OtwartyWroclaw_rozklad_jazdy_GTFS/*.txt"


database_name = "PoC_2_wroclaw_mpk.db"

trips_csv = "trips.csv"
stops_csv = "stops.csv"
stop_times_csv = "stop_times.csv"



#Recall of functions
# downloading data and uploading them to the database
# f.download_data(URL, fileName, path)
# f.replace_txt_to_csv(txt_file_path)
# f.creating_database(database_name)
# f.load_write_data(database_name, path, trips_csv, stops_csv, stop_times_csv)

## Collecting user responses
# f.index
# f.user_answers()


## Calculating the distance and providing a table with the final results
f.sql_query(database_name)
f.dataframe_start_point()
f.dataframe_end_point()
f.dataframe_data_from_db()
f.distance_start_point_to_stops()
f.distance_end_point_to_stops()
f.distance_start_end_direction()
f.table_with_routes()
