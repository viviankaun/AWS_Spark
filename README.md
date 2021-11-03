# Overview
![This is an image](https://github.com/viviankaun/AWS_Spark/blob/main/img/spark001.jpeg)

# Files in repository
Etl.py : Loading data from json files from s3.  Extrating data using Spark's temport viewws then  export files to s3.
1. There is unix time format in milliseconds in Json files. Divide by 1000 then convert date time which the system request. 
2. I use  SQL command  instad of data frame to drop duplicates. 
✅ Duplicates are handled.
You can as well use drop_duplicates() on the data frame.
Example:
users_table = users_table.drop_duplicates(subset=['userId'])

# result 
There would be generated parquet files under a couple of folders in S3.
# How to run the python scripts
New console  > run etl.py 
