"""
Base Agent Class
All agents inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = "idle"
        self.last_execution = None
        self.execution_count = 0
        self.errors = []
        self.logs = []
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main task
        
        Args:
            context: Dictionary containing:
                - business_id: int
                - business_name: str
                - industry: str
                - city: str
                - state: str
                - investment: float
                - query: str (optional)
                - data: dict (optional - data from previous agents)
        
        Returns:
            Dictionary containing:
                - success: bool
                - data: dict
                - message: str
                - errors: list
        """
        pass
    
    def log(self, message: str, level: str = "info"):
        """Add log entry"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "agent": self.agent_id
        }
        self.logs.append(log_entry)
        print(f"[{self.agent_id}] {level.upper()}: {message}")
    
    def add_error(self, error: str):
        """Add error entry"""
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": error,
            "agent": self.agent_id
        }
        self.errors.append(error_entry)
        self.log(f"Error: {error}", "error")
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent with error handling and logging
        """
        self.status = "running"
        self.execution_count += 1
        self.log(f"Starting execution #{self.execution_count}")
        
        try:
            result = await self.execute(context)
            self.status = "completed"
            self.last_execution = datetime.utcnow().isoformat()
            self.log(f"Execution completed successfully")
            return result
        
        except Exception as e:
            self.status = "failed"
            self.add_error(str(e))
            self.log(f"Execution failed: {str(e)}", "error")
            return {
                "success": False,
                "data": {},
                "message": f"Agent {self.name} failed: {str(e)}",
                "errors": [str(e)]
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "last_execution": self.last_execution,
            "execution_count": self.execution_count,
            "error_count": len(self.errors),
            "recent_logs": self.logs[-10:] if self.logs else [],
            "recent_errors": self.errors[-5:] if self.errors else []
        }
    
    def reset(self):
        """Reset agent state"""
        self.status = "idle"
        self.logs = []
        self.errors = []
        self.log("Agent reset")
