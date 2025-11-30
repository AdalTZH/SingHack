"""
Import MSIG Travel Insurance Claims into Neo4j Graph Database
Creates nodes and relationships from claims JSON data
"""

from neo4j import GraphDatabase
import json
from datetime import datetime
from typing import List, Dict, Any


class Neo4jClaimsImporter:
    """Import claims data into Neo4j graph database"""

    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize Neo4j connection

        Args:
            uri: Neo4j connection URI (e.g., 'bolt://localhost:7687')
            user: Database username
            password: Database password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"✓ Connected to Neo4j at {uri}")

    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
        print("✓ Neo4j connection closed")

    def clear_database(self):
        """Clear all nodes and relationships (use with caution!)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✓ Database cleared")

    def create_constraints(self):
        """Create constraints and indexes for better performance"""
        with self.driver.session() as session:
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT claim_id IF NOT EXISTS FOR (c:Claim) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT destination_name IF NOT EXISTS FOR (d:Destination) REQUIRE d.name IS UNIQUE",
                "CREATE CONSTRAINT claim_type_name IF NOT EXISTS FOR (ct:ClaimType) REQUIRE ct.name IS UNIQUE",
                "CREATE CONSTRAINT cause_name IF NOT EXISTS FOR (ca:CauseOfLoss) REQUIRE ca.name IS UNIQUE",
                "CREATE CONSTRAINT loss_type_name IF NOT EXISTS FOR (lt:LossType) REQUIRE lt.name IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"  ✓ Created constraint")
                except Exception as e:
                    print(f"  ℹ Constraint already exists or error: {e}")

    def import_claims(self, claims_data: List[Dict[str, Any]]):
        """
        Import claims data into Neo4j graph

        Graph Model:
        - Claim nodes (with accident_date, gross_paid)
        - Destination nodes
        - ClaimType nodes
        - CauseOfLoss nodes
        - LossType nodes
        
        Relationships:
        - (Claim)-[:OCCURRED_IN]->(Destination)
        - (Claim)-[:IS_TYPE]->(ClaimType)
        - (Claim)-[:CAUSED_BY]->(CauseOfLoss)
        - (Claim)-[:HAS_LOSS_TYPE]->(LossType)
        """
        
        with self.driver.session() as session:
            for idx, claim in enumerate(claims_data, 1):
                # Create Claim node and relationships
                query = """
                // Create or merge Destination
                MERGE (dest:Destination {name: $destination})
                ON CREATE SET dest.created_at = datetime()
                
                // Create or merge ClaimType
                MERGE (ct:ClaimType {name: $claim_type})
                ON CREATE SET ct.created_at = datetime()
                
                // Create or merge CauseOfLoss
                MERGE (cause:CauseOfLoss {name: $cause_of_loss})
                ON CREATE SET cause.created_at = datetime()
                
                // Create or merge LossType
                MERGE (lt:LossType {name: $loss_type})
                ON CREATE SET lt.created_at = datetime()
                
                // Create Claim node
                CREATE (claim:Claim {
                    id: $claim_id,
                    accident_date: date($accident_date),
                    gross_paid: $gross_paid,
                    created_at: datetime()
                })
                
                // Create relationships
                CREATE (claim)-[:OCCURRED_IN]->(dest)
                CREATE (claim)-[:IS_TYPE]->(ct)
                CREATE (claim)-[:CAUSED_BY]->(cause)
                CREATE (claim)-[:HAS_LOSS_TYPE]->(lt)
                
                RETURN claim.id as claim_id
                """
                
                params = {
                    'claim_id': f"CLAIM_{idx}",
                    'accident_date': claim['accident_date'],
                    'destination': claim['destination'],
                    'claim_type': claim['claim_type'],
                    'cause_of_loss': claim['cause_of_loss'],
                    'loss_type': claim['loss_type'],
                    'gross_paid': float(claim['gross_paid'])
                }
                
                session.run(query, params)
                
                if idx % 100 == 0:
                    print(f"  Processed {idx} claims...")
            
            print(f"✓ Imported {len(claims_data)} claims into Neo4j")

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the imported graph"""
        with self.driver.session() as session:
            stats = {}
            
            # Count nodes by label
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
            """)
            stats['node_counts'] = [dict(record) for record in result]
            
            # Count relationships
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as relationship, count(r) as count
                ORDER BY count DESC
            """)
            stats['relationship_counts'] = [dict(record) for record in result]
            
            # Top destinations by claim count
            result = session.run("""
                MATCH (c:Claim)-[:OCCURRED_IN]->(d:Destination)
                RETURN d.name as destination, count(c) as claim_count
                ORDER BY claim_count DESC
                LIMIT 10
            """)
            stats['top_destinations'] = [dict(record) for record in result]
            
            # Top claim types
            result = session.run("""
                MATCH (c:Claim)-[:IS_TYPE]->(ct:ClaimType)
                RETURN ct.name as claim_type, count(c) as claim_count,
                       sum(c.gross_paid) as total_paid
                ORDER BY claim_count DESC
                LIMIT 10
            """)
            stats['top_claim_types'] = [dict(record) for record in result]
            
            return stats

    def example_queries(self):
        """Run example queries to demonstrate graph capabilities"""
        print("\n" + "="*70)
        print("EXAMPLE QUERIES")
        print("="*70)
        
        with self.driver.session() as session:
            # Query 1: Claims by destination
            print("\n1. Top 5 destinations by total paid amount:")
            result = session.run("""
                MATCH (c:Claim)-[:OCCURRED_IN]->(d:Destination)
                RETURN d.name as destination, 
                       count(c) as claim_count,
                       sum(c.gross_paid) as total_paid
                ORDER BY total_paid DESC
                LIMIT 5
            """)
            for record in result:
                print(f"   {record['destination']}: {record['claim_count']} claims, ${record['total_paid']:.2f}")
            
            # Query 2: Claims by cause and type
            print("\n2. Claim patterns (Cause -> Type):")
            result = session.run("""
                MATCH (c:Claim)-[:CAUSED_BY]->(cause:CauseOfLoss),
                      (c)-[:IS_TYPE]->(ct:ClaimType)
                RETURN cause.name as cause, ct.name as type, count(c) as count
                ORDER BY count DESC
                LIMIT 5
            """)
            for record in result:
                print(f"   {record['cause']} -> {record['type']}: {record['count']} claims")
            
            # Query 3: High value claims
            print("\n3. High value claims (>$500):")
            result = session.run("""
                MATCH (c:Claim)-[:OCCURRED_IN]->(d:Destination)
                WHERE c.gross_paid > 500
                RETURN c.accident_date as date, d.name as destination, 
                       c.gross_paid as amount
                ORDER BY c.gross_paid DESC
                LIMIT 5
            """)
            for record in result:
                print(f"   {record['date']} | {record['destination']} | ${record['amount']:.2f}")


