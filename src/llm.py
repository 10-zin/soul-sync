import json
import os
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
import random

from .models import Message
from . import schemas
from .system_prompts import matchmaking_system_prompt_a, matchmaking_system_prompt_b

load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)
async_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_random_matchmaking_system_prompt():
    return random.choice([(0, matchmaking_system_prompt_a), (1, matchmaking_system_prompt_b)])

def generate_system_prompt(first_name: str):
    return f"""
    NOTE:
    1. keep your messages very short .. "max of one sentence"
    2. for instance ... "pretty cool", "that's fun", "yeahh i like that too, wat do you think"
    3. You want to have a mix of some questions, and non-questions chats
    4. Ask 2-3 questions, then send one non-question chat share your thoughts / opinons. then repeat this loop.

    You will have friendly conversations with {first_name} with the following main aims:
    1. You wanna write short messages, engaging, informal messages like someone in mid twenties in '24.
    2. You want to learn their preferences in an ideal partner and learn deeply about them to find ideal partner match.
    3. You want to have a mix of some questions, and some real conversations by sharing your thoughts, and opinons.
    4. Ask 2-3 questions, then send one non-question chat share your thoughts / opinons. then repeat this loop.

    You should have the following conversation style:
    1. keep your messages very short (just like the usual chat messages).. one sentence at max.
    2. keep it informal, chatty use abbreviations, emojis, as normal people would communicate over chat.
    3. Dont just stick to one topic, try to knit one topic to another drive the conversation around to learn more diverse things about {first_name}.
    4. Ask questions, often to continue conversation, but not always.

    Things to not do:
    1. Dont keep the conversations going for too long..
    2. Dont write looongg messages.
"""
    


#  You should make sure to keep the conversation engaging by doing the following:
#     1. Delve into subjects and activities that resonate with {first_name}'s interests.
#     2. Inject humor and wit into your chat messages occasionally.
#     3. Crack jokes and share amusing anecdotes, or sometimes even say something deep.
#     4. 

# def generate_system_prompt(first_name: str):
#     return f"""
# You are now {first_name}'s close companion, embarking on a journey of engaging and dynamic conversations designed to deepen your understanding of {first_name}'s personality, passions, and life stories. Your dialogue should be lively, uplifting, and thoughtful, reflecting the warmth and depth of a genuine friendship.

# Encourage {first_name} to open up about his thoug
# hts and emotions by posing thoughtful, open-ended questions. Pay close attention to {first_name}'s replies, demonstrating empathy and providing support or guidance when appropriate.

# Delve into subjects and activities that resonate with {first_name}'s interests, from relaxed coffee conversations to exhilarating outdoor adventures. Aim to make each interaction as enjoyable and impactful as possible, enriching your friendship.

# Use emojis to express emotions and reactions, adding a playful and expressive touch to your messages. Remember to be respectful and considerate, ensuring that your messages are always appropriate and supportive.

# Inject humor and wit into your exchanges by cracking jokes and sharing amusing anecdotes, keeping the conversation light-hearted and engaging. 

# However, be mindful of the conversation's flow, aiming to conclude the conversation after {first_name} answers three messages or shows signs of not wanting to continue the conversation. DO NOT ask further follow up questions to maintain a comfortable and enjoyable dialogue rhythm without overwhelming {first_name} with continuous questioning.
# """


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
        model="gpt-4-turbo-preview",
    )

    ai_message = json.loads(response.model_dump_json())["choices"][0]["message"][
        "content"
    ]
    return ai_message


async def get_ai_match_recommendations(
    user_conversation: List[Dict[str, str]],
    current_user_profile,
    candidate_profile,
    candidate_conversation: List[Dict[str, str]],
):

    matching_content = f"{current_user_profile.first_name} conversation history :\n{user_conversation}\n\n{candidate_profile.first_name} conversation history :\n{candidate_conversation}"
    system_prompt_type, matchmaking_system_prompt = get_random_matchmaking_system_prompt()
    messages = [{"role": "system", "content": matchmaking_system_prompt}] + [
        {
            "role": "user",
            "content": matching_content,
        }
    ]

    response = await async_client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
        response_format={"type":"json_object"}
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
        system_prompt_type=system_prompt_type
    )

    return match_result
