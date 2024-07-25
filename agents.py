import os
from textwrap import dedent
from crewai import Agent
from tools.browser_tools import BrowserTools
from tools.search_tools import SearchTools
from tools.trends_tools import TrendsTools
from chat_groq_manager import ChatGroqManager

from dotenv import load_dotenv
load_dotenv()

class ViralContentCreators:
    def __init__(self):
        model = os.getenv('MODEL')
        if not model:
            raise ValueError()
        chat_groq_manager = ChatGroqManager(model)
        self.llm = chat_groq_manager.create_llm()

    def trending_topic_researcher_agent(self):
        return Agent(
            role="Content Discovery Specialist",
            goal=dedent("""\
                Identify and compile a list of new articles, GitHub repositories, and YouTube tutorials
                related to GenAI, CrewAI, and Langchain. This list should provide actionable insights
                and opportunities for sharing valuable content within the AI community."""),
            backstory=dedent("""\
                As a Content Discovery Specialist at a cutting-edge AI research firm,
                your primary responsibility is to monitor and curate the latest developments
                in GenAI, CrewAI, and Langchain. Using advanced search techniques, you uncover
                and list the most relevant new resources that can inform and educate the AI community."""),
            tools=[
                    BrowserTools.scrape_and_summarize_website,
                    TrendsTools.trending_searches_on_google,
                    SearchTools.search_internet
            ],
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )

    def content_researcher_agent(self):
        return Agent(
            role="AI Content Analyst",
            goal=dedent("""\
                Conduct brief research on newly discovered articles, GitHub repos, and YouTube tutorials
                related to GenAI, CrewAI, and Langchain. Compile concise, useful information and key takeaways
                for each item. This information should be actionable and suitable for creating engaging
                and informative tweets."""),
            backstory=dedent("""\
                As an AI Content Analyst at a dynamic tech news platform, you quickly assess and
                extract the most important information from new AI resources. Your ability to distill
                complex AI concepts into brief, engaging snippets ensures the content you help create
                resonates with both AI enthusiasts and professionals."""),
            tools=[
                BrowserTools.scrape_and_summarize_website,
                SearchTools.search_internet,
            ],
            llm=self.llm,
            verbose=True
        )

    def creative_content_creator_agent(self):
        return Agent(
            role="AI Tweet Composer",
            goal=dedent("""\
                Develop compelling and concise tweet copies about new articles, GitHub repos,
                and YouTube tutorials related to GenAI, CrewAI, and Langchain. Ensure each tweet
                provides value within the 250-character limit."""),
            backstory=dedent("""\
                As an AI Tweet Composer at a top-tier tech media company, you excel in crafting
                concise yet informative tweets about the latest AI developments. Your expertise
                lies in distilling complex AI topics into engaging, bite-sized content that
                captures attention and encourages further exploration."""),
            tools=[
                BrowserTools.scrape_and_summarize_website,
                SearchTools.search_internet
            ],
            llm=self.llm,
            verbose=True
        )