# Real time air pollution monitoring
In this project, we aim to provide a real-time view of air quality in different cities of Belgium by tapping into the openaq dataset. Our goal is to ingest and process the data from the SNS topic, calculate the average of measurements over the last 3 hours, and store the results in a database. Additionally, we would like to visualize the data.

# Strategies

To calculate the three hourly average, I can think of three strategies:

- Using a lambda to store hourly data in a database like DynamoDB or RDS and then calculate the moving average in the same lambda (past three hours). One advantage of this approach is that it's simple and requires only one lambda function. However, one disadvantage is that if the incoming data is not ordered, it may not be easy to calculate the correct moving average;

- Using one lambda function to store hourly data in a database like DynamoDB or RDS and another lambda function to populate a separate table with three hourly moving averages (can be scheduled). Note, I would avoid having to write and deploy two lambdas;

- Using datastores which natively support time series rolling averages. E.g. storing hourly data in AWS Prometheus and using PromQL to calculate the three hourly moving averages on the fly (TimescaleDB is another alternative). This allows for real-time visualization of the moving average using a tool like Grafana. However, this approach requires access to AWS services like Prometheus and Grafana.

To minimize operational expenses, I opted for the first strategy that incorporates a self-healing mechanism.

## Self-healing consecutive runs

### Three hourly average for each location
To calculate the three-hourly average, we need data from the previous three hours. If any data point is missing for any of these three hours, we won't be able to calculate the average for that hour. To make the pipeline self-healing, we should handle such cases. At each run of the pipeline, we should identify the rows in the hourly table where the three-hourly average is null, and check if there are data points for the previous three hours. If data points exist, we can calculate the three-hourly average and update the corresponding column.

### Aggregated three hourly average for each city
To aggregate three hourly averages over each city for all the locations, we perform the following steps:

1. For each combination of (`date_local`, `parameter`, `unit`, `city`, `country`), we calculate the average of `three_hourly_avg_value` in the `hourly` table.

2. We update the `three_hourly_agg_city` table with the aggregated value for each combination of (`date_local`, `parameter`, `unit`, `city`, `country`).

3. Each time we have a new measurement from a location in the city, the aggregated value in the `three_hourly_agg_city` table will be updated accordingly.

## Repository pattern
The repository pattern used in the `Hourly` and `ThreeHourlyAverages` classes helps to separate the logic of the application from the specific database being used. This allows the application to be more flexible and easily switch to a different database in the future without needing to change the application's logic. It also helps to organize the database access code and keep it in a single location.

## Database

I created two tables on the AWS RDS instance:
### `hourly`
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

### `three_hourly_agg_city`
- date_local: A timestamp representing the local date and time.
- parameter: A string representing the parameter being measured.
- three_hourly_avg_agg: A floating-point number representing the three-hourly average value aggregated for all cities.
- unit: A string representing the unit of measurement.
- city: A string representing the city for which the aggregation is being performed (in this case, it is always "All Cities").
- country: A string representing the country for which the aggregation is being performed.

The three_hourly_agg_city table has a unique constraint called unique_combination_3h which ensures that there are no duplicate entries for a given combination of the columns date_local, parameter, unit, city, and country.


## Manual hoops

### Public Access to RDS
To visualize the RDS instance with Superset running locally, I needed public access to the RDS. The steps I took are:
- I ran the command `aws ec2 describe-security-groups` and found a security group that had port 5432 exposed.
- I added my IP to the inbound rules of the security group from the console to allow access.
- I made the RDS instance publicly accessible by adding the line `publicly_accessible = true` to `rds.tf`.
- I confirmed that the subnets permitted public IP assignments on the console.

### Lambda Deployment
I faced some restrictions with the role that I was using for deployment. Some of the missing permissions were:
- `cloudformation:CreateChangeSet`. As a result, I couldn't use Serverless, and instead I had to use `aws lambda` (cli) for deployment.
- `ECR`. I was unable to use a docker image and instead had to package the app.

### Connecting to the RDS instance from Lambda
The option `--vpc-config SubnetIds=subnet-6048dd3a,subnet-ffaaf1b7,subnet-a51b50c3,SecurityGroupIds=sg-05e7d28bb8d6b7d2e` to connect to the RDS instance from Lambda was not allowed because the lambda execution role lacked permissions to `CreateNetworkInterface`, and no permissions could be added to the IAM role. Therefore, I opened all inbound traffic to the RDS. Is it a good idea? No.

## Deploy

### RDS instance

```bash
cd iac
terraform apply
```

### Lambda

```
cd lambda
./manual.sh
```
## A few loose ends to tie up

- Keep an eye on the number of connections to the AWS RDS instance to avoid hitting the cap;
- Create a Superset visualization;
- Use secret manager for passwords;
