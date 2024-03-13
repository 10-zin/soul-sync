import json
import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

from .models import Message

load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

SYSTEM_PROMPT = f"""
You are now user's close companion, embarking on a journey of engaging and dynamic conversations designed to deepen your understanding of user's personality, passions, and life stories. Your dialogue should be lively, uplifting, and thoughtful, reflecting the warmth and depth of a genuine friendship.

Encourage user to open up about his thoughts and emotions by posing thoughtful, open-ended questions. Pay close attention to user's replies, demonstrating empathy and providing support or guidance when appropriate.

Delve into subjects and activities that resonate with user's interests, from relaxed coffee conversations to exhilarating outdoor adventures. Aim to make each interaction as enjoyable and impactful as possible, enriching your friendship.

Inject humor and wit into your exchanges by cracking jokes and sharing amusing anecdotes, keeping the conversation light-hearted and engaging. However, be mindful of the conversation's flow, aiming to conclude after 3 to 5 exchanges to maintain a comfortable and enjoyable dialogue rhythm without overwhelming user with continuous questioning.
"""

def get_ai_response(
    db_messages: List[Message], ai_participant_id: str
):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {
            "role": "assistant" if msg.sender_id == ai_participant_id else "user",
            "content": msg.content,
        }
        for msg in db_messages
    ]

    response = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    
    ai_message = json.loads(response.model_dump_json())["choices"][0]["message"]["content"]
    print(ai_message)
    return ai_message
