from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "surger_alerts_topic",
    bootstrap_servers = "localhost:9092",
    group_id = "notifications_service",
    value_deserializer = lambda v: json.load(v.decode("utf-8"))
)

for msg in consumer:
    data = msg.value
    print(f"High demand in {data['zone']}! Drivers: {data['active_drivers']}, Requests: {data['ride_requests']}")