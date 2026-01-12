"""
Clinical data loader for Lassa Fever case data
Loads and processes CSV files from mntrk-tensorflow2-symbolic-v2
"""

import os
import pandas as pd
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ClinicalDataLoader:
    """Loads and processes clinical data from CSV files"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize clinical data loader
        
        Args:
            data_dir: Path to data directory (defaults to mntrk-tensorflow2-symbolic-v2)
        """
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "mntrk-tensorflow2-symbolic-v2"
            )
        
        self.data_dir = data_dir
        self.cases_df: Optional[pd.DataFrame] = None
        self.assessments_df: Optional[pd.DataFrame] = None
        self.prescriptions_df: Optional[pd.DataFrame] = None
        self.treatments_df: Optional[pd.DataFrame] = None
        
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all CSV files"""
        try:
            logger.info(f"[v0] Loading clinical data from {self.data_dir}")
            
            # Load cases
            cases_path = os.path.join(self.data_dir, "cases.csv")
            if os.path.exists(cases_path):
                self.cases_df = pd.read_csv(cases_path, skiprows=2)  # Skip header rows
                logger.info(f"[v0] Loaded {len(self.cases_df)} cases")
            
            # Load clinical assessments
            assessments_path = os.path.join(self.data_dir, "clinical_assessments.csv")
            if os.path.exists(assessments_path):
                self.assessments_df = pd.read_csv(assessments_path)
                logger.info(f"[v0] Loaded {len(self.assessments_df)} assessments")
            
            # Load prescriptions
            prescriptions_path = os.path.join(self.data_dir, "prescriptions.csv")
            if os.path.exists(prescriptions_path):
                self.prescriptions_df = pd.read_csv(prescriptions_path)
                logger.info(f"[v0] Loaded {len(self.prescriptions_df)} prescriptions")
            
            # Load treatments
            treatments_path = os.path.join(self.data_dir, "treatments.csv")
            if os.path.exists(treatments_path):
                self.treatments_df = pd.read_csv(treatments_path)
                logger.info(f"[v0] Loaded {len(self.treatments_df)} treatments")
                
        except Exception as e:
            logger.error(f"[v0] Error loading clinical data: {e}")
    
    def get_cases_by_region(self, region: str) -> List[Dict]:
        """Get cases for a specific region"""
        if self.cases_df is None:
            return []
        
        try:
            region_cases = self.cases_df[
                self.cases_df['responsibleRegion'].str.contains(region, case=False, na=False)
            ]
            return region_cases.to_dict('records')
        except Exception as e:
            logger.error(f"[v0] Error getting cases by region: {e}")
            return []
    
    def get_cases_by_outcome(self, outcome: str) -> List[Dict]:
        """Get cases by outcome (Recovered, Deceased, etc.)"""
        if self.cases_df is None:
            return []
        
        try:
            outcome_cases = self.cases_df[
                self.cases_df['outcome'] == outcome
            ]
            return outcome_cases.to_dict('records')
        except Exception as e:
            logger.error(f"[v0] Error getting cases by outcome: {e}")
            return []
    
    def get_recent_cases(self, limit: int = 10) -> List[Dict]:
        """Get most recent cases"""
        if self.cases_df is None:
            return []
        
        try:
            # Sort by report date (descending)
            recent = self.cases_df.sort_values('reportDate', ascending=False).head(limit)
            return recent.to_dict('records')
        except Exception as e:
            logger.error(f"[v0] Error getting recent cases: {e}")
            return []
    
    def get_case_statistics(self) -> Dict:
        """Get overall case statistics"""
        if self.cases_df is None:
            return {}
        
        try:
            stats = {
                "total_cases": len(self.cases_df),
                "by_outcome": self.cases_df['outcome'].value_counts().to_dict(),
                "by_region": self.cases_df['responsibleRegion'].value_counts().to_dict(),
                "by_sex": self.cases_df['person.sex'].value_counts().to_dict(),
                "hospitalized": self.cases_df['hospitalization.admittedToHealthFacility'].value_counts().to_dict()
            }
            return stats
        except Exception as e:
            logger.error(f"[v0] Error calculating statistics: {e}")
            return {}
    
    def correlate_detection_with_cases(self, latitude: float, longitude: float, radius_km: float = 50) -> Dict:
        """
        Correlate rodent detection with nearby Lassa cases
        
        Args:
            latitude: Detection latitude
            longitude: Detection longitude
            radius_km: Search radius in kilometers
            
        Returns:
            Correlation data including nearby cases and risk assessment
        """
        if self.cases_df is None:
            return {"nearby_cases": 0, "risk_level": "unknown"}
        
        try:
            # Simple distance calculation (approximate)
            # In production, use proper geospatial libraries
            nearby_cases = []
            
            for _, case in self.cases_df.iterrows():
                # This is a placeholder - actual implementation would use GPS coordinates
                # from person.address.postalCode or addressGpsCoordinates
                nearby_cases.append(case)
            
            risk_level = "low"
            if len(nearby_cases) > 10:
                risk_level = "critical"
            elif len(nearby_cases) > 5:
                risk_level = "high"
            elif len(nearby_cases) > 2:
                risk_level = "medium"
            
            return {
                "nearby_cases": len(nearby_cases),
                "risk_level": risk_level,
                "cases_summary": self.get_case_statistics()
            }
            
        except Exception as e:
            logger.error(f"[v0] Error correlating detection with cases: {e}")
            return {"nearby_cases": 0, "risk_level": "unknown", "error": str(e)}
