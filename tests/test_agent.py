from fde_lab.runtime.agent import Agent
from fde_lab.tools.environment import GetServicesTool

def test_agent_initialization():
    agent = Agent(name="TestAgent", instructions="Test")
    assert agent.name == "TestAgent"
    assert agent.instructions == "Test"
    assert len(agent.tools) == 0

def test_agent_run_no_tools():
    agent = Agent(name="TestAgent", instructions="Test")
    response = agent.run("hello")
    assert "Try asking me about 'services'" in response

def test_agent_run_with_tools():
    tool = GetServicesTool()
    agent = Agent(name="TestAgent", instructions="Test", tools=[tool])
    
    response = agent.run("What services are running?")
    assert "postgres" in response
    assert "api-gateway" in response
    
    # Check memory recorded the interaction
    history = agent.memory.get_history()
    assert len(history) == 3 # user, tool, assistant
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "tool"
    assert history[1]["tool_name"] == "get_services"
    assert history[2]["role"] == "assistant"
