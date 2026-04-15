import csv
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COURSE_ALIAS_PATH = DATA_DIR / "course_aliases.csv"
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
COURSE_CODE_PATTERN = re.compile(r"\b([A-Za-z]{2,5})[\s-]?(\d{3}[A-Za-z]?)\b")
GRADE_TOKEN_PATTERN = re.compile(r"\b(?:A|A-|A\+|B|B-|B\+|C|C-|C\+|D|D-|D\+|P|PS|CR|S)\b")


@dataclass(frozen=True)
class RetrievedDocument:
    source_type: str
    title: str
    content: str
    department: Optional[str] = None
    major: Optional[str] = None
    contact: Optional[str] = None
    score: float = 0.0


@dataclass(frozen=True)
class AttachmentCourseSignals:
    mentioned_codes: tuple[str, ...] = ()
    completed_codes: tuple[str, ...] = ()
    planned_codes: tuple[str, ...] = ()
    remaining_codes: tuple[str, ...] = ()


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


@lru_cache(maxsize=1)
def load_course_rows() -> tuple[dict[str, str], ...]:
    path = DATA_DIR / "courses.csv"
    if not path.exists():
        return tuple()

    with path.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_course_alias_rows() -> tuple[dict[str, str], ...]:
    if not COURSE_ALIAS_PATH.exists():
        return tuple()

    with COURSE_ALIAS_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def _course_alias_map() -> dict[str, str]:
    alias_map: dict[str, str] = {}
    for row in load_course_alias_rows():
        alias_code = _normalize(row.get("alias_code")).upper()
        canonical_code = _normalize(row.get("canonical_code")).upper()
        if alias_code and canonical_code:
            alias_map[alias_code] = canonical_code
    return alias_map


def canonicalize_course_code(code: Optional[str]) -> str:
    normalized = _normalize(code).upper()
    if not normalized:
        return ""
    return _course_alias_map().get(normalized, normalized)


def extract_known_course_codes(text: Optional[str], limit: int = 12) -> list[str]:
    if not text:
        return []

    known_codes = {
        canonicalize_course_code(row.get("code"))
        for row in load_course_rows()
        if _normalize(row.get("code"))
    }
    matched_codes: list[str] = []
    seen: set[str] = set()

    for prefix, number in COURSE_CODE_PATTERN.findall(text):
        normalized = canonicalize_course_code(f"{prefix.upper()}{number.upper()}")
        if normalized in known_codes and normalized not in seen:
            seen.add(normalized)
            matched_codes.append(normalized)
            if len(matched_codes) >= limit:
                break

    return matched_codes


def extract_all_course_codes(text: Optional[str], limit: int = 30) -> list[str]:
    if not text:
        return []

    detected_codes: list[str] = []
    seen: set[str] = set()
    for prefix, number in COURSE_CODE_PATTERN.findall(text):
        normalized = canonicalize_course_code(f"{prefix.upper()}{number.upper()}")
        if normalized in seen:
            continue
        seen.add(normalized)
        detected_codes.append(normalized)
        if len(detected_codes) >= limit:
            break

    return detected_codes


def get_course_documents_by_code(course_codes: Iterable[str], limit: int = 6) -> list[RetrievedDocument]:
    target_codes = [canonicalize_course_code(code) for code in course_codes if _normalize(code)]
    if not target_codes:
        return []

    row_map = {
        canonicalize_course_code(row.get("code")): row
        for row in load_course_rows()
        if _normalize(row.get("code"))
    }
    docs: list[RetrievedDocument] = []
    seen: set[str] = set()

    for code in target_codes:
        if code in seen:
            continue
        row = row_map.get(code)
        if not row:
            continue
        seen.add(code)
        docs.append(
            RetrievedDocument(
                source_type="course",
                title=f"{code}: {_normalize(row.get('title'))}",
                content=(
                    f"Description: {_normalize(row.get('description'))}. "
                    f"Credits: {_normalize(row.get('credits'))}. "
                    f"Department: {_normalize(row.get('department'))}. "
                    f"Level: {_normalize(row.get('level'))}. "
                    f"Semester Offered: {_normalize(row.get('semester_offered'))}. "
                    f"Instructor: {_normalize(row.get('instructor'))}."
                ),
                department=_normalize(row.get("department")) or None,
                major=_normalize(row.get("department")) or None,
            )
        )
        if len(docs) >= limit:
            break

    return docs


