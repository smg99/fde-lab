from fde_lab.tools.environment import GetServicesTool

def test_get_services_tool():
    tool = GetServicesTool()
    assert tool.name == "get_services"
    assert "running services" in tool.description.lower()
    
    result = tool.execute()
    assert result["status"] == "success"
    assert len(result["services"]) > 0
    
    postgres_service = next(s for s in result["services"] if s["name"] == "postgres")
    assert postgres_service["status"] == "running"
    assert postgres_service["port"] == 5432
