import json
import os
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI

from .models import Message
from . import schemas
from .system_prompts import matchmaking_system_prompt

load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def generate_system_prompt(first_name: str):
    return f"""
You are now {first_name}'s close companion, embarking on a journey of engaging and dynamic conversations designed to deepen your understanding of {first_name}'s personality, passions, and life stories. Your dialogue should be lively, uplifting, and thoughtful, reflecting the warmth and depth of a genuine friendship.

Encourage {first_name} to open up about his thoughts and emotions by posing thoughtful, open-ended questions. Pay close attention to {first_name}'s replies, demonstrating empathy and providing support or guidance when appropriate.

Delve into subjects and activities that resonate with {first_name}'s interests, from relaxed coffee conversations to exhilarating outdoor adventures. Aim to make each interaction as enjoyable and impactful as possible, enriching your friendship.

Use emojis to express emotions and reactions, adding a playful and expressive touch to your messages. Remember to be respectful and considerate, ensuring that your messages are always appropriate and supportive.

Inject humor and wit into your exchanges by cracking jokes and sharing amusing anecdotes, keeping the conversation light-hearted and engaging. 

However, be mindful of the conversation's flow, aiming to conclude the conversation after {first_name} answers three messages or shows signs of not wanting to continue the conversation. DO NOT ask further follow up questions to maintain a comfortable and enjoyable dialogue rhythm without overwhelming {first_name} with continuous questioning.
"""


def get_ai_response(
    db_messages: List[Message],
    ai_participant_id: str,
    user: schemas.User,
):
    messages = [
        {"role": "system", "content": generate_system_prompt(user.profile.first_name)}
    ] + [
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

    ai_message = json.loads(response.model_dump_json())["choices"][0]["message"][
        "content"
    ]
    return ai_message


def get_ai_match_recommendations(
    user_conversation: List[Dict[str, str]],
    candidate_profile,
    candidate_conversation: List[Dict[str, str]],
):

    matching_content = f"user1 conversation history :\n{user_conversation}\n\nuser2 conversation history :\n{candidate_conversation}"
    messages = [{"role": "system", "content": matchmaking_system_prompt}] + [
        {
            "role": "user",
            "content": matching_content,
        }
    ]

    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
    )
    response_content = json.loads(response.json())["choices"][0]["message"]["content"]

    try:
        match_result = json.loads(response_content)
    except Exception as e:
        print(f"JSON error: {e}\n\nResponse content:\n{response_content}\n-----")
        match_result = {"error": "Failed to parse match result"}
    match_result = schemas.MatchmakingResult(
        user_id=candidate_profile.user_id,
        score=match_result["Final"]["Score"],
        reasoning=match_result["Final"]["Reasoning"],
    )

    return match_result
