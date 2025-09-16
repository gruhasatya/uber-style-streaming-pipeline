# uber-style-streaming-pipeline

## End-to-End View Now


###Producers

gps_producer.py → sends driver GPS pings.

rides_producer.py → sends ride requests.

### Spark Jobs

surge_detection.py → Kafka → Kafka (surge_alerts_topic).

batch_to_s3.py → Kafka → S3 (history).

driver_matching.py → Kafka → Kafka (matched_rides_topic).

### Consumers

pricing_service_consumer.py → uses surge alerts.

notifications_consumer.py → uses surge alerts.

dashboard_consumer.py → logs surge alerts.

dispatch_service_consumer.py → assigns drivers to rides.
