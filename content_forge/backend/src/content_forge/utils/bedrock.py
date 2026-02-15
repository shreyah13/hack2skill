"""AWS Bedrock AI service integration."""

import json
import logging
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class BedrockClient:
    """AWS Bedrock client for AI services."""
    
    def __init__(self, region: str = "us-east-1"):
        """Initialize Bedrock client."""
        self.bedrock = boto3.client('bedrock-runtime', region_name)
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    def invoke_claude(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Invoke Claude model for text generation."""
        try:
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
        except ClientError as e:
            logger.error(f"Error invoking Claude: {e}")
            return None
    
    def generate_topics(self, niche: str, audience: str, keywords: List[str]) -> Optional[List[Dict]]:
        """Generate topic suggestions."""
        prompt = f"""
        Generate 5 engaging content topics for a {niche} creator targeting {audience}.
        
        Keywords to consider: {', '.join(keywords) if keywords else 'None'}
        
        For each topic, provide:
        1. Catchy title (under 60 characters)
        2. Brief description (2-3 sentences)
        3. Predicted CTR (0-100%)
        4. Competitiveness (low/medium/high)
        5. Trending score (0-100)
        6. 5 relevant keywords
        
        Return as JSON array.
        """
        
        response = self.invoke_claude(prompt)
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.error("Failed to parse topics response")
        return None
    
    def generate_script_section(self, section: str, topic: str, tone: str = "casual") -> Optional[str]:
        """Generate script section."""
        prompts = {
            "hook": f"Create an attention-grabbing hook for: {topic}. Keep it under 40 words. Tone: {tone}.",
            "introduction": f"Write a compelling introduction for: {topic}. 50-75 words. Tone: {tone}.",
            "main": f"Create main content outline for: {topic}. 3-5 key points with details. Tone: {tone}.",
            "cta": f"Write an effective call-to-action for: {topic}. 25-40 words. Tone: {tone}."
        }
        
        prompt = prompts.get(section, prompts["main"])
        return self.invoke_claude(prompt, max_tokens=500)
    
    def analyze_retention(self, script_content: str) -> Optional[Dict]:
        """Analyze script for retention risks."""
        prompt = f"""
        Analyze this script for retention risks:
        
        {script_content}
        
        Provide analysis as JSON:
        {{
            "overall_score": 0-100,
            "hook_strength": 0-100,
            "pacing_score": 0-100,
            "clarity_score": 0-100,
            "risk_sections": [
                {{
                    "section": "hook/introduction/main/cta",
                    "risk_level": "low/medium/high",
                    "issues": ["issue1", "issue2"],
                    "suggestions": ["suggestion1", "suggestion2"]
                }}
            ],
            "recommendations": ["rec1", "rec2"]
        }}
        """
        
        response = self.invoke_claude(prompt, max_tokens=1000)
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.error("Failed to parse retention analysis")
        return None
