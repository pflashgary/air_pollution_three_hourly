from datetime import datetime, timedelta
from typing import List
from timezonefinder import TimezoneFinder

tf = TimezoneFinder()


class Hourly:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cur = self.conn.cursor()

    def add_hourly_data(
        self,
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
    ):
        self.cur.execute(
            """
            INSERT INTO hourly (date_local, parameter, value, unit, city, country, source_name, source_type, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
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
            ),
        )
        self.conn.commit()

    def count_hourly_data(
        self,
        parameter,
        city,
        country,
        source_name,
        source_type,
        latitude,
        longitude,
        start_time,
        end_time,
    ):
        self.cur.execute(
            """
            SELECT COUNT(*) FROM hourly
            WHERE parameter = %s AND city = %s AND country = %s AND source_name = %s AND source_type = %s
                AND latitude = %s AND LONGITUDE = %s AND date_local BETWEEN %s AND %s
            """,
            (
                parameter,
                city,
                country,
                source_name,
                source_type,
                latitude,
                longitude,
                start_time,
                end_time,
            ),
        )
        data_count = self.cur.fetchone()[0]
        return data_count

    def get_average_value(
        self,
        parameter,
        city,
        country,
        source_name,
        source_type,
        latitude,
        longitude,
        start_time,
        end_time,
    ):
        self.cur.execute(
            """
            SELECT AVG(value) FROM hourly
            WHERE parameter = %s AND city = %s AND country = %s AND source_name = %s AND source_type = %s
                AND latitude = %s AND LONGITUDE = %s AND date_local BETWEEN %s AND %s
            """,
            (
                parameter,
                city,
                country,
                source_name,
                source_type,
                latitude,
                longitude,
                start_time,
                end_time,
            ),
        )
        three_hourly_average = self.cur.fetchone()[0]

        return three_hourly_average
