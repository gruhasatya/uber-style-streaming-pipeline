from kafka import KafkaConsumer
import json
import logging


KAFKA_BROKER = "localhost:9092"
MATCHED_RIDES_TOPIC = "matched_rides_topic"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

consumer = KafkaConsumer(
    MATCHED_RIDES_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    group_id="dispatch_service",
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

logging.info("🚦 Dispatch Service started...")

for msg in consumer:
    match = msg.value
    logging.info(
        f"Dispatching {match['driver_id']} to pickup ride {match['ride_id']} "
        f"at {match['pickup_zone']} → dropoff {match['dropoff_zone']}"
    )



# it should run like this 

# Dispatching driver_12 to pickup ride ride_1234 at midtown → dropoff downtown
# dispatching driver_7 to pickup ride ride_5678 at uptown → dropoff downtown