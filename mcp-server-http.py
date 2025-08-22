from mcp.server.fastmcp import FastMCP
import requests
from tavily import TavilyClient
from dotenv import load_dotenv
import os
from typing import List, Dict
from pydantic import BaseModel, Field

from models import WeatherAPIError, WeatherData


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
    
@mcp.tool()
def get_weather_weatherapi(city: str) -> WeatherData:
    """
    Récupère la météo via WeatherAPI pour une ville donnée.
    Aligne l'appel sur:
      GET https://api.weatherapi.com/v1/current.json?key=...&q=...&aqi=no&lang=fr
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise WeatherAPIError("Variable d’environnement WEATHER_API_KEY manquante.")

    url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city,
        "aqi": "no",
        "lang": "fr",
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
    except requests.RequestException as e:
        raise WeatherAPIError(f"Erreur réseau lors de l'appel WeatherAPI: {e}") from e

    # Gestion fine des statuts communs
    if resp.status_code == 400:
        # WeatherAPI renvoie souvent un JSON d'erreur { "error": { "message": "...", "code": ... } }
        try:
            err_msg = resp.json().get("error", {}).get("message", "Requête invalide (400).")
        except Exception:
            err_msg = "Requête invalide (400)."
        raise WeatherAPIError(err_msg)

    if resp.status_code == 401:
        raise WeatherAPIError("Clé API invalide (401).")

    if not resp.ok:
        # Inclut le message d'erreur retourné par l'API si disponible
        try:
            err_obj = resp.json().get("error", {})
            err_msg = err_obj.get("message") or resp.text
        except Exception:
            err_msg = resp.text
        raise WeatherAPIError(f"Erreur API {resp.status_code}: {err_msg}")

    payload = resp.json()
    current = payload.get("current") or {}
    condition_obj = current.get("condition") or {}

    # Conversions sécurisées avec valeurs par défaut
    def to_float(value, default=None):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    temp_c = to_float(current.get("temp_c"))
    humidity = to_float(current.get("humidity"))
    wind_kph = to_float(current.get("wind_kph"), 0.0)

    # Vérifications minimales si des champs essentiels manquent
    if temp_c is None or humidity is None:
        raise WeatherAPIError("Réponse invalide: champs 'temp_c' ou 'humidity' manquants.")

    condition_text = str(condition_obj.get("text", "N/A"))

    return WeatherData(
        temperature=temp_c,
        humidity=humidity,
        condition=condition_text,
        wind_speed=wind_kph / 3.6,  # conversion kph -> m/s
    )



if __name__ == "__main__":
    mcp.run(transport="sse")