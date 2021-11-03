import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format

# 403 
config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS']['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    
    # get filepath to song data file
    song_data = input_data + 'song-data/A/A/A/*.json'
     
    print(song_data)
    
     
    # read song data file 
    df = spark.read.json(song_data)
    # creates or replaces a local temporary view with this DataFrame.
    df.createOrReplaceTempView("temp_songs") 
    # extract columns to create songs table
    songs_table = spark.sql("""
                            SELECT song_id, 
                            title,
                            artist_id,
                            year,
                            duration
                            FROM temp_songs
                            WHERE song_id IS NOT NULL
                        """)
    
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.mode('overwrite').partitionBy("year","artist_id").parquet(output_data+'songs/')

    # extract columns to create artists table
     
    artists_table = spark.sql("""
                                SELECT DISTINCT artist_id, 
                                artist_name,
                                artist_location,
                                artist_latitude,
                                artist_longitude
                                FROM temp_songs
                                WHERE artist_id IS NOT NULL
                            """)
    
    # write artists table to parquet files
    artists_table.write.mode('overwrite').parquet(output_data+'artists/')


def process_log_data(spark, input_data, output_data):
    # get filepath to log data file
    input_data ='./data/'
    log_data = os.path.join(input_data, 'log-data/*.json') 
    # read log data file
     
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df = df.filter(df.page == 'NextSong')
    # filter by actions for song plays
    
    df.createOrReplaceTempView("temp_logs")#

    # extract columns for users table    
     
    
    users_table = spark.sql("""
                            SELECT DISTINCT userId as user_id, 
                            firstName as first_name,
                            lastName as last_name,
                            gender as gender,
                            level as level
                            FROM temp_logs
                            WHERE userId IS NOT NULL
                        """)
    
    
    # write users table to parquet files
    users_table.write.mode('overwrite').parquet(output_data+'users/') 
    
    time_table = spark.sql("""
                            SELECT 
                            A.start_time_sub as start_time,
                            hour(A.start_time_sub) as hour,
                            dayofmonth(A.start_time_sub) as day,
                            weekofyear(A.start_time_sub) as week,
                            month(A.start_time_sub) as month,
                            year(A.start_time_sub) as year,
                            dayofweek(A.start_time_sub) as weekday
                            FROM
                            (SELECT to_timestamp(timeSt.ts/1000) as start_time_sub
                            FROM temp_logs timeSt
                            WHERE timeSt.ts IS NOT NULL
                            ) A
                        """)
    
    # write time table to parquet files partitioned by year and month
    time_table.write.mode('overwrite').partitionBy("year", "month").parquet(output_data+'times/')

     
    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = spark.sql("""
                                SELECT monotonically_increasing_id() as songplay_id,
                                to_timestamp(logT.ts/1000) as start_time,
                                month(to_timestamp(logT.ts/1000)) as month,
                                year(to_timestamp(logT.ts/1000)) as year,
                                logT.userId as user_id,
                                logT.level as level,
                                songT.song_id as song_id,
                                songT.artist_id as artist_id,
                                logT.sessionId as session_id,
                                logT.location as location,
                                logT.userAgent as user_agent
                                FROM temp_logs logT
                                JOIN temp_songs songT on logT.artist = songT.artist_name and logT.song = songT.title
                            """)
    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.mode('overwrite').partitionBy("year", "month").parquet(output_data+'songplays/')


def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "./"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
