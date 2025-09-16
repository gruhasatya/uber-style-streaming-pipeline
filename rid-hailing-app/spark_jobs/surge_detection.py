# Reads from Kafka (gps_topic, rides_topic).

# Calculates demand vs supply per zone.
# If ride_requests > 2 * active_drivers → surge alert.

# Writes alerts back into Kafka (surge_alerts_topic).

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, count, to_json, struct
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType

KAFKA_BROKER = "localhost:9092"
GPS_TOPIC = "gps_topic"
RIDES_TOPIC = "rides_topic"

SURGE_ALERTS_TOPIC = "surge_alerts_topic"
CHECKPOINT_PATH = "s3a://my-ride-hailing-data/checkpoints/surge_detection/"

spark = SparkSession.builder.appName("RideHailingSurgeDetection").getOrCreate()

gps_schema = StructType() \
    .add("driver_id", StringType()) \
    .add("zone", StringType()) \
    .add("lat", DoubleType()) \
    .add("lon", DoubleType()) \
    .add("timestamp", IntegerType())

ride_schema = StructType() \
    .add("ride_id", StringType()) \
    .add("pickup_zone", StringType()) \
    .add("dropoff_Zone", StringType()) \
    .add("status", StringType()) \
    .add("timestamp", IntegerType())

## read part

gps_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", GPS_TOPIC) \
    .load() \
    .select(from_json(col("val").cast("string"), gps_schema).alias("data")).select("data.*")

ride_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", RIDES_TOPIC) \
    .load()

parsed = ride_df.selectExpr("CAST(value AS STRING)").select(from_json(col("value"), ride_schema).alias("data")).select("data.*")


# Aggregate drivers per zone
drivers_per_zone = gps_df.groupBy("zone").agg(count("driver_id").alias("active_drivers"))


rides_per_zone = parsed.filter(col("status") == "requested") \
    .groupBy("pickup_zone").agg(count("ride_id").alias("ride_requested")) \
    .withColumnRenamed("pickup_zone", "zone")


# Join supply & demand
demand_supply = rides_per_zone.join(drivers_per_zone,"zone", "left")

surge_alerts = demand_supply.filter(col("ride_requested") > 2 * col("active_drivers")) \
    .selectExpr("zone as key", "to_json(struct(*)) as value")

query = surge_alerts.writeStream.format("kafka") \
    .otpion("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("topic", SURGE_ALERTS_TOPIC) \
    .option("checkpointLocation", CHECKPOINT_PATH) \
    .outputMode("append") \
    .start()
  
query.awaitTermination()