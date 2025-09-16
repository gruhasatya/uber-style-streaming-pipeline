from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "surge_alerts_topic",
    bootstrap_servers="localhost:9092",
    group_id="dashboard_service",
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)


with open("surge_dashboard.log", "a") as f:
    for msg in consumer:
        data = msg.value
        log_line = f"{data['zone']},{data['ride_requests']},{data['active_drivers']}\n"
        f.write(log_line)
        print(data)