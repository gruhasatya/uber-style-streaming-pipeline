from kafka import KafkaProducers
import json, time, ranodm, logging


KAFKA_BROKER = "localhost:9092"
GPS_TOPIC = "gps_topic"

logging.basicConfig(
    level = logging.info,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def create_procedure():
    return KafkaProducers(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer = lambda v : json.dumps(v).encode("utf-8"),
        retries = 5
    )

def generate_gps_event():
    zones = ["midtown", "downtown", "uptown"]
    return {
        "driver_id": f"driver_{random.randint(1, 50)}",
        "zone": random.choice(zones),
        "lat": round(random.uniform(40.70, 40.80), 5),
        "lon": round(random.uniform(-73.95, -73.85), 5),
        "timestamp": int(time.time())
    }

def main():
    producer = create_procedure()
    logging.info("GPS producer Started")

    try:
        while True:
            event = generate_gps_event()
            producer.send(GPS_TOPIC, value=event)
            logging.info(f"Produced GPS:{event}")
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Gps producer stopped manully")
    
    finally:
        producer.close()

if __name__ == "__main__":
    main()