import re
import logging
from typing import Dict, Any, List, Optional, Tuple
import httpx
from sqlalchemy.orm import Session
from app.config import get_settings
from app import crud

logger = logging.getLogger(__name__)
settings = get_settings()


class EduSphereAIService:
    """
    Intelligent AI service that grounds natural-language answers in actual SQLite records.
    Communicates with local Ollama if available, or gracefully falls back to deterministic
    grounded record analysis with clear setup instructions.
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    async def check_ollama_status(self) -> Tuple[bool, List[str], Optional[str]]:
        """
        Check if Ollama service is reachable and retrieve installed models.
        Returns (is_available, model_names, error_message).
        """
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    return True, models, None
                return False, [], f"Ollama returned HTTP status {res.status_code}"
        except httpx.ConnectError:
            return False, [], "Could not connect to Ollama server at 127.0.0.1:11434. Service is not running."
        except Exception as e:
            return False, [], f"Connection error: {str(e)}"

    def extract_intent_and_ground_data(self, query: str, db: Session) -> Tuple[str, Dict[str, Any], str]:
        """
        Controlled retrieval based on user query intent.
        Ensures NO raw/unrestricted SQL is ever run.
        Returns (intent_type, grounded_data, human_readable_summary).
        """
        q = query.lower().strip()

        # 1. Check for count / total questions
        if any(w in q for w in ["how many", "total student", "count of", "number of student", "registered student"]):
            count_data = crud.ai_query_total_students(db)
            total = count_data["total_students"]
            summary = f"There are currently **{total}** students registered in the EduSphere system."
            return "count", count_data, summary

        # 2. Check for distribution / course summary
        if any(w in q for w in ["distribution", "summary", "breakdown", "by course", "how many per course"]):
            dist = crud.ai_query_course_distribution(db)
            lines = [f"- **{d['course']}**: {d['count']} students ({d['percentage']}%)" for d in dist]
            summary = "### Student Distribution by Course:\n" + ("\n".join(lines) if lines else "No student records found.")
            return "distribution", {"distribution": dist}, summary

        # 3. Check for birth year questions (e.g., "born after 2005", "born before 2000", "born in 2004")
        year_match = re.search(r"\b(19\d{2}|20\d{2})\b", q)
        if "born" in q or "dob" in q or "birth" in q:
            if year_match:
                year = int(year_match.group(1))
                comparison = "after"
                if "before" in q or "prior" in q or "earlier" in q:
                    comparison = "before"
                elif "in" in q or "during" in q or "exact" in q:
                    comparison = "in"

                students = crud.ai_query_by_birth_year(db, year, comparison)
                if comparison == "after":
                    header = f"Students born after {year} ({len(students)} found):"
                elif comparison == "before":
                    header = f"Students born before {year} ({len(students)} found):"
                else:
                    header = f"Students born in {year} ({len(students)} found):"

                items = [f"- **{s['full_name']}** (ID: `{s['student_id']}`, DOB: {s['date_of_birth']}, Course: {s.get('course') or 'N/A'})" for s in students]
                summary = f"### {header}\n" + ("\n".join(items) if items else "No matching students found.")
                return "birth_year", {"year": year, "comparison": comparison, "students": students}, summary

        # 4. Check for email or phone search
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", query)
        phone_match = re.search(r"(\+?[0-9]{1,4}[\s-]?)?[0-9]{5,10}", query)
        if email_match or "email" in q or (phone_match and ("phone" in q or "contact" in q)):
            search_term = email_match.group(0) if email_match else (phone_match.group(0) if phone_match else "")
            if not search_term and "email" in q:
                # Try finding words after 'email'
                parts = q.split("email")
                if len(parts) > 1:
                    search_term = parts[1].replace("address", "").replace("is", "").strip()

            students = crud.ai_query_by_contact(db, search_term) if search_term else []
            items = [f"- **{s['full_name']}** (ID: `{s['student_id']}`, Email: `{s.get('email')}`, Phone: `{s.get('phone')}`)" for s in students]
            summary = f"### Contact Search Results for '{search_term}':\n" + ("\n".join(items) if items else "No students found with that contact info.")
            return "contact_search", {"term": search_term, "students": students}, summary

        # 5. Check for course lookup
        all_courses = crud.get_all_courses(db)
        matched_course = None
        for course in all_courses:
            if course.lower() in q:
                matched_course = course
                break

        # Also check common shorthand/synonyms
        if not matched_course:
            if "cs" in q or "computer science" in q:
                matched_course = "Computer Science"
            elif "ai" in q or "artificial intelligence" in q:
                matched_course = "Artificial Intelligence"
            elif "data science" in q or "ds" in q:
                matched_course = "Data Science"

        if matched_course or "course" in q or "enrolled in" in q:
            search_course = matched_course or q.replace("show students enrolled in", "").replace("who is in", "").strip()
            students = crud.ai_query_by_course(db, search_course)
            items = [f"- **{s['full_name']}** (ID: `{s['student_id']}`, DOB: {s['date_of_birth']}, Email: {s.get('email') or 'N/A'})" for s in students]
            summary = f"### Students enrolled in {search_course} ({len(students)} found):\n" + ("\n".join(items) if items else f"No students currently enrolled in '{search_course}'.")
            return "course_students", {"course": search_course, "students": students}, summary

        # 6. Specific student ID or name search (e.g., "who is STU-2025-001" or "details of Aarav")
        id_match = re.search(r"\b[A-Za-z0-9\-_]{3,20}\b", query)
        for token in query.split():
            clean_token = token.strip("?,.!'\"")
            s = crud.get_student_by_student_id(db, clean_token)
            if s:
                details = s.to_dict()
                summary = (
                    f"### Student Record: {s.full_name}\n"
                    f"- **Student ID:** `{s.student_id}`\n"
                    f"- **Date of Birth:** {s.date_of_birth}\n"
                    f"- **Email:** {s.email or 'N/A'}\n"
                    f"- **Phone:** {s.phone or 'N/A'}\n"
                    f"- **Course:** {s.course or 'N/A'}\n"
                    f"- **Address:** {s.address or 'N/A'}\n"
                    f"- **Enrollment Date:** {s.enrollment_date or 'N/A'}"
                )
                return "student_profile", {"student": details}, summary

        # 7. General snapshot / fallback
        context = crud.ai_get_comprehensive_context(db)
        summary = (
            f"EduSphere currently holds **{context['total_count']}** registered students across "
            f"**{len(context['courses'])}** courses ({', '.join(context['courses']) if context['courses'] else 'No courses yet'}).\n\n"
            f"You can ask me to search by course, birth year, contact info, or get course statistics!"
        )
        return "general_overview", context, summary

    async def answer_question(self, query: str, db: Session) -> Dict[str, Any]:
        """
        Main query responder:
        1. Retrieves grounded records from SQLite.
        2. Queries Ollama if online.
        3. Falls back gracefully with grounded synthesis and setup guidance if offline.
        """
        # Step 1: Controlled Database Retrieval
        intent, grounded_data, grounded_summary = self.extract_intent_and_ground_data(query, db)

        # Step 2: Check Ollama availability
        ollama_available, models, err_msg = await self.check_ollama_status()

        suggestions = [
            "How many students are registered?",
            "Show students enrolled in Computer Science.",
            "Which students were born after 2005?",
            "Summarize the student distribution by course."
        ]

        if ollama_available:
            try:
                # Prepare grounded prompt
                chosen_model = self.model if (self.model in models or not models) else models[0]
                prompt = (
                    f"You are EduSphere Assistant, an intelligent database assistant for the EduSphere AI Student Management System.\n"
                    f"Answer the user query based ONLY on the verified database information below.\n"
                    f"Do NOT invent facts, fake IDs, or unrecorded students.\n\n"
                    f"[VERIFIED DATABASE CONTEXT]\n"
                    f"{grounded_summary}\n\n"
                    f"[RAW DATA]\n"
                    f"{grounded_data}\n\n"
                    f"[USER QUESTION]\n"
                    f"{query}\n\n"
                    f"Please provide a polite, professional, and neatly formatted markdown answer."
                )

                payload = {
                    "model": chosen_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2
                    }
                }

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                    if resp.status_code == 200:
                        res_data = resp.json()
                        llm_text = res_data.get("response", "").strip()
                        if llm_text:
                            return {
                                "query": query,
                                "answer": llm_text,
                                "grounded_data": grounded_data,
                                "source": "ollama",
                                "model": chosen_model,
                                "ollama_available": True,
                                "suggestions": suggestions
                            }
            except Exception as e:
                logger.warning(f"Ollama generation failed: {e}. Falling back to grounded rule engine.")

        # Step 3: Offline / Fallback mode
        # Provide the real grounded answer directly, plus clear enable guidance
        offline_note = (
            f"\n\n---\n"
            f"> 💡 **Local AI Note:** Ollama is currently offline or not detected. "
            f"The answer above was generated directly by the **EduSphere Grounded Engine** using real SQLite records.\n"
            f"> To enable conversational LLM mode: run `ollama serve` and `ollama run llama3.2` locally."
        )

        return {
            "query": query,
            "answer": grounded_summary + offline_note,
            "grounded_data": grounded_data,
            "source": "grounded_rules",
            "model": None,
            "ollama_available": False,
            "suggestions": suggestions
        }


ai_service = EduSphereAIService()
