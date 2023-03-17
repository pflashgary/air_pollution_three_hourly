import pytz
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder

tf = TimezoneFinder()


class ThreeHourlyAverages:
    def __init__(self, pool):
        self.pool = pool

    def find_null_three_hourly(
        self,
        parameter,
        unit,
        city,
        country,
        source_name,
        source_type,
        latitude,
        longitude,
    ):
        conn = self.pool.getconn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT date_local
            FROM hourly
            WHERE parameter = %s
                AND unit = %s
                AND city = %s
                AND country = %s
                AND source_name = %s
                AND source_type = %s
                AND latitude = %s
                AND longitude = %s
                AND three_hourly_avg_value IS NULL
        """,
            (
                parameter,
                unit,
                city,
                country,
                source_name,
                source_type,
                latitude,
                longitude,
            ),
        )

        date_locals = [
            row[0] for row in cur.fetchall()
        ]  # fetch all rows and extract the date_local values

        cur.close()  # close the cursor
        self.pool.putconn(conn)  # return the connection to the pool

        return date_locals

    def update_three_hourly_average(
        self,
        date_local,
        parameter,
        unit,
        city,
        country,
        source_name,
        source_type,
        latitude,
        longitude,
        three_hourly_average,
    ):

        conn = self.pool.getconn()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE hourly SET three_hourly_avg_value = ROUND(%s::numeric, 2) WHERE date_local = %s AND parameter = %s AND unit = %s AND city = %s AND country = %s AND source_name = %s AND source_type = %s AND latitude = %s AND longitude = %s
            """,
            (
                three_hourly_average,
                date_local,
                parameter,
                unit,
                city,
                country,
                source_name,
                source_type,
                latitude,
                longitude,
            ),
        )
        conn.commit()
        cur.close()
        self.pool.putconn(conn)

    def aggregate(
        self,
        date_local,
        parameter,
        unit,
        city,
        country,
    ):
        conn = self.pool.getconn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO three_hourly_agg_city (date_local, parameter, three_hourly_avg_agg, unit, city, country)
            SELECT date_local, parameter, ROUND(AVG(three_hourly_avg_value), 2) AS three_hourly_avg, unit, city, country
            FROM hourly
            WHERE date_local = %s AND parameter = %s AND unit = %s AND city = %s AND country = %s
            GROUP BY date_local, parameter, unit, city, country
            ON CONFLICT (date_local, parameter, unit, city, country) DO UPDATE SET three_hourly_avg_agg = EXCLUDED.three_hourly_avg_agg;
            """,
            (date_local, parameter, unit, city, country),
        )

        conn.commit()
        cur.close()
        self.pool.putconn(conn)
