import json
import os
import psycopg2.pool
from timezonefinder import TimezoneFinder
from datetime import timedelta
import logging
from airpollution.hourly import Hourly
from airpollution.three_hourly import ThreeHourlyAverages

tf = TimezoneFinder()

# Create a connection pool with 5 maximum connections
pool = psycopg2.pool.SimpleConnectionPool(
    os.environ["DB_MIN"],  # minimum number of connections
    os.environ["DB_MAX"],  # maximum number of connections
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    database=os.environ["DB_NAME"],
)

hourly = Hourly(pool)
three_hourly = ThreeHourlyAverages(pool)


def handler(event, context):

    # Get the message from SQS
    for record in event["Records"]:
        body = json.loads(record["body"])
        message = json.loads(body["Message"])
        logging.info(f"Here is the message {message}")

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
        logging.info("Data to hourly successful")

        date_local_nulls = three_hourly.find_null_three_hourly(
            parameter,
            unit,
            city,
            country,
            source_name,
            source_type,
            latitude,
            longitude,
        )

        for date_local_null in date_local_nulls:
            logging.info(
                f"check if {date_local_null} has gathered the last three hours."
            )
            # Check if there is any missing data for this hour
            data_count = hourly.count_distinct_hourly_data(
                parameter,
                unit,
                city,
                country,
                source_name,
                source_type,
                latitude,
                longitude,
                date_local_null - timedelta(hours=2),
                date_local_null,
            )
            logging.info(
                f"The number of hourly rows between {date_local_null - timedelta(hours=2)}/{date_local_null} is {data_count}."
            )

            if data_count == 3:

                # Calculate the three-hourly average
                three_hourly_average = hourly.get_average_value(
                    parameter,
                    unit,
                    city,
                    country,
                    source_name,
                    source_type,
                    latitude,
                    longitude,
                    date_local_null - timedelta(hours=2),
                    date_local_null,
                )

                # Update hourly three_hourly_avg_value
                three_hourly.update_three_hourly_average(
                    date_local_null,
                    parameter,
                    unit,
                    city,
                    country,
                    source_name,
                    source_type,
                    latitude,
                    longitude,
                    three_hourly_average,
                )
                logging.info("Three hourly average update is successful.")

                # Calculate the aggregated values for each parameter by city
                three_hourly.aggregate(
                    date_local_null,
                    parameter,
                    unit,
                    city,
                    country,
                )
                logging.info("Three hourly city aggregate is successful.")
