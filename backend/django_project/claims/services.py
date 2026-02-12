# backend/django_project/claims/services.py
from neo4j import GraphDatabase


def sync_all_to_neo4j():
    """Sync all data from PostgreSQL to Neo4j"""
    from .models import Insured
    neo4j = Neo4jClient()

    # Delete existing Neo4j data (optional - comment if not needed)
    # with neo4j.driver.session() as session:
    #     session.run("MATCH (n) DETACH DELETE n")

    for insured in Insured.objects.all():
        neo4j.create_insured_node(insured)

    neo4j.close()
    print("✅ All insured members synced to Neo4j")


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://neo4j:7687",
            auth=("neo4j", "password123")
        )

    def close(self):
        self.driver.close()

    def create_insured_node(self, insured):
        """Create insured node in Neo4j with intelligent duplicate handling for phone and address"""
        with self.driver.session() as session:
            # Delete existing node (if any)
            session.run("MATCH (i:Insured {id: $id}) DETACH DELETE i", id=insured.id)

            # Create insured node
            session.run("""
                CREATE (i:Insured {
                    id: $id,
                    name: $name,
                    national_code: $national_code
                })
            """,
                id=insured.id,
                name=insured.full_name,
                national_code=insured.national_code
            )

            # Phone number - MERGE prevents duplicates!
            session.run("""
                MATCH (i:Insured {id: $id})
                MERGE (p:Phone {number: $phone})
                MERGE (i)-[:HAS_PHONE]->(p)
            """,
                id=insured.id,
                phone=insured.phone_number
            )

            # Address - MERGE prevents duplicates!
            session.run("""
                MATCH (i:Insured {id: $id})
                MERGE (a:Address {text: $address})
                MERGE (i)-[:HAS_ADDRESS]->(a)
            """,
                id=insured.id,
                address=insured.address
            )

            print(f"✅ {insured.full_name} added to Neo4j")

    def check_fraud(self, insured_id):
        """Fraud detection - duplicate phone numbers and addresses"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (i:Insured {id: $id})

                // Duplicate phone numbers
                OPTIONAL MATCH (i)-[:HAS_PHONE]->(phone:Phone)<-[:HAS_PHONE]-(other:Insured)
                WHERE other.id <> i.id

                // Duplicate addresses
                OPTIONAL MATCH (i)-[:HAS_ADDRESS]->(addr:Address)<-[:HAS_ADDRESS]-(other2:Insured)
                WHERE other2.id <> i.id

                RETURN 
                    count(DISTINCT other) as phone_fraud_count,
                    count(DISTINCT other2) as address_fraud_count,
                    collect(DISTINCT other.name) as phone_sharers,
                    collect(DISTINCT other2.name) as address_sharers
            """, id=insured_id)

            return result.single()

    def get_fraud_score(self, insured_id):
        """Get fraud score from Neo4j"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (i:Insured {id: $id})
                OPTIONAL MATCH (i)-[:HAS_PHONE]->(p)<-[:HAS_PHONE]-(phone_frauds:Insured)
                WHERE phone_frauds.id <> i.id
                WITH i, COUNT(DISTINCT phone_frauds) AS phone_fraud_count
                OPTIONAL MATCH (i)-[:HAS_ADDRESS]->(a)<-[:HAS_ADDRESS]-(address_frauds:Insured)
                WHERE address_frauds.id <> i.id
                RETURN phone_fraud_count * 30 + address_fraud_count * 20 AS fraud_score
            """, id=insured_id)

            record = result.single()
            return record["fraud_score"] if record else 0