import os
import json
from dotenv import load_dotenv
from textwrap import dedent

import tweepy
import re
from groq import Groq
from crewai import Crew
from crewai.process import Process
from tasks import ViralContentCreationTasks
from agents import ViralContentCreators

# Load environment variables from a .env file
load_dotenv()

# Define necessary constants from environment variables
MODEL = os.getenv('MODEL')
if not MODEL:
    raise ValueError("MODEL environment variable is not set.")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET_KEY = os.getenv('TWITTER_API_SECRET_KEY')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('TWITTER_BEARE_TOKEN')

# Ensure all necessary environment variables are set
if not all([GROQ_API_KEY, TWITTER_API_KEY, TWITTER_API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN]):
    raise ValueError("One or more Twitter API keys/secrets are not set.")

# Initialize Groq client for generating tweets
groqClient = Groq(api_key=GROQ_API_KEY)

# Function to extract tweets from content using a language model
def get_tweets_from_llm(content):
    chat_completion = groqClient.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": dedent("""\
                    You are a helpful assistant that receives some text from the user.
                    The text contains a couple of twitter tweets.
                    You extract all the tweets from the text and create an array of tweets and return
                    the array without any additional info, explanation, instructions or metadata.
                """)
            },
            {
                "role": "user",
                "content": dedent(f"""\
                    Generate an array of tweets based on the content below.
                    Return only the array of tweets in the format: ["tweet_1", "tweet_2", ...], where tweet_1 is the
                    first tweet, tweet_2 is the second tweet and so on, without any explanation or
                    metadata. Let's call your response to this query as tweets_array. Then this
                    python code should work fine on my end: "tweets_list = json.loads(tweets_array)"
                    Content: {content}
                """)
            }
        ],
        model=MODEL,
    )

    # Extract the JSON array from the response
    response_text = chat_completion.choices[0].message.content
    match = re.search(r'\[(.*?)\]', response_text, re.DOTALL)

    if match:
        tweets_array = '[' + match.group(1) + ']'
        try:
            print("tweets_array: ")
            print(tweets_array)
            tweets_list = json.loads(tweets_array)
            return tweets_list
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            return []
    else:
        print("No valid JSON array found in the response.")
        return []

# Function to post a tweet using the Twitter API
def process_tweet(tweet):
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET_KEY,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    tweet_params = {"text": tweet}

    try:
        response = client.create_tweet(**tweet_params)
        print("Tweet posted successfully!", response.data)
        return response
    except Exception as e:
        print("Error during tweeting:", e)
        return e

# Initialize the agents for creating viral content
tasks = ViralContentCreationTasks()
agents = ViralContentCreators()
trending_topic_researcher_agent = agents.trending_topic_researcher_agent()
content_researcher_agent = agents.content_researcher_agent()
creative_agent = agents.creative_content_creator_agent()

# Create tasks for the agents
niche = "Llama LLM models"
topic_analysis = tasks.topic_analysis(trending_topic_researcher_agent, niche)
content_research = tasks.content_research(content_researcher_agent, niche)
twitter_posts = tasks.create_twitter_posts(creative_agent, niche)

# Create a Crew to manage the agents and tasks
crew = Crew(
    agents=[
        trending_topic_researcher_agent,
        content_researcher_agent,
        creative_agent
    ],
    tasks=[
        topic_analysis,
        content_research,
        twitter_posts
    ],
    process=Process.sequential,
    verbose=True,
    max_rpm=3
)

# Kick off the process and get the result
result = crew.kickoff()
print("Crew usage", crew.usage_metrics)

# Print the result of the process
print("\n\n########################")
print("## Here is the result")
print("########################\n")
print(result)

# Extract tweets from the result using the LLM
tweets = get_tweets_from_llm(result)
print("tweets: ")
print(tweets)

# Process each tweet to post on Twitter
for tweet in tweets:
    print(tweet)
    process_tweet(tweet)
