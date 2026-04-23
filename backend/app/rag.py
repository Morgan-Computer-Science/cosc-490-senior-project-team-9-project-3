import csv
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COURSE_ALIAS_PATH = DATA_DIR / "course_aliases.csv"
BUSINESS_PATHWAYS_PATH = DATA_DIR / "business_pathways.csv"
TECH_HEALTH_PATHWAYS_PATH = DATA_DIR / "tech_health_pathways.csv"
CS_PATHWAYS_PATH = DATA_DIR / "cs_pathways.csv"
CS_CAPSTONE_RULES_PATH = DATA_DIR / "cs_capstone_rules.csv"
CS_FOCUS_AREAS_PATH = DATA_DIR / "cs_focus_areas.csv"
OFFICES_PATH = DATA_DIR / "offices.csv"
ORGANIZATIONS_PATH = DATA_DIR / "organizations.csv"
OPPORTUNITIES_PATH = DATA_DIR / "opportunities.csv"
PROCESS_GUIDANCE_PATH = DATA_DIR / "process_guidance.csv"
WORKFLOW_ENTRYPOINTS_PATH = DATA_DIR / "workflow_entrypoints.csv"
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
SUPPORT_TOKENS = {
    "stress",
    "anxiety",
    "help",
    "support",
    "counseling",
    "mental",
    "overwhelmed",
    "tutoring",
    "accessibility",
    "accommodation",
    "accommodations",
    "internship",
    "internships",
    "career",
    "research",
    "scholarship",
    "scholarships",
    "funding",
    "grant",
    "grants",
    "stipend",
    "resume",
    "resumes",
    "job",
    "jobs",
    "success",
}
GREETING_PATTERNS = (
    "hello",
    "hi",
    "hey",
    "how are you",
    "how's it going",
    "whats up",
    "what's up",
    "good morning",
    "good afternoon",
    "good evening",
    "thanks",
    "thank you",
)
LEADERSHIP_TOKENS = {"dean", "chair", "director", "head", "lead", "leader", "runs", "run", "in charge"}
OFFICE_TOKENS = {
    "office",
    "contact",
    "advising",
    "advisor",
    "registrar",
    "transfer",
    "support",
    "tutoring",
    "career",
    "financial",
    "aid",
    "counseling",
    "resource",
    "tutoring",
    "accessibility",
    "accommodation",
    "accommodations",
    "internship",
    "internships",
    "research",
    "center",
    "centers",
    "involved",
    "scholarship",
    "scholarships",
    "funding",
    "grant",
    "grants",
    "stipend",
    "resume",
    "resumes",
    "job",
    "jobs",
    "success",
}
ORG_TOKENS = {
    "organization",
    "organizations",
    "org",
    "orgs",
    "club",
    "clubs",
    "team",
    "teams",
    "robotics",
    "society",
    "group",
    "chapter",
    "lab",
    "labs",
    "research",
    "community",
    "involved",
}
OPPORTUNITY_TOKENS = {
    "career",
    "internship",
    "internships",
    "scholarship",
    "scholarships",
    "funding",
    "grant",
    "grants",
    "stipend",
    "research",
    "resume",
    "resumes",
    "job",
    "jobs",
    "opportunity",
    "opportunities",
}
PROCESS_TOKENS = {
    "transcript",
    "transcripts",
    "registrar",
    "transfer",
    "withdraw",
    "withdrawal",
    "drop",
    "override",
    "permission",
    "clearance",
    "graduation",
    "verification",
    "record",
    "records",
    "registration",
    "accommodation",
    "accommodations",
}
WORKFLOW_TOKENS = {
    "form",
    "forms",
    "page",
    "pages",
    "start",
    "begin",
    "apply",
    "application",
    "request",
    "requests",
    "workflow",
    "entry",
    "entrypoint",
    "entrypoints",
    "submit",
}
TRANSCRIPT_TOKENS = {
    "gpa",
    "credits",
    "earned",
    "standing",
    "transcript",
    "degreeworks",
    "degree",
    "audit",
    "import",
    "pdf",
}
COURSE_PREREQ_TOKENS = {"prerequisite", "prereq", "before", "requires", "need before"}
DEGREE_PLANNING_TOKENS = {
    "take next",
    "next semester",
    "schedule",
    "plan",
    "degree requirements",
    "graduate",
    "remaining",
    "capstone",
    "ready",
}
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


