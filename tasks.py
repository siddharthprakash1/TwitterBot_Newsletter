from crewai import Task
from textwrap import dedent

class ViralContentCreationTasks:
    def topic_analysis(self, agent, niche):
        return Task(
            description=dedent(f"""\
                Find new articles, GitHub repositories, and YouTube tutorials related to the niche: {niche}, 
                released or published in the past 1 month.
                
                Compile this information into a structured list of content items. 
                Each item should include a very very brief description (1-2 lines max) and relevance score 
                to guide content sharing efforts around these new resources and also inlucde the link of the resource. 
                Ensure the final list is clear, actionable, and ready to inform strategic 
                content curation.
                Also remember there is limit on tokens per minute cannot be more than 6000 tokens per minute.
                """),
            expected_output="List of new content items in the format: [item1, item2, ...]",
            agent=agent
        )

    def content_research(self, agent, niche):
        return Task(
            description=dedent(f"""\
                Do a very brief research on all the new content items (articles, repos, tutorials).
                For each item related to {niche}, gather:
                    - A one-sentence summary of the item's significance.
                    - The source link (article URL, GitHub repo link, or YouTube video link) this is mandatory.
                    - One key takeaway or interesting fact from the content.
                    
                Compile these details for each item, keeping in mind the 250-character limit for tweets.
                Also remember there is limit on tokens per minute cannot be more than 6000 tokens per minute.
                Maximum number of google searches you can do is 10.
                The source link (article URL, GitHub repo link, or YouTube video link)  is mandatory.
                """),
            expected_output=dedent(f"""\
                        A map of content items to structured research details for that item.
                        This report will serve as a foundation 
                        for creating targeted, informed, and engaging twitter posts"""),
            agent=agent
        )

    def create_twitter_posts(self, agent, niche):
        return Task(
            description=dedent(f"""\
                Create 5 Twitter posts related to {niche} using the content research done for each of 
                the new articles, GitHub repos, or YouTube tutorials. Craft engaging, valuable, and concise 
                Twitter posts that are ready to be published. Use the following structure:
                    1. Start with a brief intro about the new content (1 line max).
                    2. Include one key takeaway or interesting fact (1 line max).
                    3. Add the source link.
                    4. Use 1-2 relevant hashtags.

                Example Post:
                "New #CrewAI tutorial on YouTube! Learn how to build complex AI workflows in minutes.
                Key takeaway: CrewAI simplifies multi-agent systems.
                Watch here: [YouTube link]
                #AITutorial"

                Note: Ensure each post is standalone and provides necessary context within the 250-character limit. 
                Compile these posts into a list, with each entry clearly labeled with the content item it addresses.
                
                After executing this task, you should print the output.
                Task should return an array containing all the 5 twitter posts"""),
            expected_output="Array containing all the twitter posts in the format: [post_1, post_2, ...]",
            agent=agent
        )

    def publish_twitter_posts(self, agent, tweets):
         return Task(
             description=dedent("""\
                 Print all the tweets created by previous task in the logs.
                 Publish all the tweets to Twitter.
                 """),
             expected_output="Posting status of all the tweets.",
             agent=agent
         )