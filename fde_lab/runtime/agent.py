from typing import List, Optional
from fde_lab.tools.base import Tool
from fde_lab.runtime.memory import Memory
from fde_lab.observability.logger import get_logger

logger = get_logger("fde_lab.agent")

class Agent:
    """Core execution loop for FDE Lab."""
    
    def __init__(self, name: str, instructions: str, tools: Optional[List[Tool]] = None):
        self.name = name
        self.instructions = instructions
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.memory = Memory()
        logger.info(f"Initialized agent {self.name}", tools=list(self.tools.keys()))
        
    def run(self, user_input: str) -> str:
        """Run the agent loop."""
        logger.info("Agent received input", input=user_input)
        self.memory.add_message("user", user_input)
        
        # In a real implementation, this is where we query the LLM.
        # For this minimal slice, we use a simple rule-based router 
        # to prove the architecture (Agent -> Tool -> Result).
        
        if "services" in user_input.lower() and "get_services" in self.tools:
            logger.info("Agent decided to use tool", tool="get_services")
            tool = self.tools["get_services"]
            result = tool.execute()
            self.memory.add_message("tool", str(result), tool_name="get_services")
            logger.info("Tool execution complete", result=result)
            
            # Simulate LLM synthesizing the tool output
            response = f"I checked the environment. Currently running services are: "
            running = [s['name'] for s in result['services'] if s['status'] == 'running']
            response += ", ".join(running) + "."
        else:
            response = "I am a simple demo agent. Try asking me about 'services'."
            
        self.memory.add_message("assistant", response)
        logger.info("Agent generated response", response=response)
        
        return response
