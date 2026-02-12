// ===================================================
// INSURANCE FRAUD DETECTION - NEO4J QUERIES
// ===================================================

// 1.Find duplicate phone numbers
MATCH (i:Insured)-[:HAS_PHONE]->(p:Phone)<-[:HAS_PHONE]-(other:Insured)
WHERE i.id <> other.id
RETURN p.number AS duplicate_phone,
       collect(DISTINCT i.name) AS users,
       count(other) AS share_count
ORDER BY share_count DESC


// 2.Find duplicate addresses
MATCH (i:Insured)-[:HAS_ADDRESS]->(a:Address)<-[:HAS_ADDRESS]-(other:Insured)
WHERE i.id <> other.id
RETURN a.text AS duplicate_address,
       collect(DISTINCT i.name) AS users,
       count(other) AS share_count
ORDER BY share_count DESC


// 3.Calculate fraud score for a specific insured
MATCH (i:Insured {id: $insured_id})
OPTIONAL MATCH (i)-[:HAS_PHONE]->(p)<-[:HAS_PHONE]-(phone_fraud)
WHERE phone_fraud.id <> i.id
WITH i, COUNT(DISTINCT phone_fraud) * 30 AS phone_score
OPTIONAL MATCH (i)-[:HAS_ADDRESS]->(a)<-[:HAS_ADDRESS]-(address_fraud)
WHERE address_fraud.id <> i.id
RETURN i.name,
       phone_score + COUNT(DISTINCT address_fraud) * 20 AS fraud_score


// 4.ind all high-risk insureds (score > 30)
MATCH (i:Insured)
OPTIONAL MATCH (i)-[:HAS_PHONE]->(p)<-[:HAS_PHONE]-(pf)
OPTIONAL MATCH (i)-[:HAS_ADDRESS]->(a)<-[:HAS_ADDRESS]-(af)
WITH i,
     COUNT(DISTINCT pf) * 30 + COUNT(DISTINCT af) * 20 AS score
WHERE score > 30
RETURN i.name, score
ORDER BY score DESC


// 5.Display complete graph visualization
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 50


// 6.Clear entire graph (for reset)
// MATCH (n) DETACH DELETE n


