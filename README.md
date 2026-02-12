# Insurance Fraud Detection System

### Real-time insurance claim fraud detection system with Event-Driven Architecture with NATS


---

## 🎯 **What is this project?**

A **real-time fraud detection system** for insurance companies that **instantly** identifies whether a claim is suspicious or not at the moment it's submitted!

---

## 🔥 **The Problem**

| Issue | Description |
|-------|-------------|
| **Organized Fraud** | One person files multiple claims using different phone numbers and addresses |
| **Slow Traditional Databases** | Finding duplicate phone/address with PostgreSQL JOIN takes several seconds |
| **Late Alerts** | Insurance experts discover fraud patterns too late |

---

## 💡 **The Solution**

### **Hybrid Architecture: PostgreSQL + Neo4j + NATS**

---

## 📬 Real-time Alerts

When a claim receives a fraud score ≥ 30, the system publishes a NATS event.

**To see alerts in real-time:**
```bash
docker exec -it fraud_django python manage.py nats_listener
```

**You'll see:**
```
📬 Received: {'claim_id': 5, 'fraud_score': 480, 'severity': 'high'}
🚨 Fraud alert for claim CL-000005
```

> 📌 **Note:** This is a demonstration of event-driven architecture. 
> The current implementation shows alerts in the console, 
> but can be extended to email, SMS, or other services by adding NATS subscribers.

---

## 📐 System Architecture

```
PostgreSQL  ←  Django  →  Neo4j
              ⬇️
            NATS
         (fraud.alert)
```
**Data Flow:**
1. **Admin** creates Insured/Claim → Django Signals auto-sync to Neo4j
2. **Neo4j** calculates fraud score (30pts phone + 20pts address)
3. **Score ≥ 30** → NATS publishes `fraud.alert`

---

## ✨ **What does it do?**

### ✅ **1. Fraud Detection in 0.1s!**
- **Duplicate Phone Number** → 30 points
- **Duplicate Address** → 20 points
- **Total Score** = Sum of both

### ✅ **2. Automatic Synchronization**
- Every `Insured` created in admin is **automatically** synced to Neo4j
- Zero additional code required!

### ✅ **3. Real-time Alerts with NATS**
- Score ≥ 30 → Fraud alert published instantly
- **145,000 messages/second!** 🚀

### ✅ **4. Smart Admin Panel**
- Color-coded fraud scores (red/orange/green)
- Filter by fraud score
- Automatic fraud alert display

---

## 🛠 Technologies

| Technology | Purpose |
|-----------|---------|
| **Django 4.2** | Backend & Admin Panel |
| **PostgreSQL 15** | Primary Database |
| **Neo4j 5** | Graph Database for Relationship Detection |
| **NATS 2.10** | Event-driven Message Broker (145k/sec) |
| **Docker** | Containerization |

---

## 🚀 **Quick Start:**

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/insurance-fraud-detection
cd insurance-fraud-detection

# 2. Run with Docker
docker-compose up -d --build

# 3. Access Django Admin
http://localhost:8000/admin

# 4. Access Neo4j Browser
http://localhost:7474

# 5. Listen to NATS alerts
docker exec -it fraud_django python manage.py nats_listener
```
---

## 📁 **Project Structure:**
```
Insurance_Fraud_Detection/
├── backend/
│   └── django_project/
│       ├── .venv/ 
│       ├── claims/                     # Main application
│       │   ├── management/ commands/
│       │   │   ├── nats_listener.py    # Listen to live fraud alerts
│       │   │   └── sync_neo4j.py       # Force full database sync    
│       │   ├── models.py        
│       │   ├── admin.py         
│       │   ├── services.py             # Neo4j client
│       │   ├── signals.py              # Auto-sync magic
│       │   ├── nats_client.py          # Message broker
│       │   └── tests.py                # 10 passing tests
│       ├── src/                        # Django settings
│       ├── manage.py
│       ├── Dockerfile
│       └── requirements.txt
├── docs/
│   ├── neo4j-queries.cypher            # Cypher queries
│   └── nats-events.json                # NATS schemas
├── docker-compose.yml                  # PostgreSQL + Neo4j + NATS + Django
├── .env                                # Environment variables
└── README.md                           # You are here!
```
---

## 👥 **Who can use this?**
- 🏢 Insurance Companies - Detect fraudulent claims
- 🏦 Banks - Identify suspicious transactions
- 📱 Telecom Operators - Detect duplicate SIM registrations
- 🚗 Leasing Companies - Risk assessment for customers

---

## 🎓 **What you'll learn from this project:**
- ✅ Event-Driven Architecture with NATS
- ✅ Graph Database (Neo4j) for relationship analysis
- ✅ Cypher Query Language
- ✅ Django Signals for auto-synchronization
- ✅ Professional Testing practices
- ✅ Docker Compose for Microservices



