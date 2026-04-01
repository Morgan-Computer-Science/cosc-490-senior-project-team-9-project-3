import csv
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "i",
    "in",
    "is",
    "me",
    "my",
    "of",
    "the",
    "to",
    "what",
    "who",
}
SUPPORT_TOKENS = {"stress", "anxiety", "help", "support", "counseling", "mental", "overwhelmed"}


@dataclass(frozen=True)
class RetrievedDocument:
    source_type: str
    title: str
    content: str
    department: Optional[str] = None
    major: Optional[str] = None
    contact: Optional[str] = None
    score: float = 0.0


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if token not in STOPWORDS
    }


def _normalize(value: Optional[str]) -> str:
    return (value or "").strip()


def _course_documents() -> List[RetrievedDocument]:
    path = DATA_DIR / "courses.csv"
    if not path.exists():
        return []

    docs = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            title = f"{_normalize(row.get('code'))}: {_normalize(row.get('title'))}"
            content = (
                f"Description: {_normalize(row.get('description'))}. "
                f"Credits: {_normalize(row.get('credits'))}. "
                f"Department: {_normalize(row.get('department'))}. "
                f"Level: {_normalize(row.get('level'))}. "
                f"Semester Offered: {_normalize(row.get('semester_offered'))}. "
                f"Instructor: {_normalize(row.get('instructor'))}."
            )
            docs.append(
                RetrievedDocument(
                    source_type="course",
                    title=title,
                    content=content,
                    department=_normalize(row.get("department")) or None,
                    major=_normalize(row.get("department")) or None,
                )
            )
    return docs


def _department_documents() -> List[RetrievedDocument]:
    path = DATA_DIR / "departments.csv"
    if not path.exists():
        return []

    docs = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            department = _normalize(row.get("department"))
            major = _normalize(row.get("major"))
            docs.append(
                RetrievedDocument(
                    source_type="department",
                    title=f"{department} Department",
                    content=(
                        f"Major: {major}. Office: {_normalize(row.get('office'))}. "
                        f"Email: {_normalize(row.get('email'))}. "
                        f"Phone: {_normalize(row.get('phone'))}. "
                        f"Overview: {_normalize(row.get('overview'))}."
                    ),
                    department=department or None,
                    major=major or None,
                    contact=_normalize(row.get("email")) or _normalize(row.get("phone")) or None,
                )
            )
    return docs


def _faculty_documents() -> List[RetrievedDocument]:
    path = DATA_DIR / "faculty.csv"
    if not path.exists():
        return []

    docs = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            department = _normalize(row.get("department"))
            docs.append(
                RetrievedDocument(
                    source_type="faculty",
                    title=f"{_normalize(row.get('name'))} - {_normalize(row.get('title'))}",
                    content=(
                        f"Department: {department}. Email: {_normalize(row.get('email'))}. "
                        f"Office: {_normalize(row.get('office'))}. "
                        f"Office Hours: {_normalize(row.get('office_hours'))}. "
                        f"Specialties: {_normalize(row.get('specialties'))}."
                    ),
                    department=department or None,
                    major=department or None,
                    contact=_normalize(row.get("email")) or None,
                )
            )
    return docs


def _degree_documents() -> List[RetrievedDocument]:
    path = DATA_DIR / "degree_requirements.csv"
    if not path.exists():
        return []

    docs = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            major = _normalize(row.get("major"))
            department = _normalize(row.get("department"))
            docs.append(
                RetrievedDocument(
                    source_type="degree_requirements",
                    title=f"{major} degree requirements",
                    content=(
                        f"Department: {department}. Required Courses: {_normalize(row.get('required_courses'))}. "
                        f"Notes: {_normalize(row.get('notes'))}. "
                        f"Advising Tips: {_normalize(row.get('advising_tips'))}."
                    ),
                    department=department or None,
                    major=major or None,
                )
            )
    return docs


def _support_documents() -> List[RetrievedDocument]:
    path = DATA_DIR / "support_resources.csv"
    if not path.exists():
        return []

    docs = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            docs.append(
                RetrievedDocument(
                    source_type="support_resource",
                    title=f"{_normalize(row.get('resource'))} ({_normalize(row.get('category'))})",
                    content=(
                        f"Contact: {_normalize(row.get('contact'))}. "
                        f"Details: {_normalize(row.get('details'))}."
                    ),
                    contact=_normalize(row.get("contact")) or None,
                )
            )
    return docs


@lru_cache(maxsize=1)
def load_knowledge_documents() -> tuple[RetrievedDocument, ...]:
    docs = [
        *_course_documents(),
        *_department_documents(),
        *_faculty_documents(),
        *_degree_documents(),
        *_support_documents(),
    ]
    return tuple(docs)


def _score_document(query_tokens: set[str], query: str, user_major: Optional[str], doc: RetrievedDocument) -> float:
    haystack = f"{doc.title} {doc.content}".lower()
    doc_tokens = _tokenize(haystack)
    overlap = query_tokens & doc_tokens
    if not overlap:
        return 0.0

    score = float(len(overlap))
    lowered_query = query.lower()

    if lowered_query in haystack:
        score += 5.0

    if user_major:
        user_major_lower = user_major.lower()
        if doc.major and user_major_lower in doc.major.lower():
            score += 3.0
        if doc.department and user_major_lower in doc.department.lower():
            score += 2.0

    if doc.source_type == "degree_requirements" and any(token in query_tokens for token in {"requirement", "required", "need", "graduate"}):
        score += 2.5
    if doc.source_type == "faculty" and any(token in query_tokens for token in {"faculty", "professor", "teacher", "instructor"}):
        score += 2.5
    if doc.source_type == "department" and any(token in query_tokens for token in {"department", "office", "advisor", "contact"}):
        score += 2.0
    if doc.source_type == "support_resource" and any(token in query_tokens for token in SUPPORT_TOKENS):
        score += 8.0
    if doc.source_type == "course" and any(token in query_tokens for token in {"course", "class", "take", "schedule", "prerequisite"}):
        score += 1.5

    return score


def retrieve_relevant_documents(
    query: str,
    user_major: Optional[str] = None,
    top_k: int = 6,
) -> List[RetrievedDocument]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    scored_docs = []
    for doc in load_knowledge_documents():
        score = _score_document(query_tokens, query, user_major, doc)
        if score > 0:
            scored_docs.append(
                RetrievedDocument(
                    source_type=doc.source_type,
                    title=doc.title,
                    content=doc.content,
                    department=doc.department,
                    major=doc.major,
                    contact=doc.contact,
                    score=score,
                )
            )

    scored_docs.sort(key=lambda doc: (-doc.score, doc.source_type, doc.title))
    return scored_docs[:top_k]


def format_retrieved_context(documents: Iterable[RetrievedDocument]) -> str:
    docs = list(documents)
    if not docs:
        return ""

    lines = ["Retrieved Morgan State advising context:"]
    for doc in docs:
        header = f"- [{doc.source_type}] {doc.title}"
        details = []
        if doc.department:
            details.append(f"Department: {doc.department}")
        if doc.major:
            details.append(f"Major: {doc.major}")
        if doc.contact:
            details.append(f"Contact: {doc.contact}")
        if details:
            header += f" ({', '.join(details)})"
        lines.append(header)
        lines.append(f"  {doc.content}")

    return "\n".join(lines)
