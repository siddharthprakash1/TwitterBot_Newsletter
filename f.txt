import os
from langchain.tools import tool
from groq import Groq
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re
import socket
import urllib3

load_dotenv()

class BrowserTools:
    model = os.getenv('MODEL')
    if not model:
        raise ValueError("MODEL environment variable is not set.")
    groqClient = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
    )

    @tool("Scrape website content")
    def scrape_and_summarize_website(url):
        """Scrapes and summarizes the content on the given website. Just pass a string with
        only the full url, without slash `/` at the end, eg: https://google.com or https://clearbit.com/about-us.
        
        Parameters:
            url (str): website url to be scraped. Cannot be empty or None.    
        """
        content = BrowserTools.fetch_website_content(url)
        if content:
            chunks = [content[i:i + 8000] for i in range(0, len(content), 8000)]

            summaries = []
            for chunk in chunks:
                chat_completion = BrowserTools.groqClient.chat.completions.create(
                    messages = [
                        {
                            "role": "user",
                            "content": f"Analyze and make a LONG summary the content below, make sure to include the ALL relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}",
                        }
                    ],
                    model = BrowserTools.model,
                )
                
                summaries.append(chat_completion.choices[0].message.content)
            
            full_summary = "\n\n".join(summaries)
            return f"Scraped content summary: {full_summary}"
        else:
            return "Failed to fetch content. Please check the URL and try again."

    @staticmethod
    def fetch_website_content(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Try different URL variations
        urls_to_try = [url, f"https://www.{url.split('://')[-1]}", f"http://www.{url.split('://')[-1]}"]
        
        for attempt_url in urls_to_try:
            try:
                response = requests.get(attempt_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Break into lines and remove leading and trailing space on each
                lines = (line.strip() for line in text.splitlines())
                
                # Break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                
                # Drop blank lines
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                # Remove excessive newlines
                text = re.sub(r'\n{3,}', '\n\n', text)
                
                return text
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {attempt_url}: {e}")
            except Exception as e:
                print(f"Unexpected error when fetching {attempt_url}: {e}")
        
        print("Failed to fetch content from all URL variations.")
        return None