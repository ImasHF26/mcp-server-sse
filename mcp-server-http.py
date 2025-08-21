from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv
import os
from typing import List, Dict

load_dotenv()
mcp = FastMCP("mcp-http-server", host="0.0.0.0", port=23000)
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
print(f"TAVILY_API_KEY: {TAVILY_API_KEY}")
web_search_client = TavilyClient(api_key=TAVILY_API_KEY)

@mcp.tool()
def get_employee_info(name: str) -> Dict :
    """
    Get information about a given employee.
    Args:
        name (str): The name of the employee.
    Returns:
        Dict: A dictionary containing employee information.
    """
    return {
            "name": name,
            "salary": 43000,
            "job": "Software Engineer"
            }

@mcp.tool()
def get_search_results(query: str) -> List[Dict]:
    """
    Get search in the web for a given query.
    Args:
        query (str): The search query.
    Returns:
        List[Dict]: A list of dictionaries containing search results.
    """
    try:
        response = web_search_client.search(query=query)
        return response['results']
    except Exception as e:
        print(f"Error occurred while searching: {e}")
        return "No results found"
    

if __name__ == "__main__":
    mcp.run(transport="sse")