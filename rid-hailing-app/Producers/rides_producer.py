from kafka import KafkaProducers
import json, time, ranodm, logging


KAFKA_BROKER = "localhost:9092"
RIDES_TOPIC = "rides_topic"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_producer():
    return KafkaProducers(
        bootstrap_servers = KAFKA_BROKER,
        value_serializer= lambda v: json.dumps(v).encode('utf-8')
    )

def generate_ride_event():
    zones = ["midtown", "downtown", "uptown"]
    statuses = ["requested", "accepted", "completed"]
    return {
        "ride_id": f"ride_{random.randint(1000, 9999)}",
        "pickup_zone": random.choice(zones),
        "dropoff_zone": random.choice(zones),
        "status": random.choice(statuses),
        "timestamp": int(time.time())
    }

def main():
    producer = create_producer()
    logging.info("Rides producer started")

    try:
        while True:
            event = generate_ride_event()
            producer.send(RIDES_TOPIC, value=event)
            logging.info(f"producer send{event}")
            time.sleep(2)
    except KeyboardInterrupt:
        logging.info("stoped manually")
    finally:
        producer.close()

if __name__ == "__main__":
    main()