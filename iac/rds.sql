psql --host=<url> --port=5432 --username=user<> --dbname=air_pollution --password \
  -c "CREATE TABLE hourly (
  id SERIAL PRIMARY KEY,
  date_local TIMESTAMP NOT NULL,
  parameter VARCHAR(255) NOT NULL,
  three_hourly_avg_value FLOAT,
  value FLOAT NOT NULL,
  unit VARCHAR(255) NOT NULL,
  city VARCHAR(255) NOT NULL,
  country VARCHAR(255) NOT NULL,
  source_name VARCHAR(255) NOT NULL,
  source_type VARCHAR(255) NOT NULL,
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  CONSTRAINT unique_combination_h
    UNIQUE (date_local, parameter, unit, city, country, source_name, source_type, latitude, longitude)
);
"
  -c "CREATE TABLE three_hourly_agg_city (
    id SERIAL PRIMARY KEY,
    date_local TIMESTAMP NOT NULL,
    parameter VARCHAR(255) NOT NULL,
    three_hourly_avg_agg FLOAT,
    unit VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    CONSTRAINT unique_combination_3h UNIQUE (date_local, parameter, unit, city, country)
);
"
