from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src import models, schemas
from src.utils import get_database_connection_string
from sqlalchemy.orm import Session
from src.models import MatchMakingResult, MatchMakingUserRating
print(get_database_connection_string())
# exit()
engine = create_engine(
    get_database_connection_string()
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
db = SessionLocal()
models.Base.metadata.create_all(bind=engine)

from sqlalchemy.orm import Session
from src.models import MatchMakingResult, MatchMakingUserRating, MatchMakingCounter

def get_detailed_matchmaking_info(user_id: str, db: Session):
    latest_counter = db.query(MatchMakingCounter.counter).filter(
        MatchMakingCounter.user_id == user_id
    ).scalar()

    if latest_counter is None:
        return None  # No counter value found

    results = db.query(
        MatchMakingResult.user_id,
        MatchMakingResult.candidate_user_id,
        MatchMakingResult.system_prompt_type,
        MatchMakingUserRating.score
    ).join(
        MatchMakingUserRating,
        (MatchMakingUserRating.user_id == MatchMakingResult.user_id) &
        (MatchMakingUserRating.candidate_user_id == MatchMakingResult.candidate_user_id) &
        (MatchMakingUserRating.counter == MatchMakingResult.counter)
    ).filter(
        MatchMakingResult.user_id == user_id,
        MatchMakingResult.counter == latest_counter
    ).all()

    detailed_results = [{
        "user_id": result.user_id,
        "candidate_user_id": result.candidate_user_id,
        "system_prompt_type": result.system_prompt_type,
        "score": result.score
    } for result in results]

    return detailed_results

tested_user_ids=["dbe8ec77-1843-4b95-bd12-6e35576d2a60", "f0901dc2-da1b-415a-8c7e-7d2f0966c5bf", "8758d995-cecb-49b5-b4d0-fd4e0f9acc83", "e22fdeef-c6bc-4def-9897-926e14767791", "c21db503-7da9-4279-aa64-5368b98006f4", "76a02501-808c-4fd4-b10d-adf614414d39",]
final_results=[]
prompt_scores = {"0":[], "1":[]}
for user_id in tested_user_ids:
    op = get_detailed_matchmaking_info(user_id=user_id,db=db)
    if not op:
        print(user_id)
    print(op)
    print('\n\n')
    for profile in op:
        prompt_scores[profile["system_prompt_type"]].append(profile["score"])
    final_results.append(op)
print(final_results)
print(len(prompt_scores["0"]), sum(prompt_scores["0"])/len(prompt_scores["0"]))
print(len(prompt_scores["1"]), sum(prompt_scores["1"])/len(prompt_scores["1"]))


