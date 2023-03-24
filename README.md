# Real time air pollution monitoring
In this project, we aim to provide a real-time view of air quality in different cities of Belgium by tapping into the openaq dataset. Our goal is to ingest and process the data from the SNS topic, calculate the average of measurements over the last 3 hours, and store the results in a database. Additionally, we would like to visualize the data.

## Methodology

### Strategies

To calculate the three hourly average, I can think of three strategies:

- Using a lambda to store hourly data in a database like DynamoDB or RDS and then calculate the moving average in the same lambda (past three hours). One advantage of this approach is that it's simple and requires only one lambda function. However, one disadvantage is that if the incoming data is not ordered, it may not be easy to calculate the correct moving average;

- Using one lambda function to store hourly data in a database like DynamoDB or RDS and another lambda function to populate a separate table with three hourly moving averages (can be scheduled). Note, I would avoid having to write and deploy two lambdas;

- Using datastores which natively support time series rolling averages. E.g. storing hourly data in AWS Prometheus and using PromQL to calculate the three hourly moving averages on the fly (TimescaleDB is another alternative). This allows for real-time visualization of the moving average using a tool like Grafana. However, this approach requires access to AWS services like Prometheus and Grafana.

To minimize operational expenses, I opted for the first strategy that incorporates a self-healing mechanism.

#### Self-healing consecutive runs

##### Three hourly average for each location
To calculate the three-hourly average, we need data from the previous three hours. If any data point is missing for any of these three hours, we won't be able to calculate the average for that hour. To make the pipeline self-healing, we should handle such cases. At each run of the pipeline, we should identify the rows in the hourly table where the three-hourly average is null, and check if there are data points for the previous three hours. If data points exist, we can calculate the three-hourly average and update the corresponding column.

##### Aggregated three hourly average for each city
To aggregate three hourly averages over each city for all the locations, we perform the following steps:

1. For each combination of (`date_local`, `parameter`, `unit`, `city`, `country`), we calculate the average of `three_hourly_avg_value` in the `hourly` table.

2. We update the `three_hourly_agg_city` table with the aggregated value for each combination of (`date_local`, `parameter`, `unit`, `city`, `country`).

3. Each time we have a new measurement from a location in the city, the aggregated value in the `three_hourly_agg_city` table will be updated accordingly.

#### Repository pattern
The repository pattern used in the `Hourly` and `ThreeHourlyAverages` classes helps to separate the logic of the application from the specific database being used. This allows the application to be more flexible and easily switch to a different database in the future without needing to change the application's logic. It also helps to organize the database access code and keep it in a single location.

#### Database

I created two tables on the AWS RDS instance:
##### `hourly`
- date_local: A timestamp representing the local date and time.
- parameter: A string representing the parameter being measured.
- three_hourly_avg_value: A floating-point number representing the three-hourly average value (if available).
- value: A floating-point number representing the value of the parameter being measured.
- unit: A string representing the unit of measurement.
- city: A string representing the city where the measurement was taken.
- country: A string representing the country where the measurement was taken.
- source_name: A string representing the name of the source of the data.
- source_type: A string representing the type of the source of the data.
- latitude: A floating-point number representing the latitude of the location where the measurement was taken.
- longitude: A floating-point number representing the longitude of the location where the measurement was taken.

The hourly table has a unique constraint called unique_combination_h which ensures that there are no duplicate entries for a given combination of the columns date_local, parameter, unit, city, country, source_name, source_type, latitude, and longitude.

##### `three_hourly_agg_city`
- date_local: A timestamp representing the local date and time.
- parameter: A string representing the parameter being measured.
- three_hourly_avg_agg: A floating-point number representing the three-hourly average value aggregated for all cities.
- unit: A string representing the unit of measurement.
- city: A string representing the city for which the aggregation is being performed (in this case, it is always "All Cities").
- country: A string representing the country for which the aggregation is being performed.

The three_hourly_agg_city table has a unique constraint called unique_combination_3h which ensures that there are no duplicate entries for a given combination of the columns date_local, parameter, unit, city, and country.


#### Manual hoops

##### Public Access to RDS
To visualize the RDS instance with Superset running locally, I needed public access to the RDS. The steps I took are:
- I ran the command `aws ec2 describe-security-groups` and found a security group that had port 5432 exposed.
- I added my IP to the inbound rules of the security group from the console to allow access.
- I made the RDS instance publicly accessible by adding the line `publicly_accessible = true` to `rds.tf`.
- I confirmed that the subnets permitted public IP assignments on the console.

##### Lambda Deployment
I faced some restrictions with the role that I was using for deployment. Some of the missing permissions were:
- `cloudformation:CreateChangeSet`. As a result, I couldn't use Serverless, and instead I had to use `aws lambda` (cli) for deployment.
- `ECR`. I was unable to use a docker image and instead had to package the app.

