"""
SORMAS data dictionary parser
Processes the SORMAS Excel data dictionary for field definitions
"""

import os
import pandas as pd
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SORMASParser:
    """Parse and query SORMAS data dictionary"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize SORMAS parser
        
        Args:
            data_dir: Path to data directory containing SORMAS dictionary
        """
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "mntrk-tensorflow2-symbolic-v2"
            )
        
        self.data_dir = data_dir
        self.dictionary_df: Optional[pd.DataFrame] = None
        self._load_dictionary()
    
    def _load_dictionary(self):
        """Load SORMAS data dictionary from Excel file"""
        try:
            dict_path = os.path.join(
                self.data_dir,
                "sormas_data_dictionary_2025-10-29_.xlsx"
            )
            
            if os.path.exists(dict_path):
                self.dictionary_df = pd.read_excel(dict_path)
                logger.info(f"[v0] Loaded SORMAS dictionary with {len(self.dictionary_df)} fields")
            else:
                logger.warning(f"[v0] SORMAS dictionary not found at {dict_path}")
                
        except Exception as e:
            logger.error(f"[v0] Error loading SORMAS dictionary: {e}")
    
    def get_field_definition(self, field_name: str) -> Optional[Dict]:
        """Get definition for a specific field"""
        if self.dictionary_df is None:
            return None
        
        try:
            field_data = self.dictionary_df[
                self.dictionary_df['Field'].str.contains(field_name, case=False, na=False)
            ]
            
            if not field_data.empty:
                return field_data.iloc[0].to_dict()
            return None
            
        except Exception as e:
            logger.error(f"[v0] Error getting field definition: {e}")
            return None
    
    def get_all_fields(self) -> List[str]:
        """Get list of all available fields"""
        if self.dictionary_df is None:
            return []
        
        try:
            return self.dictionary_df['Field'].tolist()
        except Exception as e:
            logger.error(f"[v0] Error getting fields: {e}")
            return []
    
    def validate_case_data(self, case_data: Dict) -> Dict:
        """
        Validate case data against SORMAS schema
        
        Args:
            case_data: Dictionary of case data
            
        Returns:
            Validation results with errors and warnings
        """
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['disease', 'reportDate', 'region', 'district']
        
        for field in required_fields:
            if field not in case_data or not case_data[field]:
                errors.append(f"Missing required field: {field}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
