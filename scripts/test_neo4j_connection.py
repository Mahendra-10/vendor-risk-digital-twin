"""Test Neo4j Aura connection"""
import sys
from pathlib import Path
from neo4j import GraphDatabase

sys.path.append(str(Path(__file__).parent.parent))

from scripts.utils import load_config

def test_connection():
    """Test Neo4j connection"""
    config = load_config()
    neo4j_config = config['neo4j']
    
    uri = neo4j_config['uri']
    user = neo4j_config['user']
    password = neo4j_config['password']
    
    print(f"Testing Neo4j connection...")
    print(f"URI: {uri}")
    print(f"User: {user}")
    print(f"Password: {'*' * len(password)}")
    print()
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test connection
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            print(f"✅ Connection successful! Test query returned: {record['test']}")
            
            # Try to get database info
            result = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions[0] as version, edition")
            print("\n📊 Database Info:")
            for record in result:
                print(f"  - {record['name']}: {record['version']} ({record['edition']})")
            
            # Check if we have any data
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = result.single()['node_count']
            print(f"\n📈 Graph Stats:")
            print(f"  - Total nodes: {node_count}")
            
            if node_count == 0:
                print("\n⚠️  Warning: Database is empty. Load data with:")
                print("   python scripts/load_graph.py --data-file data/sample/sample_dependencies.json")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"\nError type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