def classify_question_intent(question: str) -> str:
    lowered = _normalize(question).lower()
    if not lowered:
        return "degree_planning"

    if any(pattern in lowered for pattern in GREETING_PATTERNS):
        return "small_talk"
    if any(token in lowered for token in WORKFLOW_TOKENS) and any(
        token in lowered
        for token in PROCESS_TOKENS
        | {
            "student organization",
            "organizations",
            "research",
            "internship",
            "internships",
            "career",
        }
    ):
        return "workflow_entrypoint"
    if (
        ("transcript" in lowered and any(token in lowered for token in {"get", "request", "order", "send"}))
        or any(token in lowered for token in {"withdraw", "withdrawal", "override", "permission", "clearance", "verification"})
        or ("transfer" in lowered and "credit" in lowered)
        or ("registration" in lowered and any(token in lowered for token in {"problem", "issue", "override", "cannot", "can't"}))
        or ("accommodation" in lowered or "accommodations" in lowered)
    ):
        return "policy_process"
    if any(token in lowered for token in TRANSCRIPT_TOKENS):
        return "transcript_import"
    if (
        any(token in lowered for token in {"program", "major"})
        or any(token in lowered for token in DEGREE_PLANNING_TOKENS)
    ) and not any(
        token in lowered
        for token in {
            "office",
            "contact",
            "registrar",
            "transfer",
            "counseling",
            "accessibility",
            "accommodation",
            "financial aid",
            "scholarship",
            "scholarships",
            "internship",
            "internships",
            "career",
            "tutoring",
        }
    ):
        return "degree_planning"
    if any(token in lowered for token in ORG_TOKENS):
        return "organization_team"
    if any(token in lowered for token in OFFICE_TOKENS):
        return "office_resource"
    if any(token in lowered for token in LEADERSHIP_TOKENS) or any(
        phrase in lowered for phrase in ("who is", "who should i contact", "who do i contact")
    ):
        return "people_contact_leadership"
    if any(token in lowered for token in COURSE_PREREQ_TOKENS):
        return "course_prerequisite"
    if any(token in lowered for token in DEGREE_PLANNING_TOKENS):
        return "degree_planning"
    return "degree_planning"


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
def load_office_rows() -> tuple[dict[str, str], ...]:
    if not OFFICES_PATH.exists():
        return tuple()

    with OFFICES_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_organization_rows() -> tuple[dict[str, str], ...]:
    if not ORGANIZATIONS_PATH.exists():
        return tuple()

    with ORGANIZATIONS_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_opportunity_rows() -> tuple[dict[str, str], ...]:
    if not OPPORTUNITIES_PATH.exists():
        return tuple()

    with OPPORTUNITIES_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_process_guidance_rows() -> tuple[dict[str, str], ...]:
    if not PROCESS_GUIDANCE_PATH.exists():
        return tuple()

    with PROCESS_GUIDANCE_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_workflow_entrypoint_rows() -> tuple[dict[str, str], ...]:
    if not WORKFLOW_ENTRYPOINTS_PATH.exists():
        return tuple()

    with WORKFLOW_ENTRYPOINTS_PATH.open(newline="", encoding="utf-8") as file:
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


@lru_cache(maxsize=1)
def _known_major_department_names() -> tuple[str, ...]:
    names: set[str] = set()

    for row in load_program_rows():
        for value in (
            row.get("major"),
            row.get("canonical_major"),
            row.get("department"),
        ):
            normalized = _normalize(value).lower()
            if normalized:
                names.add(normalized)
        aliases = _normalize(row.get("aliases"))
        if aliases:
            for alias in aliases.split(";"):
                normalized = _normalize(alias).lower()
                if normalized:
                    names.add(normalized)

    for row in load_department_rows():
        for value in (row.get("department"), row.get("major")):
            normalized = _normalize(value).lower()
            if normalized:
                names.add(normalized)

    return tuple(sorted(names))


def _query_mentions_other_named_unit(query: str, user_major: Optional[str]) -> bool:
    lowered_query = query.lower()
    normalized_major = _normalize(user_major).lower()
    if not normalized_major:
        return False

    for unit_name in _known_major_department_names():
        if unit_name == normalized_major:
            continue
        if normalized_major in unit_name:
            continue
        if unit_name in lowered_query:
            return True
    return False


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


def _office_documents() -> List[RetrievedDocument]:
    docs = []
    for row in load_office_rows():
        docs.append(
            RetrievedDocument(
                source_type="office",
                title=f"{_normalize(row.get('office'))} ({_normalize(row.get('category'))})",
                content=(
                    f"Email: {_normalize(row.get('email'))}. "
                    f"Phone: {_normalize(row.get('phone'))}. "
                    f"Location: {_normalize(row.get('location'))}. "
                    f"Overview: {_normalize(row.get('overview'))}. "
                    f"Source URL: {_normalize(row.get('source_url'))}."
                ),
                contact=_normalize(row.get("email")) or _normalize(row.get("phone")) or None,
            )
        )
    return docs


def _organization_documents() -> List[RetrievedDocument]:
    docs = []
    for row in load_organization_rows():
        department = _normalize(row.get("owner_department"))
        docs.append(
            RetrievedDocument(
                source_type="organization",
                title=f"{_normalize(row.get('name'))} ({_normalize(row.get('category'))})",
                content=(
                    f"Owner Department: {department}. "
                    f"Email: {_normalize(row.get('contact_email'))}. "
                    f"Phone: {_normalize(row.get('contact_phone'))}. "
                    f"Overview: {_normalize(row.get('overview'))}. "
                    f"Source URL: {_normalize(row.get('url'))}."
                ),
                department=department or None,
                major=department or None,
                contact=_normalize(row.get("contact_email")) or _normalize(row.get("contact_phone")) or None,
            )
        )
    return docs


