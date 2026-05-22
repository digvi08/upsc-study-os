"""AI Mentor service — conversational UPSC mentor."""
from typing import List, Optional, AsyncGenerator
import logging

from app.ai.openai_client import chat_completion, stream_chat_completion, UPSC_SYSTEM_PROMPT
from app.schemas.common import AIQueryRequest

logger = logging.getLogger(__name__)

MODE_INSTRUCTIONS = {
    "beginner": "Explain in simple language with analogies. Avoid jargon. Use examples from daily life.",
    "prelims": "Give concise, factual answers. Focus on MCQ-relevant facts, dates, and data points.",
    "mains": "Provide structured answer with Introduction, Body (with headings), and Conclusion. Include examples, data, and current affairs linkage.",
    "quick_revision": "Give only bullet points with key facts. Maximum 10 points. No elaboration.",
}


class MentorService:
    def build_messages(self, request: AIQueryRequest, history: Optional[List[dict]] = None) -> List[dict]:
        """Build the message list for the AI mentor."""
        mode_instruction = MODE_INSTRUCTIONS.get(request.mode, MODE_INSTRUCTIONS["mains"])

        system_content = f"{UPSC_SYSTEM_PROMPT}\n\nCurrent Mode: {request.mode.upper()}\n{mode_instruction}"

        if request.subject:
            system_content += f"\n\nContext Subject: {request.subject}"
        if request.topic:
            system_content += f"\nContext Topic: {request.topic}"

        messages = [{"role": "system", "content": system_content}]

        # Add conversation history
        if history:
            messages.extend(history[-10:])  # Last 10 messages for context

        messages.append({"role": "user", "content": request.query})
        return messages

    async def get_response(self, request: AIQueryRequest, history: Optional[List[dict]] = None) -> str:
        """Get a complete AI mentor response."""
        messages = self.build_messages(request, history)
        return await chat_completion(messages, temperature=0.7, max_tokens=2000)

    async def stream_response(
        self, request: AIQueryRequest, history: Optional[List[dict]] = None
    ) -> AsyncGenerator[str, None]:
        """Stream an AI mentor response."""
        messages = self.build_messages(request, history)
        async for chunk in stream_chat_completion(messages, temperature=0.7, max_tokens=2000):
            yield chunk

    async def generate_note_summary(self, content: str, topic: str) -> str:
        """Generate an AI summary of a note."""
        messages = [
            {"role": "system", "content": "You are a UPSC expert. Summarize the following content concisely for revision purposes. Use bullet points for key facts."},
            {"role": "user", "content": f"Topic: {topic}\n\nContent:\n{content}\n\nProvide a concise summary with key points for UPSC revision."},
        ]
        return await chat_completion(messages, temperature=0.5, max_tokens=800)

    async def generate_flashcards(self, content: str, topic: str, count: int = 10) -> List[dict]:
        """Generate flashcards from content."""
        messages = [
            {"role": "system", "content": "You are a UPSC expert. Generate flashcards in JSON format: [{\"front\": \"question\", \"back\": \"answer\"}]"},
            {"role": "user", "content": f"Topic: {topic}\n\nContent:\n{content}\n\nGenerate {count} flashcards covering key facts, dates, and concepts important for UPSC."},
        ]
        import json
        response = await chat_completion(messages, temperature=0.5, max_tokens=1500)
        try:
            # Extract JSON from response
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except Exception:
            pass
        return []

    async def analyze_pyq_with_ai(self, topic: str, questions: List[str]) -> str:
        """Generate AI insights for PYQ analysis."""
        questions_text = "\n".join([f"- {q}" for q in questions[:10]])
        messages = [
            {"role": "system", "content": UPSC_SYSTEM_PROMPT},
            {"role": "user", "content": f"""Analyze these UPSC PYQs on topic "{topic}":

{questions_text}

Provide:
1. Key themes and patterns
2. Important subtopics to focus on
3. Likely future question angles
4. Mains answer writing tips
5. Prelims MCQ strategy"""},
        ]
        return await chat_completion(messages, temperature=0.6, max_tokens=1500)

    async def generate_study_plan(
        self,
        subjects: List[str],
        weak_areas: List[str],
        available_hours: float,
        exam_date: str,
        completed_topics: List[str],
    ) -> dict:
        """Generate an AI-powered study plan."""
        messages = [
            {"role": "system", "content": "You are a UPSC study planner. Generate a detailed, realistic study plan in JSON format."},
            {"role": "user", "content": f"""Create a UPSC study plan with:
- Subjects: {', '.join(subjects)}
- Weak areas: {', '.join(weak_areas)}
- Daily available hours: {available_hours}
- Exam date: {exam_date}
- Already completed: {', '.join(completed_topics)}

Return JSON with: {{
  "daily_schedule": [{{"day": "Monday", "tasks": [{{"subject": "", "topic": "", "hours": 0, "type": "study/revision"}}]}}],
  "weekly_targets": [],
  "revision_schedule": [],
  "mock_test_schedule": [],
  "tips": []
}}"""},
        ]
        import json
        response = await chat_completion(messages, temperature=0.6, max_tokens=2000)
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except Exception:
            pass
        return {"raw_plan": response}

    async def evaluate_answer(self, question: str, answer: str, marks: int = 10) -> dict:
        """Evaluate a UPSC answer."""
        messages = [
            {"role": "system", "content": "You are a UPSC examiner. Evaluate answers strictly but fairly. Return JSON with scores and feedback."},
            {"role": "user", "content": f"""Evaluate this UPSC answer:

Question: {question}
Total Marks: {marks}

Answer:
{answer}

Return JSON: {{
  "total_marks": {marks},
  "obtained_marks": 0,
  "structure_score": 0,
  "content_score": 0,
  "keyword_score": 0,
  "analytical_score": 0,
  "grammar_score": 0,
  "examples_score": 0,
  "overall_feedback": "",
  "strengths": [],
  "improvements": [],
  "suggested_answer": "",
  "word_count": 0
}}"""},
        ]
        import json
        response = await chat_completion(messages, temperature=0.3, max_tokens=2000)
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except Exception:
            pass
        return {"raw_feedback": response}

    async def link_current_affairs(self, title: str, summary: str) -> dict:
        """Link current affairs to static UPSC subjects."""
        messages = [
            {"role": "system", "content": "You are a UPSC expert. Analyze current affairs and link them to static UPSC subjects. Return JSON."},
            {"role": "user", "content": f"""Analyze this current affair and link it to UPSC syllabus:

Title: {title}
Summary: {summary}

Return JSON: {{
  "related_subjects": [],
  "related_topics": [],
  "upsc_relevance_score": "High/Medium/Low",
  "prelims_relevant": true/false,
  "mains_relevant": true/false,
  "mains_angles": [],
  "ai_relevance_explanation": "",
  "keywords": []
}}"""},
        ]
        import json
        response = await chat_completion(messages, temperature=0.5, max_tokens=1000)
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except Exception:
            pass
        return {}
