# 🚖 Ride-Hailing Real-Time Data Pipeline on AWS

## Why This Project?

Modern ride-hailing apps (like Uber or Lyft) rely on **real-time data pipelines** to:

* Track **driver GPS locations** continuously.
* Process **ride requests** as they happen.
* Detect **surge pricing conditions** when demand > supply.
* Match drivers with riders instantly.
* Store events for **analytics and reporting**.

This project simulates that architecture using **Apache Kafka (MSK), Apache Spark (EMR/Glue), AWS S3, Glue, Athena, and QuickSight**.

It demonstrates **both streaming (real-time) and batch (historical analytics)** on AWS, following industry standards.

---

##  Architecture Overview

![AWS Ride-Hailing Architecture](.rid-hailing-app/Ride-hailing.png)

**Flow**:

1. **Producers** → send GPS & Ride request events to **Kafka (MSK)**.
2. **Spark Jobs (EMR / Glue Streaming)** →

   * Detect surge → publish to Kafka.
   * Match drivers with rides → publish to Kafka.
   * Archive events to **S3 Data Lake (Bronze → Silver → Gold)**.
3. **Consumers (EC2/Lambda Services)** →

   * Pricing, Notifications, Dashboard, Dispatch.
4. **Analytics** → S3 → Glue Crawler → Athena → QuickSight dashboards.
5. **Monitoring** → CloudWatch for logs, metrics, alarms.

---

## Project Structure

```bash
ride-hailing-pipeline/
│── README.md
│── docker-compose.yml          # Local Kafka (optional testing)
│── requirements.txt            # Python dependencies
│
├── producers/
│   ├── gps_producer.py         # Simulates driver GPS events
│   └── rides_producer.py       # Simulates ride requests
│
├── spark_jobs/
│   ├── surge_detection.py      # Detects surge pricing, writes to Kafka
│   ├── driver_matching.py      # Matches rides with drivers, writes to Kafka
│   └── batch_to_s3.py          # Archives raw data into S3 (Bronze)
│
├── consumers/
│   ├── pricing_service_consumer.py
│   ├── notifications_consumer.py
│   ├── dashboard_consumer.py
│   └── dispatch_service_consumer.py
│
├── utils/
│   ├── logging_utils.py        # Centralized logging
│   └── metrics_utils.py        # Simple monitoring counters
│
└── images/
    └── aws_architecture.png    # Architecture diagram
```

---

##  EC2 Setup (for Producers & Consumers)

Launch an **Amazon Linux 2 EC2 instance** (t2.medium recommended).

### 1. Install dependencies

```bash
sudo yum update -y
sudo yum install -y python3 git
python3 -m venv venv
source venv/bin/activate
pip install kafka-python pyspark boto3
```

### 2. Connect EC2 to MSK

* Ensure EC2 is in the same VPC as your **MSK cluster**.
* Add security group rules to allow traffic on port `9092`.

Update Kafka bootstrap servers in your code:

```python
producer = KafkaProducer(
    bootstrap_servers="b-1.msk-cluster-xyz.amazonaws.com:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)
```

---

## Running the Pipeline

### Step 1: Start Producers

```bash
python producers/gps_producer.py
python producers/rides_producer.py
```

### Step 2: Submit Spark Jobs

If using **EMR**:

```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 \
    spark_jobs/surge_detection.py

spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 \
    spark_jobs/driver_matching.py

spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 \
    spark_jobs/batch_to_s3.py
```

If using **AWS Glue Streaming Jobs**, upload `.py` files in Glue Console and configure MSK + S3 connection.

### Step 3: Start Consumers

```bash
python consumers/pricing_service_consumer.py
python consumers/notifications_consumer.py
python consumers/dashboard_consumer.py
python consumers/dispatch_service_consumer.py
```

---

##  Data Lake & Analytics

1. **S3 Storage** (Medallion)

   * Bronze: raw events (`gps_data/`, `rides_data/`)
   * Silver: cleaned (deduped, normalized)
   * Gold: aggregates (zone surge stats, driver utilization)

2. **Glue Crawler**

   * Run crawler on `s3://ride-hailing-data/`
   * Tables created in **Glue Data Catalog**

3. **Athena Queries**
   Example:

   ```sql
   SELECT zone, COUNT(*) AS total_rides
   FROM rides_data
   WHERE status = 'requested'
   GROUP BY zone;
   ```

4. **QuickSight Dashboards**

   * Connect QuickSight to Athena
   * Create dashboards for:

     * Surge trends
     * Driver distribution
     * Ride demand by zone

---

##  Monitoring

* **CloudWatch Logs** → Spark jobs, EC2 consumers, producers.
* **CloudWatch Metrics** → custom counters from `metrics_utils.py`.
* **CloudWatch Alarms** → trigger if Spark job fails or Kafka lag > threshold.

---

## ✅ Key Learnings

* Built an **end-to-end streaming + batch pipeline**.
* Applied **Medallion Architecture** on AWS S3.
* Combined **real-time (surge, dispatch)** with **batch analytics (Athena, QuickSight)**.
* Used **logging and monitoring best practices**.