def _opportunity_documents() -> List[RetrievedDocument]:
    docs = []
    for row in load_opportunity_rows():
        owner_office = _normalize(row.get("owner_office"))
        docs.append(
            RetrievedDocument(
                source_type="opportunity",
                title=f"{_normalize(row.get('name'))} ({_normalize(row.get('category'))})",
                content=(
                    f"Owner Office: {owner_office}. "
                    f"Email: {_normalize(row.get('contact_email'))}. "
                    f"Phone: {_normalize(row.get('contact_phone'))}. "
                    f"Overview: {_normalize(row.get('overview'))}. "
                    f"Source URL: {_normalize(row.get('url'))}."
                ),
                department=owner_office or None,
                major=owner_office or None,
                contact=_normalize(row.get("contact_email")) or _normalize(row.get("contact_phone")) or None,
            )
        )
    return docs


def _process_guidance_documents() -> List[RetrievedDocument]:
    docs = []
    for row in load_process_guidance_rows():
        owner_office = _normalize(row.get("owner_office"))
        docs.append(
            RetrievedDocument(
                source_type="process_guidance",
                title=f"{_normalize(row.get('process'))} ({_normalize(row.get('category'))})",
                content=(
                    f"Owner Office: {owner_office}. "
                    f"Email: {_normalize(row.get('contact_email'))}. "
                    f"Phone: {_normalize(row.get('contact_phone'))}. "
                    f"Overview: {_normalize(row.get('overview'))}. "
                    f"Source URL: {_normalize(row.get('url'))}."
                ),
                department=owner_office or None,
                major=owner_office or None,
                contact=_normalize(row.get("contact_email")) or _normalize(row.get("contact_phone")) or None,
            )
        )
    return docs


