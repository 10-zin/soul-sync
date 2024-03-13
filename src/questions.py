from sqlalchemy.orm import Session
from . import models  # Adjust the import path based on your project structure

# Define your questions along with their frequency
# TODO: The frequency_days is currently not being checked ....
QUESTIONS = [
    # Monthly questions
    {"content": "Tell me about a hobby you're passionate about. How did you get into it, and what do you love most about it?", "frequency_days": 30},
    {"content": "What's a dream you're working towards? How can someone you're dating support or share in that dream?", "frequency_days": 30},
    {"content": "What values are most important to you in a relationship? How do you think those values guide your interactions with others?", "frequency_days": 30},
    {"content": "How do you like to spend your free time? Are you more of a 'stay at home and relax' person, or do you prefer going out and exploring?", "frequency_days": 30},
    # Daily questions
    {"content": "What was a highlight of your day today, and what made it stand out for you?", "frequency_days": 1},
    {"content": "What's one thing you're grateful for today, and why? How does expressing gratitude affect your day?", "frequency_days": 1},
    {"content": "Faced any challenges today? How did you tackle them, and what did you learn from the experience?", "frequency_days": 1},
    {"content": "What's something you're looking forward to tomorrow or later this week? How are you preparing for it?", "frequency_days": 1},
]

def populate_questions(db: Session):
    for question_info in QUESTIONS:
        # Check if the question already exists
        exists = db.query(models.Question).filter(models.Question.content == question_info["content"]).first()
        if not exists:
            # Create a new Question object and add it to the session
            new_question = models.Question(
                content=question_info["content"],
                frequency_days=question_info["frequency_days"]
            )
            db.add(new_question)
    # Commit the session to save all new questions to the database
    db.commit()

# Example usage (adjust according to how you manage your DB session)
# from your_database_session_manager import SessionLocal
# db = SessionLocal()
# populate_questions(db)
