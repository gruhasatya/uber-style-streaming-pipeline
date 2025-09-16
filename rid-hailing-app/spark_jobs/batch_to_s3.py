# Spark Job: batch_to_s3.py


# Reads both streams (gps_topic and rides_topic) from Kafka.
# Parses JSON → structured DataFrames.
# Writes data into Parquet files in S3 (or local path if testing).
# Uses checkpointing so Spark doesn’t reprocess duplicates.

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, form_json
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType

KAFKA_BROKER = "localhost:9092"
GPS_TOPIC = "gps_topic"
RIDES_TOPIC = "rides_topic"

S3_BUCKET = "s3a://my-ride-hailing-data"
GPS_PATH = f"{S3_BUCKET}/gps_data/"
RIDES_PATH = f"{S3_BUCKET}/rides_data/"
CHECKPOINT_PATH = f"{S3_BUCKET}/checkpoints/batch_to_s3/"


spark = SparkSession.builder.appName("RideHAilingBatchToS3").getOrCreate()

gps_schema = StructType() \
    .add("driver_id", StringType()) \
    .add("zone", StringType()) \
    .add("lat", DoubleType()) \
    .add("lon", DoubleType()) \
    .add("timestamp", IntegerType())

ride_schema = StructType() \
    .add("ride_id", StringType()) \
    .add("pickup_zone", StringType()) \
    .add("dropoff_zone", StringType()) \
    .add("status", StringType()) \
    .add("timestamp", IntegerType())


gps_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", GPS_TOPIC) \
    .load()

gps_parsed = gps_df.selectExpr("CAST(value AS STRING)").select(from_json(col("value"), gps_schema).alias("data")).select("data.*")

rides_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", GPS_TOPIC) \
    .load()

rides_parsed = rides_df.selectExpr("CAST(value AS STRING)").select(form_json(col("value"), ride_schema).alias("data")).select("data.*")

# write

gps_query = gps_parsed.writeStream.format("parquet") \
    .option("path", GPS_PATH) \
    .option("checkpoints", f"{CHECKPOINT_PATH}/gps/") \
    .outputMode("append") \
    .start()

rides_query = rides_df.writeStream \
    .format("parquet") \
    .option("path", RIDES_PATH) \
    .option("checkpointLocation", f"{CHECKPOINT_PATH}/rides/") \
    .outputMode("append") \
    .start()

gps_query.awaitTermination()
rides_query.awaitTermination()