def _workflow_entrypoint_documents() -> List[RetrievedDocument]:
    docs = []
    for row in load_workflow_entrypoint_rows():
        owner_office = _normalize(row.get("owner_office"))
        docs.append(
            RetrievedDocument(
                source_type="workflow_entrypoint",
                title=f"{_normalize(row.get('name'))} ({_normalize(row.get('category'))})",
                content=(
                    f"Owner Office: {owner_office}. "
                    f"Email: {_normalize(row.get('contact_email'))}. "
                    f"Phone: {_normalize(row.get('contact_phone'))}. "
                    f"Overview: {_normalize(row.get('overview'))}. "
                    f"Source URL: {_normalize(row.get('url'))}."
                ),
                department=owner_office or None,
                major=owner_office or None,
                contact=_normalize(row.get("contact_email")) or _normalize(row.get("contact_phone")) or None,
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
        *_office_documents(),
        *_organization_documents(),
        *_opportunity_documents(),
        *_process_guidance_documents(),
        *_workflow_entrypoint_documents(),
    ]
    return tuple(docs)


def _score_document(
    query_tokens: set[str],
    query: str,
    user_major: Optional[str],
    doc: RetrievedDocument,
    intent: str,
) -> float:
    haystack = f"{doc.title} {doc.content}".lower()
    doc_tokens = _tokenize(haystack)
    overlap = query_tokens & doc_tokens
    user_major_tokens = _tokenize(user_major or "")
    major_overlap = user_major_tokens & doc_tokens
    lowered_query = query.lower()
    explicit_doc_match = any(
        candidate and candidate.lower() in lowered_query
        for candidate in (doc.major, doc.department)
    )
    exact_major_match = bool(
        user_major
        and doc.major
        and _normalize(user_major).lower() == _normalize(doc.major).lower()
    )

    if not overlap and not major_overlap and not exact_major_match and not explicit_doc_match:
        return 0.0

    explicit_other_unit_query = _query_mentions_other_named_unit(query, user_major)
    score = float(len(overlap))
    if not explicit_other_unit_query:
        if intent in {"people_contact_leadership", "office_resource", "organization_team", "policy_process", "workflow_entrypoint"}:
            score += float(len(major_overlap)) * 0.25
        else:
            score += float(len(major_overlap)) * 1.5
    if exact_major_match:
        if intent in {"people_contact_leadership", "office_resource", "organization_team", "policy_process", "workflow_entrypoint"}:
            score += 1.0
        else:
            score += 2.0 if explicit_other_unit_query else 4.0

    if lowered_query in haystack:
        score += 5.0

    if explicit_doc_match:
        score += 8.0

    if user_major and not explicit_other_unit_query and intent not in {"people_contact_leadership", "office_resource", "organization_team", "policy_process", "workflow_entrypoint"}:
        user_major_lower = user_major.lower()
        if doc.major and user_major_lower in doc.major.lower():
            score += 3.0
        if doc.department and user_major_lower in doc.department.lower():
            score += 2.0

    if doc.source_type == "degree_requirements" and any(token in query_tokens for token in {"requirement", "required", "need", "graduate"}):
        score += 2.5
    leadership_query = any(token in query_tokens for token in {"dean", "chair", "director", "head"})
    if doc.source_type == "faculty" and any(token in query_tokens for token in {"faculty", "professor", "teacher", "instructor", "dean", "chair", "director", "head"}):
        score += 2.5
        if leadership_query:
            leadership_title = doc.title.lower()
            if any(token in leadership_title for token in {"dean", "chair", "director", "head"}):
                score += 6.0
            if "dean" in query_tokens and "dean" in leadership_title:
                score += 11.0
            if "chair" in query_tokens and "chair" in leadership_title:
                score += 5.0
            if "director" in query_tokens and "director" in leadership_title:
                score += 4.0
    if doc.source_type == "department" and any(token in query_tokens for token in {"department", "office", "advisor", "contact"}):
        score += 2.0
    if doc.source_type == "program" and any(token in query_tokens for token in {"program", "major", "school", "college", "path"}):
        score += 2.5
    if doc.source_type == "support_resource" and any(token in query_tokens for token in SUPPORT_TOKENS):
        score += 8.0
    if doc.source_type == "office" and any(token in query_tokens for token in OFFICE_TOKENS):
        score += 8.0
    if doc.source_type == "organization" and any(token in query_tokens for token in ORG_TOKENS):
        score += 8.0
    if doc.source_type == "opportunity" and any(token in query_tokens for token in OPPORTUNITY_TOKENS):
        score += 9.0
    if doc.source_type == "process_guidance" and any(token in query_tokens for token in PROCESS_TOKENS):
        score += 10.0
    if doc.source_type == "workflow_entrypoint" and any(token in query_tokens for token in WORKFLOW_TOKENS | PROCESS_TOKENS | ORG_TOKENS | OPPORTUNITY_TOKENS):
        score += 12.0
    if doc.source_type == "course" and any(token in query_tokens for token in {"course", "class", "take", "schedule", "prerequisite"}):
        score += 1.5

    if "tutoring" in query_tokens and ("tutoring" in haystack or "academic success" in haystack):
        score += 10.0
    if {"accessibility", "accommodation", "accommodations"} & query_tokens and "accessibility" in haystack:
        score += 10.0
    if {"internship", "internships", "career"} & query_tokens and ("career" in haystack or "internship" in haystack):
        score += 8.0
    if {"scholarship", "scholarships", "funding", "grant", "grants", "stipend"} & query_tokens and (
        "scholarship" in haystack or "grant" in haystack or "funding" in haystack or "stipend" in haystack
    ):
        score += 10.0
    if {"resume", "resumes", "job", "jobs"} & query_tokens and (
        "career" in haystack or "job" in haystack or "resume" in haystack or "handshake" in haystack
    ):
        score += 9.0
    if "research" in query_tokens and ("research" in haystack or "lab" in haystack):
        score += 8.0
    if "success" in query_tokens and ("student success" in haystack or "retention" in haystack or "academic success" in haystack):
        score += 10.0
    if {"struggling", "academically", "academic", "support"} & query_tokens and (
        "student success" in haystack or "retention" in haystack or "academic success" in haystack or "tutoring" in haystack
    ):
        score += 12.0
    if {"transcript", "transcripts"} & query_tokens and ("registrar" in haystack or "transcript" in haystack):
        score += 12.0
    if {"withdraw", "withdrawal", "drop"} & query_tokens and ("withdraw" in haystack or "registration" in haystack):
        score += 12.0
    if {"override", "permission"} & query_tokens and ("override" in haystack or "advising" in haystack or "registration" in haystack):
        score += 10.0
    if {"verification", "graduation", "clearance"} & query_tokens and ("verification" in haystack or "graduation" in haystack or "registrar" in haystack):
        score += 10.0
    if WORKFLOW_TOKENS & query_tokens and ("source url" in haystack or "starting point" in haystack or "official" in haystack or "page" in haystack):
        score += 12.0
    if "robotics" in query_tokens and "robotics" in haystack:
        score += 12.0
    if {"organization", "organizations", "org", "orgs", "club", "clubs", "community", "involved"} & query_tokens and (
        "student organization" in haystack
        or "student organizations" in haystack
        or "student life" in haystack
        or "get involved" in haystack
        or "community" in haystack
    ):
        score += 10.0
    if {"center", "research"} & query_tokens and "student research center" in haystack:
        score += 12.0

    if intent == "people_contact_leadership":
        if doc.source_type == "faculty":
            score += 7.0
        elif doc.source_type == "department":
            score += 4.0
        elif doc.source_type == "program":
            score += 2.0
    elif intent == "office_resource":
        if doc.source_type in {"office", "support_resource"}:
            score += 9.0
        elif doc.source_type == "opportunity" and any(token in query_tokens for token in OPPORTUNITY_TOKENS):
            score += 7.0
        elif doc.source_type == "department":
            score += 1.0
    elif intent == "policy_process":
        if doc.source_type == "process_guidance":
            score += 10.0
        elif doc.source_type in {"office", "support_resource"}:
            score += 5.0
        elif doc.source_type == "department":
            score += 1.0
    elif intent == "workflow_entrypoint":
        if doc.source_type == "workflow_entrypoint":
            score += 12.0
        elif doc.source_type == "process_guidance":
            score += 6.0
        elif doc.source_type in {"office", "support_resource", "opportunity", "organization"}:
            score += 3.0
    elif intent == "organization_team":
        if doc.source_type == "organization":
            score += 8.0
        elif doc.source_type in {"faculty", "department"}:
            score += 3.0
    elif intent == "course_prerequisite":
        if doc.source_type == "course":
            score += 5.0
        elif doc.source_type == "degree_requirements":
            score += 1.5
    elif intent == "transcript_import":
        if doc.source_type in {"degree_requirements", "course", "department"}:
            score += 1.0

    return score


def retrieve_relevant_documents(
    query: str,
    user_major: Optional[str] = None,
    top_k: int = 6,
) -> List[RetrievedDocument]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    intent = classify_question_intent(query)
    scored_docs = []
    for doc in load_knowledge_documents():
        score = _score_document(query_tokens, query, user_major, doc, intent)
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


@lru_cache(maxsize=1)
def load_business_pathway_rows() -> tuple[dict[str, str], ...]:
    if not BUSINESS_PATHWAYS_PATH.exists():
        return tuple()

    with BUSINESS_PATHWAYS_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_tech_health_pathway_rows() -> tuple[dict[str, str], ...]:
    if not TECH_HEALTH_PATHWAYS_PATH.exists():
        return tuple()

    with TECH_HEALTH_PATHWAYS_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_cs_pathway_rows() -> tuple[dict[str, str], ...]:
    if not CS_PATHWAYS_PATH.exists():
        return tuple()

    with CS_PATHWAYS_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_cs_capstone_rule_rows() -> tuple[dict[str, str], ...]:
    if not CS_CAPSTONE_RULES_PATH.exists():
        return tuple()

    with CS_CAPSTONE_RULES_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_cs_focus_area_rows() -> tuple[dict[str, str], ...]:
    if not CS_FOCUS_AREAS_PATH.exists():
        return tuple()

    with CS_FOCUS_AREAS_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


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


def _is_business_depth_major(major: Optional[str]) -> bool:
    return _normalize(major) in {
        "Business Administration",
        "Marketing",
        "Entrepreneurship",
        "Accounting",
        "Finance",
        "Hospitality Management",
        "Human Resource Management",
    }


def _is_tech_health_depth_major(major: Optional[str]) -> bool:
    return _normalize(major) in {
        "Information Systems",
        "Information Science",
        "Cloud Computing",
        "Nursing",
        "Biology",
        "Psychology",
    }


def _is_computer_science_major(major: Optional[str]) -> bool:
    return _normalize(major).lower() == "computer science"


def _unique_preserve_order(values: Iterable[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _apply_implied_completed_courses(
    major: Optional[str],
    completed_course_codes: Iterable[str],
) -> list[str]:
    completed = {
        canonicalize_course_code(code)
        for code in completed_course_codes
        if _normalize(code)
    }

    if _is_computer_science_major(major):
        if "MATH241" in completed or "MATH242" in completed:
            completed.add("MATH141")
        if "MATH242" in completed:
            completed.add("MATH241")

    return sorted(completed)


def _build_business_priority_map(major: Optional[str]) -> dict[str, int]:
    normalized_major = _normalize(major)
    if not normalized_major:
        return {}

    priority_map: dict[str, int] = {}
    for row in load_business_pathway_rows():
        if _normalize(row.get("major")) != normalized_major:
            continue
        course_code = canonicalize_course_code(row.get("required_course"))
        priority_value = _normalize(row.get("priority"))
        if not course_code or not priority_value.isdigit():
            continue
        priority_map[course_code] = int(priority_value)
    return priority_map


def _build_tech_health_priority_map(major: Optional[str]) -> dict[str, int]:
    normalized_major = _normalize(major)
    if not normalized_major:
        return {}

    priority_map: dict[str, int] = {}
    for row in load_tech_health_pathway_rows():
        if _normalize(row.get("major")) != normalized_major:
            continue
        course_code = canonicalize_course_code(row.get("required_course"))
        priority_value = _normalize(row.get("priority"))
        if not course_code or not priority_value.isdigit():
            continue
        priority_map[course_code] = int(priority_value)
    return priority_map


def _recommend_business_next_courses(
    major: Optional[str],
    required: list[str],
    completed: list[str],
) -> tuple[list[str], list[str]]:
    completed_set = set(completed)
    course_map = {
        canonicalize_course_code(row.get("code")): row
        for row in load_course_rows()
    }
    prereq_map = _prerequisite_map()
    priority_map = _build_business_priority_map(major)

    def _business_sort_key(code: str) -> tuple[int, int, int, str]:
        level, semester_bonus, course_code = _course_sort_key(code, course_map)
        return (priority_map.get(code, 999), level, semester_bonus, course_code)

    remaining = [code for code in required if code not in completed_set]
    ready: list[str] = []
    blocked: list[str] = []
    for code in remaining:
        prerequisites = prereq_map.get(code, [])
        if all(prereq in completed_set for prereq in prerequisites):
            ready.append(code)
        else:
            blocked.append(code)

    ready.sort(key=_business_sort_key)
    blocked.sort(key=_business_sort_key)
    recommendations = ready[:3] if ready else blocked[:3]
    return recommendations, blocked


def _recommend_tech_health_next_courses(
    major: Optional[str],
    required: list[str],
    completed: list[str],
) -> tuple[list[str], list[str]]:
    completed_set = set(completed)
    course_map = {
        canonicalize_course_code(row.get("code")): row
        for row in load_course_rows()
    }
    prereq_map = _prerequisite_map()
    priority_map = _build_tech_health_priority_map(major)

    def _tech_health_sort_key(code: str) -> tuple[int, int, int, str]:
        level, semester_bonus, course_code = _course_sort_key(code, course_map)
        return (priority_map.get(code, 999), level, semester_bonus, course_code)

    remaining = [code for code in required if code not in completed_set]
    ready: list[str] = []
    blocked: list[str] = []
    for code in remaining:
        prerequisites = prereq_map.get(code, [])
        if all(prereq in completed_set for prereq in prerequisites):
            ready.append(code)
        else:
            blocked.append(code)

    ready.sort(key=_tech_health_sort_key)
    blocked.sort(key=_tech_health_sort_key)
    recommendations = ready[:3] if ready else blocked[:3]
    return recommendations, blocked


def _build_business_program_guidance(
    major: Optional[str],
    completed: list[str],
    remaining: list[str],
) -> list[str]:
    normalized_major = _normalize(major)
    completed_set = set(completed)
    remaining_set = set(remaining)
    guidance: list[str] = []

    shared_core = {"ACCT201", "ECON201", "MGMT220", "STAT302"}
    marketing_transition = {"MKTG210"}
    entrepreneurship_ready = {"ACCT201", "ECON201", "MGMT220", "MKTG210", "STAT302"}

    if normalized_major == "Business Administration":
        if shared_core.issubset(completed_set):
            guidance.append(
                "Your shared business core is in place, so upper-level management and strategy planning is starting to make sense."
            )
        else:
            guidance.append(
                "You are still building the shared business core, so accounting, economics, statistics, and management foundations should stay ahead of upper-level strategy choices."
            )

    if normalized_major == "Marketing":
        if marketing_transition.issubset(completed_set):
            guidance.append(
                "You have the principles-level marketing foundation needed to start moving into upper-level marketing strategy work."
            )
        else:
            guidance.append(
                "Marketing students should use MKTG210 as the transition point into upper-level marketing work."
            )
        if "MKTG331" in remaining_set:
            guidance.append(
                "Once your shared business core and MKTG210 are in place, upper-level marketing should move ahead of supporting electives."
            )

    if normalized_major == "Entrepreneurship":
        if entrepreneurship_ready.issubset(completed_set):
            guidance.append(
                "You now have enough shared business context for venture-focused coursework to be useful and well-timed."
            )
        else:
            guidance.append(
                "Entrepreneurship works best after accounting, economics, management, marketing, and quantitative foundations are in place."
            )

    if normalized_major == "Accounting":
        if {"ACCT201", "ACCT202"}.issubset(completed_set):
            guidance.append(
                "You have the lower accounting sequence in place, so intermediate accounting and stronger internship planning are starting to make sense."
            )
        else:
            guidance.append(
                "Accounting should move in sequence from ACCT201 to ACCT202 before intermediate accounting work."
            )

    if normalized_major == "Finance":
        if {"ACCT201", "ECON201", "ECON202"}.issubset(completed_set):
            guidance.append(
                "Your accounting and economics foundation is in place, so finance planning can start moving toward upper-level finance coursework."
            )
        else:
            guidance.append(
                "Finance advising should stay grounded in accounting and economics first, so upper-level finance courses are not taken too early."
            )

    if normalized_major == "Hospitality Management":
        guidance.append(
            "Hospitality Management works best after the shared business core is underway, so operations and service-focused planning stays grounded in business fundamentals."
        )

    if normalized_major == "Human Resource Management":
        guidance.append(
            "Human Resource Management builds on management and organizational foundations, so lower-division business preparation should lead into upper-level people and organizational planning."
        )

    return guidance


def _build_tech_health_program_guidance(
    major: Optional[str],
    completed: list[str],
    remaining: list[str],
) -> list[str]:
    normalized_major = _normalize(major)
    completed_set = set(completed)
    guidance: list[str] = []

    if normalized_major in {"Information Systems", "Information Science"}:
        if {"INSS201", "INSS220"}.issubset(completed_set):
            guidance.append(
                "Your Information Science foundation is in place, so you can start moving toward more advanced systems, analytics, and information-flow coursework."
            )
        else:
            guidance.append(
                "Information Science should move through the early INSS sequence before upper-level systems and data-oriented planning."
            )

    if normalized_major == "Cloud Computing":
        if {"CLDC101", "CLDC220"}.issubset(completed_set):
            guidance.append(
                "Your cloud foundation is underway, so upper cloud, platform, and automation planning is starting to make sense."
            )
        else:
            guidance.append(
                "Cloud Computing should stay grounded in lower-division cloud and technical foundations before upper-level platform work."
            )

    if normalized_major == "Nursing":
        if {"NURS101", "NURS201", "NURS220"}.issubset(completed_set):
            guidance.append(
                "Your lower-division nursing progression is underway, so the next nursing step can be planned more confidently."
            )
        else:
            guidance.append(
                "Nursing should stay orderly and foundation-first so upper nursing coursework is not recommended too early."
            )

    if normalized_major == "Biology":
        if {"BIOL101", "BIOL102"}.issubset(completed_set):
            guidance.append(
                "Your introductory biology foundation is in place, so upper biology planning can begin more naturally."
            )
        else:
            guidance.append(
                "Biology should complete the intro science sequence before upper-level biology recommendations take priority."
            )

    if normalized_major == "Psychology":
        if "PSYC101" in completed_set and ("STAT302" in completed_set or "PSYC210" in completed_set):
            guidance.append(
                "Your psychology foundation is taking shape, so more advanced psychology planning is starting to make sense."
            )
        else:
            guidance.append(
                "Psychology should build through intro and methods-oriented preparation before more advanced psychology planning."
            )

    return guidance


def _cs_focus_area_to_pathway(focus_area: str) -> str:
    mapping = {
        "artificial intelligence": "AI and Data",
        "data science": "AI and Data",
        "software engineering": "Software Engineering",
        "cybersecurity": "Cybersecurity",
        "quantum security": "Cybersecurity",
        "cloud computing": "Systems and Cloud",
    }
    return mapping.get(focus_area.lower(), focus_area)


def _build_cs_focus_area_recommendations(
    completed: list[str],
    remaining: list[str],
    question_hint: Optional[str] = None,
) -> list[dict[str, object]]:
    question_tokens = _tokenize(question_hint or "")
    if not question_tokens:
        return []

    completed_set = set(completed)
    remaining_set = set(remaining)
    grouped: dict[str, dict[str, object]] = {}

    for row in load_cs_focus_area_rows():
        keyword_tokens = _tokenize((_normalize(row.get("interest_keywords"))).replace(";", " "))
        overlap = question_tokens & keyword_tokens
        if keyword_tokens and not overlap:
            continue

        focus_area = _normalize(row.get("focus_area"))
        pathway = _cs_focus_area_to_pathway(focus_area)
        related_courses = [
            canonicalize_course_code(code)
            for code in _normalize(row.get("related_courses")).split(";")
            if code.strip()
        ]
        foundational_courses = [
            canonicalize_course_code(code)
            for code in _normalize(row.get("foundational_courses")).split(";")
            if code.strip()
        ]
        missing_foundations = [code for code in foundational_courses if code not in completed_set]
        recommended_courses = [code for code in related_courses if code not in completed_set]
        if not recommended_courses:
            recommended_courses = [code for code in foundational_courses if code in remaining_set]

        current = grouped.setdefault(
            pathway,
            {
                "pathway": pathway,
                "recommended_courses": [],
                "missing_foundations": [],
                "relevant_contact": None,
                "notes": [],
                "score": 0,
            },
        )
        current["recommended_courses"].extend(recommended_courses)
        current["missing_foundations"].extend(missing_foundations)
        if not current["relevant_contact"]:
            current["relevant_contact"] = _normalize(row.get("faculty_contact")) or None
        note = _normalize(row.get("notes"))
        if note:
            current["notes"].append(note)
        current["score"] += len(overlap) or 1

    ranked = sorted(grouped.values(), key=lambda row: (-int(row["score"]), row["pathway"]))
    results: list[dict[str, object]] = []
    for row in ranked[:2]:
        results.append(
            {
                "pathway": row["pathway"],
                "recommended_courses": _unique_preserve_order(row["recommended_courses"])[:3],
                "missing_foundations": _unique_preserve_order(row["missing_foundations"])[:3],
                "relevant_contact": row["relevant_contact"],
                "notes": " ".join(_unique_preserve_order(row["notes"])) or None,
            }
        )
    return results


def _build_cs_pathway_recommendations(
    completed: list[str],
    remaining: list[str],
    question_hint: Optional[str] = None,
) -> list[dict[str, object]]:
    focus_area_recommendations = _build_cs_focus_area_recommendations(
        completed,
        remaining,
        question_hint=question_hint,
    )
    if focus_area_recommendations:
        return focus_area_recommendations

    completed_set = set(completed)
    remaining_set = set(remaining)
    question_tokens = _tokenize(question_hint or "")
    recommendations: list[dict[str, object]] = []

    for row in load_cs_pathway_rows():
        pathway = _normalize(row.get("pathway"))
        keyword_tokens = _tokenize((_normalize(row.get("interest_keywords"))).replace(";", " "))
        recommended_courses = [
            canonicalize_course_code(code)
            for code in _normalize(row.get("recommended_courses")).split(";")
            if code.strip()
        ]
        foundation_courses = [
            canonicalize_course_code(code)
            for code in _normalize(row.get("foundation_courses")).split(";")
            if code.strip()
        ]

        if question_tokens and keyword_tokens and not (question_tokens & keyword_tokens):
            continue

        missing_foundations = [code for code in foundation_courses if code not in completed_set]
        suggested_courses = [
            code for code in recommended_courses if code in remaining_set and code not in missing_foundations
        ]
        if not suggested_courses:
            suggested_courses = [code for code in foundation_courses if code in remaining_set][:2]

        recommendations.append(
            {
                "pathway": pathway,
                "recommended_courses": suggested_courses[:3],
                "missing_foundations": missing_foundations[:3],
                "relevant_contact": None,
                "notes": _normalize(row.get("notes")) or None,
            }
        )

    if recommendations:
        return recommendations[:2]

    default_rows = load_cs_pathway_rows()[:2]
    for row in default_rows:
        pathway = _normalize(row.get("pathway"))
        recommended_courses = [
            canonicalize_course_code(code)
            for code in _normalize(row.get("recommended_courses")).split(";")
            if code.strip()
        ]
        foundation_courses = [
            canonicalize_course_code(code)
            for code in _normalize(row.get("foundation_courses")).split(";")
            if code.strip()
        ]
        recommendations.append(
            {
                "pathway": pathway,
                "recommended_courses": [code for code in recommended_courses if code in remaining_set][:3],
                "missing_foundations": [code for code in foundation_courses if code not in completed_set][:3],
                "relevant_contact": None,
                "notes": _normalize(row.get("notes")) or None,
            }
        )
    return recommendations


def _build_cs_capstone_readiness(completed: list[str]) -> dict[str, object]:
    completed_set = set(completed)
    rule_map = {
        _normalize(row.get("status")).lower(): row
        for row in load_cs_capstone_rule_rows()
        if _normalize(row.get("status"))
    }

    ready_row = rule_map.get("ready")
    nearly_ready_row = rule_map.get("nearly_ready")
    not_ready_row = rule_map.get("not_ready")

    def _missing_from(row: Optional[dict[str, str]]) -> list[str]:
        if not row:
            return []
        return [
            canonicalize_course_code(code)
            for code in _normalize(row.get("required_courses")).split(";")
            if code.strip() and canonicalize_course_code(code) not in completed_set
        ]

    ready_missing = _missing_from(ready_row)
    if not ready_missing:
        return {
            "status": "ready",
            "missing_foundations": [],
            "notes": _normalize((ready_row or {}).get("notes")) or None,
        }

    nearly_ready_missing = _missing_from(nearly_ready_row)
    if len(nearly_ready_missing) <= 1:
        return {
            "status": "nearly_ready",
            "missing_foundations": nearly_ready_missing,
            "notes": _normalize((nearly_ready_row or {}).get("notes")) or None,
        }

    return {
        "status": "not_ready",
        "missing_foundations": _missing_from(not_ready_row),
        "notes": _normalize((not_ready_row or {}).get("notes")) or None,
    }


def get_computer_science_audit_summary(
    completed_codes: list[str],
    in_progress_codes: list[str],
    remaining_codes: list[str],
    planning_interest: Optional[str] = None,
) -> dict[str, object]:
    from .cs_audit import interpret_computer_science_audit

    return interpret_computer_science_audit(
        completed_codes=completed_codes,
        in_progress_codes=in_progress_codes,
        remaining_codes=remaining_codes,
        planning_interest=planning_interest,
    )



def get_degree_progress(
    major: Optional[str],
    completed_course_codes: Iterable[str],
    planning_interest: Optional[str] = None,
) -> dict[str, object]:
    completed = _apply_implied_completed_courses(major, completed_course_codes)
    if not major:
        return {
            "major": None,
            "required_courses": [],
            "completed_courses": completed,
            "remaining_courses": [],
            "recommended_next_courses": [],
            "blocked_courses": [],
            "program_guidance": [],
            "pathway_recommendations": [],
            "capstone_readiness": {"status": "unknown", "missing_foundations": [], "notes": None},
            "cs_audit_summary": None,
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
            "program_guidance": [],
            "pathway_recommendations": [],
            "capstone_readiness": {"status": "unknown", "missing_foundations": [], "notes": None},
            "cs_audit_summary": None,
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
    if _is_business_depth_major(canonical_major):
        recommended_next_courses, blocked_courses = _recommend_business_next_courses(
            canonical_major,
            required,
            completed,
        )
    elif _is_tech_health_depth_major(canonical_major):
        recommended_next_courses, blocked_courses = _recommend_tech_health_next_courses(
            canonical_major,
            required,
            completed,
        )
    else:
        recommended_next_courses, blocked_courses = _recommend_next_courses(required, completed)
    completion_percent = round((len(required) - len(remaining)) / len(required) * 100, 1) if required else 0.0
    program_guidance: list[str] = []
    pathway_recommendations: list[dict[str, object]] = []
    capstone_readiness = {"status": "unknown", "missing_foundations": [], "notes": None}
    cs_audit_summary = None

    if _is_business_depth_major(canonical_major):
        program_guidance = _build_business_program_guidance(
            canonical_major,
            completed,
            remaining,
        )
    elif _is_tech_health_depth_major(canonical_major):
        program_guidance = _build_tech_health_program_guidance(
            canonical_major,
            completed,
            remaining,
        )

    if _is_computer_science_major(canonical_major):
        pathway_recommendations = _build_cs_pathway_recommendations(
            completed,
            remaining,
            question_hint=planning_interest,
        )
        capstone_readiness = _build_cs_capstone_readiness(completed)
        cs_audit_summary = get_computer_science_audit_summary(
            completed_codes=completed,
            in_progress_codes=[],
            remaining_codes=remaining,
            planning_interest=planning_interest,
        )

    return {
        "major": _normalize(matching_row.get("major")) or major,
        "required_courses": required,
        "completed_courses": completed,
        "remaining_courses": remaining,
        "recommended_next_courses": recommended_next_courses,
        "blocked_courses": blocked_courses,
        "program_guidance": program_guidance,
        "pathway_recommendations": pathway_recommendations,
        "capstone_readiness": capstone_readiness,
        "cs_audit_summary": cs_audit_summary,
        "completion_percent": completion_percent,
        "notes": _normalize(matching_row.get("notes")) or None,
        "advising_tips": _normalize(matching_row.get("advising_tips")) or None,
    }