def extract_attachment_course_signals(
    text: Optional[str],
    document_type: Optional[str],
    limit: int = 16,
) -> AttachmentCourseSignals:
    if not text:
        return AttachmentCourseSignals()

    known_codes = {
        canonicalize_course_code(row.get("code"))
        for row in load_course_rows()
        if _normalize(row.get("code"))
    }
    completed_keywords = {
        "completed",
        "earned",
        "passed",
        "fulfilled",
        "satisfied",
        "taken",
        "history",
    }
    planned_keywords = {
        "schedule",
        "planned",
        "enrolled",
        "registered",
        "current",
        "taking",
        "ip",
        "in-progress",
        "in progress",
    }
    schedule_keywords = {"semester", "fall", "spring", "summer", "winter"}
    remaining_keywords = {
        "remaining",
        "needed",
        "required",
        "outstanding",
        "incomplete",
        "missing",
        "still need",
        "not completed",
    }

    mentioned: list[str] = []
    completed: list[str] = []
    planned: list[str] = []
    remaining: list[str] = []
    seen_mentioned: set[str] = set()
    seen_completed: set[str] = set()
    seen_planned: set[str] = set()
    seen_remaining: set[str] = set()

    text_segments = [
        segment.strip()
        for segment in re.split(r"[\r\n]+|(?<=[.!?;])\s+", text)
        if segment.strip()
    ] or [text]

    for raw_line in text_segments:
        lowered_line = raw_line.lower()
        line_codes: list[str] = []
        for prefix, number in COURSE_CODE_PATTERN.findall(raw_line):
            normalized = canonicalize_course_code(f"{prefix.upper()}{number.upper()}")
            if normalized not in known_codes:
                continue
            line_codes.append(normalized)
            if normalized not in seen_mentioned:
                seen_mentioned.add(normalized)
                mentioned.append(normalized)
                if len(mentioned) >= limit:
                    break
        if not line_codes:
            continue

        has_completed_signal = any(keyword in lowered_line for keyword in completed_keywords)
        has_grade_signal = document_type in {"transcript", "degree_audit"} and bool(
            GRADE_TOKEN_PATTERN.search(raw_line)
        )
        has_planned_signal = any(keyword in lowered_line for keyword in planned_keywords) or (
            document_type == "schedule"
            and any(keyword in lowered_line for keyword in schedule_keywords)
        )
        has_remaining_signal = any(keyword in lowered_line for keyword in remaining_keywords)
        transcript_completed_line = (
            document_type == "transcript"
            and not has_planned_signal
            and not has_remaining_signal
        )

        for code in line_codes:
            if has_completed_signal or has_grade_signal or transcript_completed_line:
                if code not in seen_completed:
                    seen_completed.add(code)
                    completed.append(code)
            if has_planned_signal or document_type == "schedule":
                if code not in seen_planned:
                    seen_planned.add(code)
                    planned.append(code)
            if has_remaining_signal:
                if code not in seen_remaining:
                    seen_remaining.add(code)
                    remaining.append(code)

    if document_type == "degree_audit" and not remaining:
        for code in mentioned:
            if (
                code not in seen_completed
                and code not in seen_planned
                and code not in seen_remaining
            ):
                seen_remaining.add(code)
                remaining.append(code)

    return AttachmentCourseSignals(
        mentioned_codes=tuple(mentioned[:limit]),
        completed_codes=tuple(completed[:limit]),
        planned_codes=tuple(planned[:limit]),
        remaining_codes=tuple(remaining[:limit]),
    )


def evaluate_course_plan(
    planned_course_codes: Iterable[str],
    completed_course_codes: Iterable[str],
) -> dict[str, list[str]]:
    planned = [canonicalize_course_code(code) for code in planned_course_codes if _normalize(code)]
    completed_set = {
        canonicalize_course_code(code) for code in completed_course_codes if _normalize(code)
    }
    prereq_map = _prerequisite_map()

    ready: list[str] = []
    blocked: list[str] = []
    already_completed: list[str] = []

    for code in planned:
        if code in completed_set:
            already_completed.append(code)
            continue
        missing_prereqs = [
            prereq for prereq in prereq_map.get(code, [])
            if prereq not in completed_set
        ]
        if missing_prereqs:
            blocked.append(f"{code} (missing {', '.join(missing_prereqs)})")
        else:
            ready.append(code)

    return {
        "ready_courses": ready,
        "blocked_courses": blocked,
        "already_completed_courses": already_completed,
    }


