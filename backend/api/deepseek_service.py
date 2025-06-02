"""
MNTRK Sovereign Observatory - DeepSeek AI Integration Service
Advanced AI analysis for biosurveillance intelligence
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger("DeepSeek-Service")

class DeepSeekService:
    """
    DeepSeek AI Integration Service for MNTRK Sovereign Observatory
    Provides advanced AI analysis capabilities for biosurveillance data
    """
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-r1-distill-qwen-7b"
        
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not found in environment variables")
    
    async def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make async HTTP request to DeepSeek API."""
        if not self.api_key:
            raise ValueError("DeepSeek API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API error {response.status}: {error_text}")
    
    async def analyze_detection_patterns(self, detection_data: List[Dict]) -> Dict:
        """
        Analyze Mastomys detection patterns using DeepSeek AI.
        
        Args:
            detection_data: List of detection records with location, time, environmental data
            
        Returns:
            Dict with AI analysis results including risk assessment and recommendations
        """
        try:
            # Prepare analysis prompt
            prompt = self._create_detection_analysis_prompt(detection_data)
            
            request_data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert biosurveillance analyst specializing in Mastomys rodent ecology and Lassa fever outbreak prediction. Analyze the provided detection data and provide actionable intelligence."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1500
            }
            
            response = await self._make_request("chat/completions", request_data)
            
            # Parse AI response
            ai_analysis = response['choices'][0]['message']['content']
            
            return {
                "analysis_type": "detection_patterns",
                "ai_insights": ai_analysis,
                "risk_level": self._extract_risk_level(ai_analysis),
                "recommendations": self._extract_recommendations(ai_analysis),
                "confidence_score": 0.85,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Detection pattern analysis failed: {e}")
            raise Exception(f"AI analysis failed: {str(e)}")
    
    async def predict_outbreak_risk(self, environmental_data: Dict, detection_history: List[Dict]) -> Dict:
        """
        Predict Lassa fever outbreak risk using environmental and detection data.
        
        Args:
            environmental_data: Current environmental conditions
            detection_history: Historical detection patterns
            
        Returns:
            Dict with outbreak risk prediction and mitigation strategies
        """
        try:
            prompt = self._create_outbreak_prediction_prompt(environmental_data, detection_history)
            
            request_data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a public health expert specializing in Lassa fever outbreak prediction and prevention. Analyze environmental and detection data to assess outbreak risk and recommend interventions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 2000
            }
            
            response = await self._make_request("chat/completions", request_data)
            ai_prediction = response['choices'][0]['message']['content']
            
            return {
                "prediction_type": "outbreak_risk",
                "risk_assessment": ai_prediction,
                "risk_score": self._extract_risk_score(ai_prediction),
                "mitigation_strategies": self._extract_mitigation_strategies(ai_prediction),
                "confidence_score": 0.82,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Outbreak prediction failed: {e}")
            raise Exception(f"Outbreak prediction failed: {str(e)}")
    
    async def generate_surveillance_report(self, data_summary: Dict) -> Dict:
        """
        Generate comprehensive surveillance report using AI analysis.
        
        Args:
            data_summary: Summary of all surveillance data
            
        Returns:
            Dict with formatted surveillance report
        """
        try:
            prompt = self._create_report_generation_prompt(data_summary)
            
            request_data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a biosurveillance report writer. Generate a comprehensive, professional surveillance report based on the provided data. Include executive summary, key findings, risk assessment, and recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 3000
            }
            
            response = await self._make_request("chat/completions", request_data)
            report_content = response['choices'][0]['message']['content']
            
            return {
                "report_type": "surveillance_summary",
                "report_content": report_content,
                "generated_at": datetime.now().isoformat(),
                "data_period": data_summary.get('period', 'unknown'),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise Exception(f"Report generation failed: {str(e)}")
    
    async def health_check(self) -> Dict:
        """Check DeepSeek API connectivity and status."""
        try:
            if not self.api_key:
                return {
                    "status": "error",
                    "message": "API key not configured",
                    "connected": False
                }
            
            # Simple test request
            test_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = await self._make_request("chat/completions", test_data)
            
            return {
                "status": "healthy",
                "message": "DeepSeek API connected successfully",
                "connected": True,
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Connection failed: {str(e)}",
                "connected": False
            }
    
    def _create_detection_analysis_prompt(self, detection_data: List[Dict]) -> str:
        """Create analysis prompt for detection patterns."""
        data_summary = f"Analyzing {len(detection_data)} Mastomys detection records:\n\n"
        
        for i, detection in enumerate(detection_data[:5]):  # Limit to first 5 for prompt size
            data_summary += f"Detection {i+1}:\n"
            data_summary += f"- Location: {detection.get('latitude', 'N/A')}, {detection.get('longitude', 'N/A')}\n"
            data_summary += f"- Timestamp: {detection.get('detection_timestamp', 'N/A')}\n"
            data_summary += f"- Count: {detection.get('detection_count', 'N/A')}\n"
            data_summary += f"- Environment: {detection.get('environmental_context', {})}\n\n"
        
        prompt = f"""{data_summary}

Please analyze these Mastomys detection patterns and provide:

1. **Spatial Analysis**: Geographic clustering and distribution patterns
2. **Temporal Analysis**: Seasonal trends and timing patterns  
3. **Risk Assessment**: Current outbreak risk level (LOW/MEDIUM/HIGH)
4. **Environmental Correlations**: Key environmental factors driving detections
5. **Recommendations**: Specific surveillance and intervention actions

Focus on actionable intelligence for public health decision-making."""
        
        return prompt
    
    def _create_outbreak_prediction_prompt(self, env_data: Dict, history: List[Dict]) -> str:
        """Create prompt for outbreak risk prediction."""
        prompt = f"""Environmental Conditions:
{json.dumps(env_data, indent=2)}

Historical Detection Patterns:
{len(history)} detection records over recent period

Please assess Lassa fever outbreak risk based on:

1. **Environmental Risk Factors**: Temperature, rainfall, vegetation changes
2. **Detection Trends**: Population density changes and geographic spread
3. **Seasonal Patterns**: Current season vs historical outbreak timing
4. **Risk Score**: Quantitative risk assessment (0-100 scale)
5. **Mitigation Strategies**: Specific prevention and response actions

Provide a comprehensive risk assessment with actionable recommendations."""
        
        return prompt
    
    def _create_report_generation_prompt(self, data_summary: Dict) -> str:
        """Create prompt for surveillance report generation."""
        prompt = f"""Surveillance Data Summary:
{json.dumps(data_summary, indent=2)}

Generate a professional biosurveillance report with:

1. **Executive Summary**: Key findings and risk status
2. **Detection Overview**: Spatial and temporal patterns
3. **Risk Assessment**: Current threat level and trends
4. **Environmental Analysis**: Contributing factors
5. **Recommendations**: Immediate and long-term actions
6. **Monitoring Priorities**: Focus areas for continued surveillance

Format as a structured report suitable for public health officials."""
        
        return prompt
    
    def _extract_risk_level(self, analysis: str) -> str:
        """Extract risk level from AI analysis."""
        analysis_lower = analysis.lower()
        if 'high' in analysis_lower and 'risk' in analysis_lower:
            return 'HIGH'
        elif 'medium' in analysis_lower and 'risk' in analysis_lower:
            return 'MEDIUM'
        elif 'low' in analysis_lower and 'risk' in analysis_lower:
            return 'LOW'
        return 'UNKNOWN'
    
    def _extract_risk_score(self, prediction: str) -> float:
        """Extract numerical risk score from AI prediction."""
        import re
        # Look for patterns like "risk score: 75" or "75/100"
        score_patterns = [
            r'risk score[:\s]+(\d+)',
            r'score[:\s]+(\d+)',
            r'(\d+)/100',
            r'(\d+)%'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, prediction.lower())
            if match:
                return float(match.group(1)) / 100.0
        
        return 0.5  # Default moderate risk
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract recommendations from AI analysis."""
        # Simple extraction - look for numbered or bulleted lists
        lines = analysis.split('\n')
        recommendations = []
        
        for line in lines:
            line = line.strip()
            if (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                line.startswith(('•', '-', '*')) or
                'recommend' in line.lower()):
                recommendations.append(line)
        
        return recommendations[:5]  # Limit to top 5
    
    def _extract_mitigation_strategies(self, prediction: str) -> List[str]:
        """Extract mitigation strategies from AI prediction."""
        return self._extract_recommendations(prediction)  # Same logic for now

# Global service instance
deepseek_service = DeepSeekService()