##### Connecting to the RDS instance from Lambda
The option `--vpc-config SubnetIds=subnet-6048dd3a,subnet-ffaaf1b7,subnet-a51b50c3,SecurityGroupIds=sg-05e7d28bb8d6b7d2e` to connect to the RDS instance from Lambda was not allowed because the lambda execution role lacked permissions to `CreateNetworkInterface`, and no permissions could be added to the IAM role. Therefore, I opened all inbound traffic to the RDS. Is it a good idea? No.

#### Deploy

##### RDS instance

```bash
cd iac
terraform apply
```

##### Lambda

```
cd lambda
./manual.sh
```
#### A few loose ends to tie up

- Keep an eye on the number of connections to the AWS RDS instance to avoid hitting the cap;
- Create a Superset visualization;
- Use secret manager for passwords;


## Suitability of openaq for AirMax usecase

- Reliability
- Accessibility
- Granularity
- Timeliness
- Coverage


### SQL-Based Preliminary Analysis

- Number of stations in each city

```sql
SELECT city, COUNT(*) AS num_stations
FROM (
  SELECT DISTINCT city, latitude, longitude
  FROM hourly
) AS subquery
GROUP BY city;
```

          city           | num_stations
-------------------------+--------------
 Luxembourg              |            4
 Brussels-Capital Region |           10
 Oost-Vlaanderen         |           16
 Limburg                 |            4
 Hainaut                 |            7
 Antwerpen               |           20
 Namur                   |            3
 West-Vlaanderen         |           10
 Vlaams-Brabant          |            7
 Liege                   |            8


- Number of parameters for each station

```sql
SELECT city, latitude, longitude, STRING_AGG(DISTINCT parameter, ', ' ORDER BY parameter) AS parameters
FROM hourly
GROUP BY city, latitude, longitude;

```

         city           |     latitude     |    longitude     |          parameters
-------------------------+------------------+------------------+------------------------------
 Antwerpen               | 51.0920000379014 | 4.38010354488249 | pm10, pm25
 Antwerpen               | 51.1203841374963 | 5.02154597760984 | no2
 Antwerpen               | 51.1702980388321 | 4.34100506456284 | pm10, pm25, so2
 Antwerpen               | 51.1771308881904 | 4.41794863777773 | no2, pm10, pm25
 Antwerpen               | 51.1928003335933 | 5.22153407909309 | so2
 Antwerpen               | 51.2082294722138 | 4.42155925106527 | no2, pm10, pm25
 Antwerpen               |   51.20951873198 | 4.43179223079244 | no2, pm10, pm25
 Antwerpen               |        51.209663 |         4.431821 | no2, o3, pm10, pm25
 Antwerpen               | 51.2146988167721 | 4.33220643231032 | no2
 Antwerpen               | 51.2286298134603 | 4.42845417753557 | no2, pm10, pm25
 Antwerpen               | 51.2336522065588 | 5.16397884633176 | no2, o3, pm10, pm25
 Antwerpen               |  51.236194200299 | 4.38522368445472 | pm10, pm25
 Antwerpen               | 51.2501064987036 | 4.34210451132214 | no2, so2
 Antwerpen               |        51.252103 |         4.491362 | no2, o3, pm10, pm25
 Antwerpen               | 51.2558066447111 | 4.38535982604938 | no2, so2
 Antwerpen               | 51.2609897078635 | 4.42439900693533 | no2, pm10, pm25
 Antwerpen               | 51.2642897846451 | 4.34127999246466 | no2, so2
 Antwerpen               | 51.3139288945411 | 4.40386813974961 | pm10, pm25
 Antwerpen               | 51.3204167857085 | 4.44481061898005 | no2
 Antwerpen               | 51.3487952923282 | 4.33970994711987 | no2, o3
 Brussels-Capital Region |        50.796632 |         4.358539 | no2, o3, pm10, pm25, so2
 Brussels-Capital Region | 50.8117008944185 | 4.32838466510102 | no2
 Brussels-Capital Region |        50.825128 |         4.384719 | no2
 Brussels-Capital Region | 50.8386311880319 | 4.37438828335274 | co, no2
 Brussels-Capital Region | 50.8407885668979 | 4.37614906974903 | co, no2
 Brussels-Capital Region |        50.849665 |          4.33382 | co, no2, o3, pm10, pm25, so2
 Brussels-Capital Region | 50.8508105371924 | 4.34858747427388 | co, no2
 Brussels-Capital Region | 50.8580305936746 |  4.2883363663059 | no2, o3, pm10, pm25
 Brussels-Capital Region | 50.8835598117798 | 4.38296325180234 | co, no2, o3, pm10, pm25, so2
 Brussels-Capital Region |        50.895101 |         4.392718 | no2, o3, pm10, pm25
 Hainaut                 |        50.377592 |           4.4247 | pm10, pm25
 Hainaut                 | 50.4078101998156 | 4.39589711703924 | co, no2, pm10, pm25, so2
 Hainaut                 |        50.409311 |         4.452172 | co, no2, pm10, pm25
 Hainaut                 | 50.4164333599369 | 4.52113020813044 | pm10, pm25, so2
 Hainaut                 |        50.428995 |         4.458681 | no2, o3, pm10, pm25
 Hainaut                 | 50.4651921568256 | 3.93971432552384 | co, no2, o3, pm10, pm25
 Hainaut                 | 50.6167184021922 | 3.45762442718173 | co, no2, o3, pm10, pm25, so2
 Liege                   |        50.583614 |         5.397446 | no2, o3, pm10, pm25, so2
 Liege                   | 50.6119227069516 | 5.61114976281943 | pm10, pm25
 Liege                   | 50.6122775285323 | 5.99275271918705 | pm10, pm25
 Liege                   |        50.613413 |         5.570223 | co, no2, o3, pm10, pm25, so2
 Liege                   |        50.620671 |         5.516405 | co, no2, pm10, pm25, so2
 Liege                   |        50.624992 |         5.547464 | pm10, pm25
 Liege                   | 50.6288602602161 | 6.00232868693696 | no2, o3, so2
 Liege                   |        50.658444 |         5.627835 | no2, o3, pm10, pm25
 Limburg                 | 50.7117060941316 | 5.10315860945395 | no2, o3, pm10, pm25
 Limburg                 | 50.8822988262256 | 5.61887398523951 | no2, o3

