## Self-healing consecutive runs

Since we are calculating the three hourly average, we need data for the previous three hours. So, if there is a missing data point for any of these hours in the past three hours, we won't be able to calculate the three hourly average for that hour.

To make the pipeline self-healing, we need to handle such cases. We can check the latest hour for which we have calculated the three hourly average. Then, we can start calculating the three hourly average for the next hour after that, and then the next hour after that, and so on, until we reach the current datetime.

For example, let's say the current datetime is 10 am and the last hour for which we have calculated the three hourly average is 7 am. This means we need to calculate the three hourly average for 8 am, 9 am, and 10 am. But if we don't have data for any of these hours, we can't calculate the three hourly average for that hour. So, we wait for the next run of the lambda, and we check again if we have data for the missing hour. If we do, we can calculate the three hourly average for that hour and continue calculating the three hourly averages for the remaining hours.

## Touch-ups

- Use secret manager for passwords;
- Use a database migration tool like Flyway or Liquibase to manage database schema changes in a more controlled and repeatable manner.
