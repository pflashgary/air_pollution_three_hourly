


Based on the information provided, here is a potential structure for your presentation:

## Introduction:
- Briefly introduce yourself and your experience with data integration and cloud infrastructure
- Recap the objective and data provided by AirMax

## Data Ingestion:
- Explain the SNS stream and how it was linked to the SQS queue
- Discuss the libraries or AWS services used for processing the data (e.g. Python Boto3 library)
- Explain the process for receiving, decoding and storing data to a database (e.g. RDS or DynamoDB)

## Data Processing:
- Discuss the method used to calculate the current air quality in a city (e.g. average of the measurements over the last 3 hours)
- Explain any challenges faced in processing the data and how they were addressed (e.g. dealing with missing or corrupt data)

## Data Visualization:
- Explain the method used to display the results on a map (e.g. using Streamlit, Dash, Plotly)
- Walk through the user interface and demonstrate how the map displays the current air quality in various cities

## Conclusion:
- Summarize the results achieved and how they meet the requirements set out by AirMax
- Discuss any further steps required to develop, test and deploy the solution to production
- Provide any recommendations for improving the solution or expanding the use case for AirMax


check gap in the data
check each parameter how many stations in the city

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


Missing hours:

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
:
at 9:00 am
select max(date_local) from hourly;
         max
---------------------
 2023-03-24 02:00:00


Suitable:

Reliability: The data should be accurate and trustworthy, and should come from reliable sources.
Granularity: The data should be available at a high level of detail, such as at the level of individual pollutants or at specific locations.
Timeliness: The data should be available in near-real time, to allow for timely decision-making and response to changing conditions.
Accessibility: The data should be easily accessible and available in formats that are easy to use and integrate with other systems.
Coverage: The data should cover a broad geographic area and should be available for multiple cities and regions.
Not suitable:

Lack of Quality Control: If the data is not subject to quality control measures, it may be unreliable or inaccurate.
Limited Granularity: If the data is only available at a high level, such as an overall air quality index, it may not provide enough detail for decision-making.
Delayed Reporting: If the data is only available after a significant delay, it may not be useful for real-time decision-making.
Limited Accessibility: If the data is not easily accessible or available in formats that are difficult to use, it may not be useful for integration with other systems.
Limited Coverage: If the data only covers a small geographic area, it may not provide enough information for decision-making at a larger scale.