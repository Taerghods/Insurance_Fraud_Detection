# Insurance_Fraud_Detection
# Insurance Fraud Detection System 🛡️

Real-time insurance claim fraud detection system with Event-Driven Architecture


[![Django](https://img.shields.io/badge/Django-4.2-green)](https://djangoproject.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-5-cyan)](https://neo4j.com)
[![NATS](https://img.shields.io/badge/NATS-2.10-blue)](https://nats.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-navy)](https://postgresql.org)

---

## 📐 System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   پنل مدیریت Django                      │
│              (ثبت خسارت، مشاهده هشدارها)                 │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│                    Django REST API                       │
│              POST /api/claims/ (ثبت خسارت)               │
└─────────┬────────────────────────┬───────────────────────┘
          │                        │
          ▼                        ▼
┌─────────────────┐      ┌─────────────────┐
│   PostgreSQL    │      │     Neo4j       │
├─────────────────┤      ├─────────────────┤
│ • بیمه‌شدگان    │      │ • گره: بیمه‌شده │
│ • خسارت‌ها      │      │ • گره: شماره    │
│ • شرکت‌های بیمه │      │ • گره: آدرس     │
│ • کارشناسان     │      │ • یال: «دارای»  │
└─────────────────┘      └────────┬────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │  NATS Server    │
                        │  "fraud.alert"  │
                        └─────────────────┘
```

---

## 🧠 Fraud Detection Algorithm

```cypher
// Detect shared phone numbers or addresses
MATCH (p:PolicyHolder {id: $id})
OPTIONAL MATCH (p)-[:HAS_PHONE]->(phone:Phone)<-[:HAS_PHONE]-(suspect)
OPTIONAL MATCH (p)-[:HAS_ADDRESS]->(addr:Address)<-[:HAS_ADDRESS]-(other)
RETURN 
    collect(DISTINCT phone.number) as shared_phones,
    collect(DISTINCT suspect.name) as phone_sharers,
    collect(DISTINCT addr.text) as shared_addresses
```

---

## 🛠 Technologies

- **Django**: Backend and admin panel
- **PostgreSQL**: Primary database
- **Neo4j**: Graph database for relationship analysis
- **NATS**: Event-driven message broker
- **Docker**: Containerization


