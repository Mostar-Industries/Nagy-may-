import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SORMASParser:
    """
    Parser for SORMAS (Surveillance Outbreak Response Management and Analysis System) data.
    Used for epidemiological data integration.
    """
    
    # SORMAS Lassa fever relevant fields
    LASSA_FIELDS = {
        "caseClassification": {
            "type": "enum",
            "description": "Case classification (CONFIRMED, PROBABLE, SUSPECT, NOT_CLASSIFIABLE)",
            "values": ["CONFIRMED", "PROBABLE", "SUSPECT", "NOT_CLASSIFIABLE"]
        },
        "outcome": {
            "type": "enum",
            "description": "Case outcome",
            "values": ["NO_OUTCOME", "RECOVERED", "DECEASED", "UNKNOWN"]
        },
        "reportDate": {
            "type": "date",
            "description": "Date case was reported"
        },
        "symptomsOnsetDate": {
            "type": "date",
            "description": "Date symptoms began"
        },
        "region": {
            "type": "string",
            "description": "Administrative region"
        },
        "district": {
            "type": "string",
            "description": "District within region"
        },
        "healthFacility": {
            "type": "reference",
            "description": "Treating health facility"
        },
        "hospitalization": {
            "type": "object",
            "description": "Hospitalization details"
        },
        "symptoms": {
            "type": "object",
            "description": "Clinical symptoms object"
        },
        "epidemiologicalData": {
            "type": "object",
            "description": "Exposure and contact data"
        }
    }
    
    def __init__(self, data_dict_path: str = None):
        """Initialize parser with optional data dictionary path"""
        self.fields = self.LASSA_FIELDS.copy()
        logger.info("[SORMASParser] Initialized with Lassa fever schema")
    
    def get_all_fields(self) -> List[str]:
        """Get list of all field names"""
        return list(self.fields.keys())
    
    def get_field_definition(self, field_name: str) -> Optional[Dict[str, Any]]:
        """Get definition for a specific field"""
        return self.fields.get(field_name)
    
    def parse_case(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw SORMAS case data into normalized format"""
        return {
            "id": raw_data.get("uuid"),
            "classification": raw_data.get("caseClassification"),
            "outcome": raw_data.get("outcome"),
            "report_date": raw_data.get("reportDate"),
            "onset_date": raw_data.get("symptomsOnsetDate"),
            "region": raw_data.get("region", {}).get("caption"),
            "district": raw_data.get("district", {}).get("caption"),
            "coordinates": {
                "lat": raw_data.get("reportLat"),
                "lon": raw_data.get("reportLon")
            }
        }
