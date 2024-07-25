from langchain.tools import tool
import http.client
import json
import os
import urllib.parse

class TrendsTools:
    @tool("GoogleTrendsTool")
    def trending_searches_on_google(input_data: str = ""):
        """A tool to fetch trending Google searches in a given niche."""
        try:
            # Parse input: it can be either a string (niche) or a JSON string (dict)
            if input_data.startswith('{') and input_data.endswith('}'):
                input_dict = json.loads(input_data)
                niche = input_dict.get("input_data", "")  # Changed from "niche" to "input_data"
            else:
                niche = input_data

            # Sanitize the niche input
            niche = urllib.parse.quote(niche.strip())

            conn = http.client.HTTPSConnection("google-trends8.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': os.environ.get('RAPIDAPI_KEY'),
                'x-rapidapi-host': "google-trends8.p.rapidapi.com"
            }
            
            endpoint = f"/trendings?region_code=US&hl=en-US"
            if niche:
                endpoint += f"&niche={niche}"
            
            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()
            
            if not data:
                return {"status": "error", "message": "No data received from the API"}
            
            trends = json.loads(data.decode("utf-8"))
            
            if 'trendingSearches' in trends:
                return {"status": "success", "trends": trends['trendingSearches']}
            else:
                return {"status": "no_trends", "message": "No trending searches found."}
        except json.JSONDecodeError:
            return {"status": "error", "message": "Failed to parse input or API response"}
        except http.client.HTTPException as e:
            return {"status": "error", "message": f"HTTP error occurred: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}
        finally:
            if 'conn' in locals():
                conn.close()