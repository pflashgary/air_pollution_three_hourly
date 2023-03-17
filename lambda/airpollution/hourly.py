class Hourly:
    def __init__(self, pool):
        self.pool = pool

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
        conn = self.pool.getconn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO hourly (date_local, parameter, value, unit, city, country, source_name, source_type, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
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
        conn.commit()
        cur.close()
        self.pool.putconn(conn)

    def count_distinct_hourly_data(
        self,
        parameter,
        unit,
        city,
        country,
        source_name,
        source_type,
        latitude,
        longitude,
        start_time,
        end_time,
    ):
        conn = self.pool.getconn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(DISTINCT date_local) FROM hourly
            WHERE parameter = %s AND unit = %s AND city = %s AND country = %s AND source_name = %s AND source_type = %s
                AND latitude = %s AND LONGITUDE = %s AND date_local BETWEEN %s AND %s
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
                start_time,
                end_time,
            ),
        )
        data_count = cur.fetchone()[0]
        cur.close()
        self.pool.putconn(conn)
        return data_count

    def get_average_value(
        self,
        parameter,
        unit,
        city,
        country,
        source_name,
        source_type,
        latitude,
        longitude,
        start_time,
        end_time,
    ):
        conn = self.pool.getconn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT AVG(value) FROM hourly
            WHERE parameter = %s AND unit = %s AND city = %s AND country = %s AND source_name = %s AND source_type = %s
                AND latitude = %s AND LONGITUDE = %s AND date_local BETWEEN %s AND %s
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
                start_time,
                end_time,
            ),
        )
        three_hourly_average = cur.fetchone()[0]
        cur.close()
        self.pool.putconn(conn)

        return three_hourly_average
