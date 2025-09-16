# Logic (Simplified for Now)

# Read GPS stream (gps_topic) → active drivers per zone.
# Read Rides stream (rides_topic) → new ride requests.
# Join rides with drivers by zone (simplified — later we could extend with actual lat/lon distance matching).
# Output driver–ride assignments to Kafka (matched_rides_topic).

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StringType, StructType, DoubleType, IntegerType

KAFKA_BROKER = "localhost:9092"
GPS_TOPIC = "gps_topic"
RIDES_TOPIC = "rides_topic"
MATCHED_RIDES_TOPIC = "matched_rides_topic"
CHECKPOINT_PATH = "s3a://my-ride-hailing-data/checkpoints/driver_matching/"

spark = SparkSession.builder.appName("RideHailingDrivingMatcher").getOrCreate()

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

gps_df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", GPS_TOPIC) \
    .load()

gps_parsed = gps_df.selectExpr("CAST(value AS STRING)").select(from_json(col("value"), gps_schema).alias("data")).select("data.*")

rides_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", RIDES_TOPIC) \
    .load() \
    .select(from_json(col("value").cast("string"), ride_schema).alias("data")) \
    .select("data.*")



requested_rides = rides_df.filter(col("status") == "requested")

# join on zone
matched_rides = requested_rides.join(
    gps_parsed,
    requested_rides.pickup_zone == gps_parsed.zone
    "inner"
).select(
    requested_rides.ride_id,
    requested_rides.pickup_zone,
    requested_rides.dropoff_zone,
    gps_parsed.driver_id,
    gps_parsed.lat,
    gps_parsed.lon,
)

### write 

query = matched_rides.selectExpr("ride_id as key", "to_json(struct(*)) as value").writeStream \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("topic", MATCHED_RIDES_TOPIC) \
    .option("checkpoints", CHECKPOINT_PATH) \
    .outputMode("append") \
    .start()

query.awaitermination() 



### output may looklike this 
# {
#   "ride_id": "ride_1234",
#   "pickup_zone": "midtown",
#   "dropoff_zone": "downtown",
#   "driver_id": "driver_12",
#   "lat": 40.75234,
#   "lon": -73.98412
# }
