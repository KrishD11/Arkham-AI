"""ADK Agent setup and initialization for Arkham AI"""

import os
import logging
from typing import Optional, Dict, Any

from agent.config import Config

logger = logging.getLogger(__name__)


class ADKAgent:
    """Google ADK Agent wrapper for Arkham AI"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize ADK Agent with configuration"""
        self.config = config or Config()
        self.agent = None
        self._initialized = False
        
        # Set up environment variables for ADK
        self._setup_environment()
    
    def _setup_environment(self):
        """Configure environment variables for ADK"""
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
        os.environ["GOOGLE_CLOUD_PROJECT"] = self.config.GOOGLE_CLOUD_PROJECT
        os.environ["GOOGLE_CLOUD_LOCATION"] = self.config.GOOGLE_CLOUD_LOCATION
        
        if self.config.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.config.GOOGLE_APPLICATION_CREDENTIALS
        
        logger.info(f"ADK environment configured for project: {self.config.GOOGLE_CLOUD_PROJECT}")
    
    def initialize(self) -> bool:
        """Initialize the ADK agent"""
        try:
            # Import ADK components
            from adk import Agent
            
            # Create agent configuration
            agent_config = {
                "name": self.config.AGENT_NAME,
                "model": "gemini-2.0-flash-exp",  # Using Gemini 2.0 Flash as specified
                "description": (
                    "An autonomous AI agent that monitors geopolitical risk and trade disruptions, "
                    "then automatically reroutes shipments to safer routes in real time."
                ),
                "instruction": self._get_agent_instruction(),
            }
            
            # Initialize the agent
            self.agent = Agent(**agent_config)
            self._initialized = True
            
            logger.info(f"{self.config.AGENT_NAME} ADK agent initialized successfully")
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import ADK: {e}")
            logger.warning("ADK not available. Using mock agent for development.")
            self._initialize_mock_agent()
            return False
        except Exception as e:
            logger.error(f"Failed to initialize ADK agent: {e}")
            self._initialize_mock_agent()
            return False
    
    def _initialize_mock_agent(self):
        """Initialize a mock agent for development/testing"""
        # Try to use Google Generative AI directly if ADK is not available
        try:
            import google.generativeai as genai
            import os
            
            # Set up Generative AI
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.agent = GenerativeAIAgent(self.config.AGENT_NAME, genai)
                self._initialized = True
                logger.info("Using Google Generative AI (Gemini) directly")
                return
            
            # Try Vertex AI if credentials are available
            if self.config.GOOGLE_APPLICATION_CREDENTIALS or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                try:
                    import vertexai
                    from google.cloud import aiplatform
                    
                    vertexai.init(
                        project=self.config.GOOGLE_CLOUD_PROJECT,
                        location=self.config.GOOGLE_CLOUD_LOCATION
                    )
                    self.agent = VertexAIAgent(self.config.AGENT_NAME)
                    self._initialized = True
                    logger.info("Using Vertex AI (Gemini) directly")
                    return
                except Exception as e:
                    logger.warning(f"Vertex AI initialization failed: {e}")
            
        except Exception as e:
            logger.warning(f"Could not initialize Generative AI: {e}")
        
        # Fallback to simple mock agent
        self.agent = MockAgent(self.config.AGENT_NAME)
        self._initialized = True
        logger.info("Mock agent initialized for development")
    
    def _get_agent_instruction(self) -> str:
        """Get the agent instruction prompt"""
        return """You are Arkham AI, an autonomous supply chain rerouting agent.

Your primary responsibilities:
1. Monitor geopolitical risks and trade disruptions in real-time
2. Assess risk levels for shipping routes using multiple data sources
3. Predict risk levels 3-7 days ahead using predictive analytics
4. Optimize routes by balancing risk, cost, and time
5. Automatically execute route changes when high risk is detected
6. Provide clear explanations for rerouting decisions

When analyzing routes, consider:
- Current geopolitical tensions and trade policies
- Port congestion and operational status
- Historical risk patterns
- Cost implications of route changes
- Time-to-delivery impacts

Always prioritize safety and reliability while minimizing disruption to supply chains."""

    def query(self, message: str, user_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Query the ADK agent"""
        if not self._initialized:
            self.initialize()
        
        try:
            # Prepare query context
            context = {
                "user_id": user_id,
                "project": self.config.GOOGLE_CLOUD_PROJECT,
                **kwargs
            }
            
            # Execute query
            response = self.agent.query(message, context=context)
            
            return {
                "success": True,
                "response": response,
                "agent": self.config.AGENT_NAME
            }
            
        except Exception as e:
            logger.error(f"Error querying agent: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.config.AGENT_NAME
            }
    
    def is_initialized(self) -> bool:
        """Check if agent is initialized"""
        return self._initialized
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.config.AGENT_NAME,
            "initialized": self._initialized,
            "project": self.config.GOOGLE_CLOUD_PROJECT,
            "location": self.config.GOOGLE_CLOUD_LOCATION,
            "model": "gemini-2.0-flash-exp"
        }


class GenerativeAIAgent:
    """Google Generative AI (Gemini) agent wrapper"""
    
    def __init__(self, name: str, genai_module):
        self.name = name
        self.genai = genai_module
        self.model = self.genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def query(self, message: str, context: Optional[Dict] = None) -> str:
        """Query Gemini model"""
        try:
            response = self.model.generate_content(message)
            return response.text
        except Exception as e:
            logger.error(f"Generative AI query failed: {e}")
            return f"Error generating AI response: {str(e)}"


class VertexAIAgent:
    """Vertex AI (Gemini) agent wrapper"""
    
    def __init__(self, name: str):
        self.name = name
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            self.model = GenerativeModel('gemini-2.0-flash-exp')
        except Exception as e:
            logger.error(f"Vertex AI model initialization failed: {e}")
            self.model = None
    
    def query(self, message: str, context: Optional[Dict] = None) -> str:
        """Query Vertex AI Gemini model"""
        if not self.model:
            return "Vertex AI model not available"
        try:
            response = self.model.generate_content(message)
            return response.text
        except Exception as e:
            logger.error(f"Vertex AI query failed: {e}")
            return f"Error generating AI response: {str(e)}"


class MockAgent:
    """Mock agent for development when ADK is not available"""
    
    def __init__(self, name: str):
        self.name = name
    
    def query(self, message: str, context: Optional[Dict] = None) -> str:
        """Mock query response"""
        return f"[Mock Agent] Received query: {message}. ADK agent not available - using mock response for development."


# Global agent instance
_agent_instance: Optional[ADKAgent] = None


def get_agent() -> ADKAgent:
    """Get or create the global ADK agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ADKAgent()
        _agent_instance.initialize()
    return _agent_instance


def initialize_agent(config: Optional[Config] = None) -> ADKAgent:
    """Initialize and return ADK agent"""
    global _agent_instance
    _agent_instance = ADKAgent(config)
    _agent_instance.initialize()
    return _agent_instance

