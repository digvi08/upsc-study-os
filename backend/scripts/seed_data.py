"""Seed sample PYQ and current affairs data for development/production."""
import sys
from pathlib import Path
from dotenv import load_dotenv

_backend_root = Path(__file__).resolve().parents[1]
load_dotenv(_backend_root / ".env")
sys.path.insert(0, str(_backend_root))

from app.database.connection import SessionLocal, init_db
from app.models.pyq import PYQ, ExamType, QuestionType
from app.models.current_affairs import CurrentAffair
from datetime import date


SAMPLE_PYQS = [
    {
        "year": 2023,
        "exam": ExamType.PRELIMS,
        "subject": "Geography",
        "topic": "Monsoon",
        "question": "With reference to the Indian monsoon, consider the following statements...",
        "question_type": QuestionType.MCQ,
        "keywords": ["monsoon", "ITCZ", "El Nino"],
        "tags": ["climate", "geography"],
    },
    {
        "year": 2022,
        "exam": ExamType.PRELIMS,
        "subject": "Geography",
        "topic": "Monsoon",
        "question": "Which of the following factors influence the onset of the southwest monsoon in India?",
        "question_type": QuestionType.MCQ,
        "keywords": ["monsoon", "onset", "Kerala"],
        "tags": ["climate"],
    },
    {
        "year": 2021,
        "exam": ExamType.MAINS,
        "subject": "Geography",
        "topic": "Monsoon",
        "question": "Discuss the mechanism of the Indian monsoon and its impact on Indian agriculture.",
        "question_type": QuestionType.DESCRIPTIVE,
        "keywords": ["monsoon", "agriculture", "rainfall"],
        "tags": ["mains", "geography"],
    },
    {
        "year": 2020,
        "exam": ExamType.PRELIMS,
        "subject": "Polity",
        "topic": "Federalism",
        "question": "Which of the following best describes cooperative federalism in India?",
        "question_type": QuestionType.MCQ,
        "keywords": ["federalism", "cooperative federalism", "constitution"],
        "tags": ["polity"],
    },
    {
        "year": 2019,
        "exam": ExamType.MAINS,
        "subject": "Polity",
        "topic": "Federalism",
        "question": "Examine the challenges to cooperative federalism in contemporary India.",
        "question_type": QuestionType.DESCRIPTIVE,
        "keywords": ["federalism", "GST council", "centre-state"],
        "tags": ["mains", "polity"],
    },
    {
        "year": 2018,
        "exam": ExamType.PRELIMS,
        "subject": "Geography",
        "topic": "Landforms Made by Running Water",
        "question": "Which of the following landforms are associated with youthful stages of rivers?",
        "question_type": QuestionType.MCQ,
        "keywords": ["erosion", "river", "landforms", "v-shaped valley"],
        "tags": ["geomorphology"],
    },
    {
        "year": 2017,
        "exam": ExamType.PRELIMS,
        "subject": "Geography",
        "topic": "Landforms Made by Running Water",
        "question": "Meanders and oxbow lakes are typically formed in which stage of a river?",
        "question_type": QuestionType.MCQ,
        "keywords": ["meander", "oxbow", "mature stage"],
        "tags": ["geomorphology"],
    },
]

SAMPLE_AFFAIRS = [
    {
        "title": "Inter-State River Water Disputes",
        "summary": "Recent developments in Cauvery and Krishna water sharing between states.",
        "source": "The Hindu",
        "published_date": date(2024, 3, 15),
        "tags": ["polity", "geography"],
        "keywords": ["river dispute", "federalism", "water"],
        "related_subjects": ["Geography", "Polity"],
        "upsc_relevance_score": "High",
        "prelims_relevant": True,
        "mains_relevant": True,
    },
    {
        "title": "India's Climate Commitments at COP",
        "summary": "India's updated NDC targets and renewable energy push discussed at global climate summit.",
        "source": "PIB",
        "published_date": date(2024, 1, 10),
        "tags": ["environment", "IR"],
        "keywords": ["climate change", "NDC", "renewable"],
        "related_subjects": ["Environment", "International Relations"],
        "upsc_relevance_score": "High",
        "prelims_relevant": True,
        "mains_relevant": True,
    },
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        existing_pyq = db.query(PYQ).filter(PYQ.is_deleted == False).count()
        if existing_pyq == 0:
            for item in SAMPLE_PYQS:
                db.add(PYQ(**item))
            print(f"Seeded {len(SAMPLE_PYQS)} PYQs")
        else:
            print(f"PYQs already exist ({existing_pyq}), skipping")

        existing_ca = db.query(CurrentAffair).filter(CurrentAffair.is_deleted == False).count()
        if existing_ca == 0:
            for item in SAMPLE_AFFAIRS:
                db.add(CurrentAffair(**item))
            print(f"Seeded {len(SAMPLE_AFFAIRS)} current affairs")
        else:
            print(f"Current affairs already exist ({existing_ca}), skipping")

        db.commit()
        print("Seed complete.")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
