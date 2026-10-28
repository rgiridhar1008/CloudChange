import pytest
import os
from unittest.mock import patch
from app.modules.ai_explanation.service import AIExplanationService
from app.core.config import settings

@pytest.mark.asyncio
async def test_fallback_provider():
    # Ensure no API key is set for this test
    with patch.object(settings, 'LLM_API_KEY', None):
        service = AIExplanationService()
        
        payload = {
            "risk_score": 85,
            "risk_level": "CRITICAL",
            "strategy": "CANARY",
            "affected_services": ["payment-service", "order-service"]
        }
        
        explanation = await service.get_explanation(payload)
        
        assert "CRITICAL" in explanation
        assert "85" in explanation
        assert "payment-service" in explanation
        assert "order-service" in explanation
        assert "CANARY" in explanation

@pytest.mark.asyncio
@patch('app.modules.ai_explanation.openai_provider.httpx.AsyncClient.post')
async def test_openai_provider_success(mock_post):
    with patch.object(settings, 'LLM_API_KEY', "test-key-123"):
        service = AIExplanationService()
        
        # Mock httpx response
        mock_response = mock_post.return_value.__aenter__.return_value
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This is a mocked AI explanation."}}]
        }
        mock_response.raise_for_status.return_value = None
        
        payload = {"risk_score": 50}
        explanation = await service.get_explanation(payload)
        
        assert explanation == "This is a mocked AI explanation."

@pytest.mark.asyncio
@patch('app.modules.ai_explanation.openai_provider.httpx.AsyncClient.post')
async def test_openai_provider_failure_fallback(mock_post):
    with patch.object(settings, 'LLM_API_KEY', "test-key-123"):
        service = AIExplanationService()
        
        # Simulate network timeout / error
        mock_post.side_effect = Exception("Connection Timeout")
        
        payload = {
            "risk_score": 10,
            "risk_level": "LOW",
            "strategy": "ROLLING"
        }
        
        # It should catch the exception and fall back
        explanation = await service.get_explanation(payload)
        
        # We expect the fallback deterministic string
        assert "LOW" in explanation
        assert "10" in explanation
        assert "ROLLING" in explanation
