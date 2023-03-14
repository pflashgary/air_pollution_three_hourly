import json
import pytz
import os
import psycopg2
from timezonefinder import TimezoneFinder
from datetime import datetime, timedelta
from airpollution.hourly import Hourly
from airpollution.three_hourly import ThreeHourlyAverages


tf = TimezoneFinder()

# Connect to RDS
db_connection = psycopg2.connect(
    host=os.environ["RDS_HOST"],
    port=os.environ["RDS_PORT"],
    dbname=os.environ["RDS_DB_NAME"],
    user=os.environ["RDS_USERNAME"],
    password=os.environ["RDS_PASSWORD"],
)

# Define PostgreSQL connection details
POSTGRES_DB = "air_pollution"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "psql"
POSTGRES_HOST = "127.0.0.1"
POSTGRES_PORT = "5432"

# Create PostgreSQL connection
db_connection = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
)


hourly = Hourly(db_connection)
three_hourly = ThreeHourlyAverages(db_connection)


def lambda_handler(event, context):

    # Get the message from SNS
    message = json.loads(event["Records"][0]["Sns"]["Message"])

    # Get data from message
    date_local = message["date"]["local"]
    parameter = message["parameter"]
    value = message["value"]
    unit = message["unit"]
    city = message["city"]
    country = message["country"]
    source_name = message["sourceName"]
    source_type = message["sourceType"]
    latitude = message["coordinates"]["latitude"]
    longitude = message["coordinates"]["longitude"]

    # Send hourly data to RDS
    hourly.add_hourly_data(
        date_local,
        parameter,
        value,
        unit,
        city,
        country,
        source_name,
        source_type,
        latitude,
        longitude,
    )

    first_three_hourly_hour, current_hour = three_hourly.get_first_datetime_by_location(
        longitude, latitude
    )

    while first_three_hourly_hour <= current_hour:
        # Check if there is any missing data for this hour
        data_count = hourly.count_hourly_data(
            parameter,
            city,
            country,
            source_name,
            source_type,
            latitude,
            longitude,
            first_three_hourly_hour - timedelta(hours=2),
            first_three_hourly_hour,
        )

        if data_count < 3:
            # Data is missing for this hour, wait until the next run of the lambda to calculate the average
            break
        # Calculate the three-hourly average
        three_hourly_average = hourly.get_average_value(
            parameter,
            city,
            country,
            source_name,
            source_type,
            latitude,
            longitude,
            first_three_hourly_hour - timedelta(hours=2),
            first_three_hourly_hour,
        )

        # Insert it into the three hourly table
        three_hourly.add_three_hourly_average(
            first_three_hourly_hour,
            parameter,
            city,
            country,
            source_name,
            source_type,
            latitude,
            longitude,
            unit,
            three_hourly_average,
        )

        # Move to the next hour
        first_three_hourly_hour += timedelta(hours=1)