def summarize_schedule_plan(
    planned_course_codes: Iterable[str],
    completed_course_codes: Iterable[str],
    major: Optional[str] = None,
) -> dict[str, object]:
    planned = [canonicalize_course_code(code) for code in planned_course_codes if _normalize(code)]
    course_map = {
        canonicalize_course_code(row.get("code")): row
        for row in load_course_rows()
        if _normalize(row.get("code"))
    }
    progress = get_degree_progress(major, completed_course_codes)
    required_set = set(progress.get("required_courses", []))

    total_credits = 0
    credit_known = False
    required_in_plan: list[str] = []
    outside_known_requirements: list[str] = []

    for code in planned:
        row = course_map.get(code)
        credits_value = _normalize(row.get("credits")) if row else ""
        if credits_value.isdigit():
            total_credits += int(credits_value)
            credit_known = True
        if code in required_set:
            required_in_plan.append(code)
        elif major:
            outside_known_requirements.append(code)

    return {
        "total_credits": total_credits if credit_known else None,
        "required_in_plan": required_in_plan,
        "outside_known_requirements": outside_known_requirements,
    }


def compare_degree_audit(
    audit_remaining_codes: Iterable[str],
    completed_course_codes: Iterable[str],
    major: Optional[str] = None,
) -> dict[str, list[str]]:
    audit_remaining = {
        canonicalize_course_code(code) for code in audit_remaining_codes if _normalize(code)
    }
    progress = get_degree_progress(major, completed_course_codes)
    system_remaining = set(progress.get("remaining_courses", []))

    return {
        "overlap_remaining": sorted(audit_remaining & system_remaining),
        "audit_only_remaining": sorted(audit_remaining - system_remaining),
        "system_only_remaining": sorted(system_remaining - audit_remaining),
    }


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


def _program_documents() -> List[RetrievedDocument]:
    path = DATA_DIR / "programs.csv"
    if not path.exists():
        return []

    docs = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            major = _normalize(row.get("major"))
            canonical_major = _normalize(row.get("canonical_major"))
            department = _normalize(row.get("department"))
            school = _normalize(row.get("school"))
            aliases = _normalize(row.get("aliases"))
            docs.append(
                RetrievedDocument(
                    source_type="program",
                    title=f"{major} program",
                    content=(
                        f"Canonical Major: {canonical_major}. Degree Type: {_normalize(row.get('degree_type'))}. "
                        f"Department: {department}. School: {school}. "
                        f"Aliases: {aliases}. Notes: {_normalize(row.get('notes'))}. "
                        f"Source URL: {_normalize(row.get('source_url'))}."
                    ),
                    department=department or None,
                    major=major or None,
                )
            )
    return docs


@lru_cache(maxsize=1)
def load_degree_requirement_rows() -> tuple[dict[str, str], ...]:
    path = DATA_DIR / "degree_requirements.csv"
    if not path.exists():
        return tuple()

    with path.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_program_rows() -> tuple[dict[str, str], ...]:
    path = DATA_DIR / "programs.csv"
    if not path.exists():
        return tuple()

    with path.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_department_rows() -> tuple[dict[str, str], ...]:
    path = DATA_DIR / "departments.csv"
    if not path.exists():
        return tuple()

    with path.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_faculty_rows() -> tuple[dict[str, str], ...]:
    path = DATA_DIR / "faculty.csv"
    if not path.exists():
        return tuple()

    with path.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_support_resource_rows() -> tuple[dict[str, str], ...]:
    path = DATA_DIR / "support_resources.csv"
    if not path.exists():
        return tuple()

    with path.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_prerequisite_rows() -> tuple[dict[str, str], ...]:
    path = DATA_DIR / "prerequisites.csv"
    if not path.exists():
        return tuple()

    with path.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def _program_lookup() -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for row in load_program_rows():
        names = {
            _normalize(row.get("major")),
            _normalize(row.get("canonical_major")),
        }
        names.update(
            alias.strip()
            for alias in _normalize(row.get("aliases")).split(";")
            if alias.strip()
        )
        for name in names:
            if name:
                lookup[name.lower()] = row
    return lookup