- Missing hours

```sql
SELECT COUNT(*) AS total_hours
FROM generate_series(
  (SELECT date_trunc('hour', MIN(date_local)) FROM hourly),
  (SELECT date_trunc('hour', MAX(date_local)) FROM hourly),
  '1 hour'::interval
) AS hours;

481

WITH all_hours AS (
  SELECT generate_series(
           date_trunc('hour', MIN(date_local)),
           date_trunc('hour', MAX(date_local)),
           interval '1 hour'
         ) AS hour
  FROM hourly
  WHERE city = 'Antwerpen' AND latitude = 51.0920000379014 AND longitude = 4.38010354488249 AND parameter = 'pm25'
)
SELECT COUNT(all_hours.hour) AS missing_count
FROM all_hours
LEFT JOIN hourly ON all_hours.hour = date_trunc('hour', hourly.date_local)
WHERE hourly.date_local IS NULL;

399
```

        hour
---------------------
 2023-03-04 14:00:00
 2023-03-04 15:00:00
 2023-03-04 16:00:00
 2023-03-04 17:00:00
 2023-03-04 18:00:00
 2023-03-04 19:00:00
 2023-03-04 20:00:00
 2023-03-04 21:00:00
 2023-03-04 22:00:00
 2023-03-04 23:00:00
 2023-03-05 00:00:00
 2023-03-05 01:00:00
 2023-03-05 16:00:00
 2023-03-05 17:00:00
 2023-03-05 18:00:00
 2023-03-05 19:00:00
 2023-03-05 20:00:00
 2023-03-05 21:00:00
 2023-03-05 22:00:00
 2023-03-05 23:00:00
 2023-03-06 00:00:00
 2023-03-06 01:00:00
 2023-03-06 02:00:00
 2023-03-06 03:00:00
 2023-03-06 04:00:00
 2023-03-06 05:00:00
 2023-03-06 06:00:00
 2023-03-06 07:00:00
 2023-03-06 08:00:00
 2023-03-06 09:00:00
 2023-03-06 10:00:00
 2023-03-06 11:00:00
 2023-03-06 12:00:00
 2023-03-06 13:00:00
 2023-03-06 14:00:00
 2023-03-06 15:00:00
 2023-03-06 16:00:00
 2023-03-06 17:00:00
 2023-03-06 18:00:00
 2023-03-06 19:00:00
 2023-03-06 20:00:00
 2023-03-06 21:00:00
 2023-03-06 22:00:00
 2023-03-06 23:00:00
 2023-03-07 00:00:00
 2023-03-07 01:00:00
 2023-03-07 02:00:00
:
:

- Delay

At 9:00 am today:

```sql
SELECT MAX(date_local) fROM HOURLY;
```
         max
---------------------
 2023-03-24 02:00:00


 ## Future Directions
 - Our results demonstrate the technical feasibility of the approach.
 - Further investigation is needed to determine whether the observed data gaps are intrinsic to the data or due to hitting the cap of RDS connections.
 - Future work will focus on developing spatiotemporal visualizations of the data using Superset.
 - For now `terraform destroy` to avoid the costs.