def main():
    """Main execution function"""
    
    # Neo4j configuration
    NEO4J_CONFIG = {
        'uri': 'neo4j+s://68783b43.databases.neo4j.io',  # Change if needed
        'user': 'neo4j',                 # Change to your username
        'password': 'GEAVC0YDgq022XAXy7098osogQpPxfXmaFZJ4QKxrTc'           # Change to your password
    }
    
    # Input file
    INPUT_FILE = 'claims_data.json'
    
    print("="*70)
    print("MSIG TRAVEL INSURANCE CLAIMS - NEO4J IMPORT")
    print("="*70)
    
    try:
        # Load JSON data
        print(f"\nLoading data from {INPUT_FILE}...")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            claims_data = json.load(f)
        print(f"✓ Loaded {len(claims_data)} claims")
        
        # Initialize Neo4j importer
        importer = Neo4jClaimsImporter(
            uri=NEO4J_CONFIG['uri'],
            user=NEO4J_CONFIG['user'],
            password=NEO4J_CONFIG['password']
        )
        
        # Optional: Clear existing data (comment out if you want to keep existing data)
        print("\nClearing existing data...")
        importer.clear_database()
        
        # Create constraints
        print("\nCreating constraints and indexes...")
        importer.create_constraints()
        
        # Import claims
        print("\nImporting claims into Neo4j...")
        importer.import_claims(claims_data)
        
        # Get statistics
        print("\n" + "="*70)
        print("IMPORT STATISTICS")
        print("="*70)
        stats = importer.get_statistics()
        
        print("\nNode counts:")
        for item in stats['node_counts']:
            print(f"  {item['label']}: {item['count']}")
        
        print("\nRelationship counts:")
        for item in stats['relationship_counts']:
            print(f"  {item['relationship']}: {item['count']}")
        
        # Run example queries
        importer.example_queries()
        
        # Save statistics
        with open('neo4j_import_stats.json', 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        print(f"\n✓ Statistics saved to neo4j_import_stats.json")
        
        # Close connection
        importer.close()
        
        print("\n" + "="*70)
        print("IMPORT COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nYou can now query your graph database using Neo4j Browser")
        print(f"Connect to: {NEO4J_CONFIG['uri']}")
        
    except FileNotFoundError:
        print(f"✗ Error: Could not find {INPUT_FILE}")
        print("  Make sure you've run the export script first")
    except Exception as e:
        print(f"\n✗ Error during import: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()