def find_program_row(major: Optional[str]) -> Optional[dict[str, str]]:
    if not major:
        return None
    return _program_lookup().get(_normalize(major).lower())


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
        *_program_documents(),
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
    if doc.source_type == "program" and any(token in query_tokens for token in {"program", "major", "school", "college", "path"}):
        score += 2.5
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


def _course_sort_key(code: str, course_map: dict[str, dict[str, str]]) -> tuple[int, int, str]:
    row = course_map.get(code, {})
    level = _normalize(row.get("level")) or "999"
    semester = _normalize(row.get("semester_offered"))
    semester_bonus = 0 if "Fall/Spring" in semester else 1
    return (int(level), semester_bonus, code)


def _prerequisite_map() -> dict[str, list[str]]:
    prereq_map: dict[str, list[str]] = {}
    for row in load_prerequisite_rows():
        course_code = canonicalize_course_code(row.get("course_code"))
        prerequisites = [
            canonicalize_course_code(code)
            for code in _normalize(row.get("prerequisites")).split(";")
            if code.strip()
        ]
        if course_code:
            prereq_map[course_code] = prerequisites
    return prereq_map


def _recommend_next_courses(required: list[str], completed: list[str]) -> tuple[list[str], list[str]]:
    completed_set = set(completed)
    course_map = {
        canonicalize_course_code(row.get("code")): row
        for row in load_course_rows()
    }
    prereq_map = _prerequisite_map()

    remaining = [code for code in required if code not in completed_set]
    ready: list[str] = []
    blocked: list[str] = []
    for code in remaining:
        prerequisites = prereq_map.get(code, [])
        if all(prereq in completed_set for prereq in prerequisites):
            ready.append(code)
        else:
            blocked.append(code)

    ready.sort(key=lambda code: _course_sort_key(code, course_map))
    blocked.sort(key=lambda code: _course_sort_key(code, course_map))
    recommendations = ready[:3] if ready else blocked[:3]
    return recommendations, blocked


def get_degree_progress(major: Optional[str], completed_course_codes: Iterable[str]) -> dict[str, object]:
    completed = sorted(
        {canonicalize_course_code(code) for code in completed_course_codes if _normalize(code)}
    )
    if not major:
        return {
            "major": None,
            "required_courses": [],
            "completed_courses": completed,
            "remaining_courses": [],
            "recommended_next_courses": [],
            "blocked_courses": [],
            "completion_percent": 0.0,
            "notes": None,
            "advising_tips": None,
        }

    program_row = find_program_row(major)
    canonical_major = _normalize(program_row.get("canonical_major")) if program_row else major
    major_lower = canonical_major.lower()
    matching_row = next(
        (row for row in load_degree_requirement_rows() if _normalize(row.get("major")).lower() == major_lower),
        None,
    )
    if not matching_row:
        program_notes = _normalize(program_row.get("notes")) if program_row else ""
        program_department = _normalize(program_row.get("department")) if program_row else ""
        program_school = _normalize(program_row.get("school")) if program_row else ""
        return {
            "major": major,
            "required_courses": [],
            "completed_courses": completed,
            "remaining_courses": [],
            "recommended_next_courses": [],
            "blocked_courses": [],
            "completion_percent": 0.0,
            "notes": program_notes or None,
            "advising_tips": (
                f"This official Morgan program is currently mapped to {program_department} in {program_school}. "
                "Use the program and department pages for detailed requirement verification until full major-level requirement modeling is added."
                if program_department or program_school
                else None
            ),
        }

    required = [
        canonicalize_course_code(code)
        for code in _normalize(matching_row.get("required_courses")).split(";")
        if code.strip()
    ]
    remaining = [code for code in required if code not in completed]
    recommended_next_courses, blocked_courses = _recommend_next_courses(required, completed)
    completion_percent = round((len(required) - len(remaining)) / len(required) * 100, 1) if required else 0.0

    return {
        "major": _normalize(matching_row.get("major")) or major,
        "required_courses": required,
        "completed_courses": completed,
        "remaining_courses": remaining,
        "recommended_next_courses": recommended_next_courses,
        "blocked_courses": blocked_courses,
        "completion_percent": completion_percent,
        "notes": _normalize(matching_row.get("notes")) or None,
        "advising_tips": _normalize(matching_row.get("advising_tips")) or None,
    }
