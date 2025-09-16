from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "surge_alerts_topic",
    bootstrap_servers="localhost:9092",
    group_id="pricing_service",
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

for msg in consumer:
    data = msg.value
    multiplier = round(data["ride_requests"] / max(data["active_drivers"], 1), 1)
    print(f"Surge in {data['zone']} → {multiplier}x fares")
