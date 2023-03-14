import pytz
from datetime import datetime, timedelta
from typing import List
from timezonefinder import TimezoneFinder

tf = TimezoneFinder()


class ThreeHourlyAverages:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cur = self.conn.cursor()

    def get_current_hour(self, longitude, latitude):
        # find the timzone for the coordinates
        tz = tf.timezone_at(lng=longitude, lat=latitude)  # 'Europe/Berlin'

        # get the current datetime in UTC timezone
        now_utc = datetime.now(pytz.utc)

        # convert to local timezone
        local_timezone = pytz.timezone(tz)  # replace with your local timezone
        now_local = now_utc.astimezone(local_timezone).replace(
            minute=0, second=0, microsecond=0
        )

        return now_local

    def get_first_datetime_by_location(self, longitude, latitude):
        self.cur.execute(
            """
            SELECT MAX(date_local) FROM three_hourly_averages WHERE longitude = %s AND latitude = %s
            """,
            (longitude, latitude),
        )
        last_datetime_str = self.cur.fetchone()[0]
        current_hour = self.get_current_hour(longitude, latitude)
        if last_datetime_str is None:
            return current_hour, current_hour
        else:
            last_datetime = datetime.strptime(last_datetime_str, "%Y-%m-%d %H:%M:%S")
            return last_datetime + timedelta(hours=1), current_hour

    def add_three_hourly_average(
        self,
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
    ):
        self.cur.execute(
            """
            INSERT INTO three_hourly_averages (date_local, parameter, city, country, source_name, source_type, latitude, longitude, unit, value)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
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
            ),
        )
        self.conn.commit()
