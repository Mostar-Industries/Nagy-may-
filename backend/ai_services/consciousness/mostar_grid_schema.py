"""
Mostar Grid - Knowledge Graph Schema
------------------------------------
Defines the structure of the Neo4j graph nodes and relationships
for the Mostar surveillance network.
"""

# Neo4j Node Labels
LABEL_HABITAT = "Habitat"
LABEL_VECTOR = "Vector"  # Mastomys
LABEL_OUTBREAK = "Outbreak"
LABEL_COMMUNITY = "Community"

# Relationships
REL_DETECTED_IN = "DETECTED_IN"
REL_CLOSE_TO = "CLOSE_TO"
REL_RISK_FLOW = "FLOWS_TO"

def get_initial_schema():
    """Return Cypher queries to initialize the Mostar Grid schema."""
    return [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (v:Vector) REQUIRE v.id IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (h:Habitat) REQUIRE h.id IS UNIQUE;"
    ]
