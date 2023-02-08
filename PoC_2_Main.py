import PoC_2_functions as f
import PoC_2_functions_downloading_data as fdd
#https://stackoverflow.com/questions/11994325/how-to-divide-flask-app-into-multiple-py-files
# https://code.visualstudio.com/docs/python/tutorial-flask 

URL = "https://www.wroclaw.pl/open-data/87b09b32-f076-4475-8ec9-6020ed1f9ac0/OtwartyWroclaw_rozklad_jazdy_GTFS.zip"
fileName = "./OtwartyWroclaw_rozklad_jazdy_GTFS.zip"
path_data = "./OtwartyWroclaw_rozklad_jazdy_GTFS"
txt_file_path = "./OtwartyWroclaw_rozklad_jazdy_GTFS/*.txt"

database_name = "PoC_2_wroclaw_mpk.db"

trips_csv = "trips.csv"
stops_csv = "stops.csv"
stop_times_csv = "stop_times.csv"

# # # # Recall of functions
# # # # downloading data and uploading them to the database
# fdd.delateing_folder_with_data_if_exists(path_data)
# fdd.download_data(URL, fileName, path_data)
# fdd.replace_txt_to_csv(txt_file_path)
# fdd.load_write_data(path_data, trips_csv, stops_csv, stop_times_csv, database_name)


# # # ## Collecting user responses
print("Please go to http link")
f.run_app() 
f.user_answers()
f.sql_query()
## Calculating the distance and providing a table with the final results

f.change_in_latitude()
f.change_in_longitude()
f.change_in_longitude_end_point()
f.create_squares()
f.select_stops_radius()
f.make_radian()
f.distance_start_end_direction()
f.table_with_routes()

