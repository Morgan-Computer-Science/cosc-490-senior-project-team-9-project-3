import csv
from functools import lru_cache
from pathlib import Path
from typing import Optional

from .rag import (
    _build_cs_capstone_readiness,
    _cs_focus_area_to_pathway,
    _normalize,
    _tokenize,
    canonicalize_course_code,
    load_cs_focus_area_rows,
    load_cs_pathway_rows,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CS_AUDIT_BUCKETS_PATH = DATA_DIR / "cs_audit_buckets.csv"


@lru_cache(maxsize=1)
def load_cs_audit_bucket_rows() -> tuple[dict[str, str], ...]:
    if not CS_AUDIT_BUCKETS_PATH.exists():
        return tuple()

    with CS_AUDIT_BUCKETS_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_cs_audit_bucket_map() -> dict[str, dict[str, str]]:
    bucket_map: dict[str, dict[str, str]] = {}
    for row in load_cs_audit_bucket_rows():
        course_code = canonicalize_course_code(row.get("course_code"))
        if course_code:
            bucket_map[course_code] = row
    return bucket_map


def _empty_bucket() -> dict[str, list[str]]:
    return {"completed": [], "in_progress": [], "remaining": []}


def _append_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)

def _bucket_role_matches_pathway(pathway: str, role: str) -> bool:
    lowered_pathway = pathway.lower()
    lowered_role = role.lower()
    if lowered_pathway == "ai and data":
        return "ai_data" in lowered_role or "data" in lowered_role
    if lowered_pathway == "cybersecurity":
        return "cybersecurity" in lowered_role or "security" in lowered_role
    if lowered_pathway == "systems and cloud":
        return "cloud" in lowered_role or "systems" in lowered_role
    if lowered_pathway == "software engineering":
        return "software" in lowered_role
    return False


def _classify_cs_courses(
    bucket_map: dict[str, dict[str, str]],
    completed_codes: list[str],
    in_progress_codes: list[str],
    remaining_codes: list[str],
) -> tuple[dict[str, object], list[str], list[str], list[str]]:
    summary = {
        "foundations": _empty_bucket(),
        "core_progress": _empty_bucket(),
        "math_support": _empty_bucket(),
        "upper_level_progress": _empty_bucket(),
    }
    aligned_upper_level: list[str] = []
    unmapped_courses: list[str] = []
    all_known_courses: list[str] = []

    for status_name, codes in {
        "completed": completed_codes,
        "in_progress": in_progress_codes,
        "remaining": remaining_codes,
    }.items():
        for raw_code in codes:
            code = canonicalize_course_code(raw_code)
            row = bucket_map.get(code)
            if not row:
                if code.startswith("COSC"):
                    _append_unique(unmapped_courses, code)
                continue

            bucket = _normalize(row.get("bucket"))
            if bucket == "foundation":
                _append_unique(summary["foundations"][status_name], code)
            elif bucket == "core":
                _append_unique(summary["core_progress"][status_name], code)
            elif bucket == "math_support":
                _append_unique(summary["math_support"][status_name], code)
            elif bucket in {"upper_level", "capstone"}:
                _append_unique(summary["upper_level_progress"][status_name], code)
                if status_name in {"completed", "in_progress"}:
                    _append_unique(aligned_upper_level, code)
            _append_unique(all_known_courses, code)

    return summary, aligned_upper_level, unmapped_courses, all_known_courses


def _build_cs_capstone_readiness_with_in_progress(
    completed_codes: list[str],
    in_progress_codes: list[str],
) -> dict[str, object]:
    normalized_in_progress = {canonicalize_course_code(code) for code in in_progress_codes}
    if "COSC490" in normalized_in_progress:
        return {
            "status": "in_progress",
            "missing_foundations": [],
            "notes": "Your record shows COSC490 is already underway, so capstone appears to be in progress.",
        }

    completed_ready = _build_cs_capstone_readiness(completed_codes)
    if completed_ready["status"] == "ready":
        return completed_ready

    combined_codes = sorted({*completed_codes, *in_progress_codes})
    combined_ready = _build_cs_capstone_readiness(combined_codes)
    if combined_ready["status"] == "ready":
        return {
            "status": "nearly_ready",
            "missing_foundations": [],
            "notes": "You look close to capstone readiness if your in-progress Computer Science core work finishes successfully.",
        }

    if completed_ready["status"] == "not_ready" and combined_ready["status"] == "nearly_ready":
        return {
            "status": "nearly_ready",
            "missing_foundations": combined_ready["missing_foundations"],
            "notes": combined_ready.get("notes")
            or "You are getting closer to capstone readiness, but some Computer Science core work is still missing.",
        }

    return completed_ready


def _infer_cs_pathway_direction(
    *,
    completed_codes: list[str],
    in_progress_codes: list[str],
    remaining_codes: list[str],
    planning_interest: Optional[str],
) -> dict[str, object]:
    interest_tokens = _tokenize(planning_interest or "")
    present_codes = {canonicalize_course_code(code) for code in [*completed_codes, *in_progress_codes]}
    remaining_set = {canonicalize_course_code(code) for code in remaining_codes}

    scored_pathways: list[dict[str, object]] = []
    grouped_notes: dict[str, list[str]] = {}

    for row in load_cs_focus_area_rows():
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
        keyword_tokens = _tokenize((_normalize(row.get("interest_keywords"))).replace(";", " "))
        overlap = interest_tokens & keyword_tokens
        aligned_courses = [code for code in related_courses if code in present_codes]
        ready_next_courses = [code for code in related_courses if code in remaining_set]
        score = len(aligned_courses) * 3 + len(overlap) * 4 + len(ready_next_courses)
        if score == 0:
            continue
        scored_pathways.append(
            {
                "pathway": pathway,
                "aligned_courses": aligned_courses or ready_next_courses,
                "score": score,
                "note": _normalize(row.get("notes")) or None,
                "missing_foundations": [code for code in foundational_courses if code not in present_codes],
            }
        )
        note = _normalize(row.get("notes"))
        if note:
            grouped_notes.setdefault(pathway, []).append(note)

    if not scored_pathways:
        for row in load_cs_pathway_rows():
            pathway = _normalize(row.get("pathway"))
            keyword_tokens = _tokenize((_normalize(row.get("interest_keywords"))).replace(";", " "))
            recommended_courses = [
                canonicalize_course_code(code)
                for code in _normalize(row.get("recommended_courses")).split(";")
                if code.strip()
            ]
            aligned_courses = [code for code in recommended_courses if code in present_codes]
            ready_next_courses = [code for code in recommended_courses if code in remaining_set]
            score = len(aligned_courses) * 2 + len(interest_tokens & keyword_tokens) * 3 + len(ready_next_courses)
            if score == 0:
                continue
            scored_pathways.append(
                {
                    "pathway": pathway,
                    "aligned_courses": aligned_courses or ready_next_courses,
                    "score": score,
                    "note": _normalize(row.get("notes")) or None,
                    "missing_foundations": [],
                }
            )

    if not scored_pathways:
        return {"primary_pathway": None, "aligned_courses": [], "notes": None}

    scored_pathways.sort(key=lambda item: (-int(item["score"]), item["pathway"]))
    best = scored_pathways[0]
    notes = grouped_notes.get(best["pathway"], [])
    note_text = " ".join(dict.fromkeys([*(notes or []), best.get("note") or ""]).keys()).strip()
    if not note_text and best.get("missing_foundations"):
        note_text = (
            "Missing foundations before this direction becomes stronger: "
            + ", ".join(best["missing_foundations"][:3])
        )

    return {
        "primary_pathway": best["pathway"],
        "aligned_courses": best["aligned_courses"][:4],
        "notes": note_text or None,
    }


def interpret_computer_science_audit(
    *,
    completed_codes: list[str],
    in_progress_codes: list[str],
    remaining_codes: list[str],
    planning_interest: Optional[str],
) -> dict[str, object]:
    normalized_completed = [canonicalize_course_code(code) for code in completed_codes if _normalize(code)]
    normalized_in_progress = [canonicalize_course_code(code) for code in in_progress_codes if _normalize(code)]
    normalized_remaining = [canonicalize_course_code(code) for code in remaining_codes if _normalize(code)]

    bucket_map = load_cs_audit_bucket_map()
    summary, aligned_upper_level, unmapped_courses, _ = _classify_cs_courses(
        bucket_map,
        normalized_completed,
        normalized_in_progress,
        normalized_remaining,
    )
    capstone_readiness = _build_cs_capstone_readiness_with_in_progress(
        normalized_completed,
        normalized_in_progress,
    )
    pathway_direction = _infer_cs_pathway_direction(
        completed_codes=normalized_completed,
        in_progress_codes=normalized_in_progress,
        remaining_codes=normalized_remaining,
        planning_interest=planning_interest,
    )
    if pathway_direction["primary_pathway"]:
        role_aligned_courses: list[str] = []
        for code in [*normalized_completed, *normalized_in_progress]:
            row = bucket_map.get(code)
            if not row:
                continue
            if _bucket_role_matches_pathway(pathway_direction["primary_pathway"], _normalize(row.get("role"))):
                _append_unique(role_aligned_courses, code)
        pathway_direction["aligned_courses"] = [
            *role_aligned_courses,
            *[code for code in pathway_direction["aligned_courses"] if code not in role_aligned_courses],
        ][:4]

    if not pathway_direction["aligned_courses"]:
        pathway_direction["aligned_courses"] = aligned_upper_level[:4]

    summary_lines: list[str] = []
    if summary["foundations"]["remaining"]:
        summary_lines.append(
            "You still have early Computer Science foundations left before the strongest upper-level progression opens up."
        )
    elif summary["foundations"]["completed"]:
        summary_lines.append(
            "Your early Computer Science programming foundations look substantially in place."
        )

    if summary["core_progress"]["remaining"]:
        summary_lines.append(
            "You still have core Computer Science sequence work remaining before the degree path is fully on track for capstone timing."
        )

    if capstone_readiness["status"] == "not_ready":
        summary_lines.append(
            "COSC490 still looks early based on the current Computer Science core record."
        )
    elif capstone_readiness["status"] == "nearly_ready":
        summary_lines.append(
            "You appear close to capstone readiness, but the remaining core gaps still matter."
        )
    elif capstone_readiness["status"] == "in_progress":
        summary_lines.append(
            "Your record shows COSC490 is already underway, so capstone appears to be in progress."
        )
    elif capstone_readiness["status"] == "ready":
        summary_lines.append(
            "Your current Computer Science record looks consistent with capstone readiness."
        )

    if pathway_direction["primary_pathway"]:
        summary_lines.append(
            f"Your current Computer Science coursework is leaning toward {pathway_direction['primary_pathway']}."
        )

    if unmapped_courses:
        summary_lines.append(
            "Some Computer Science-coded courses still need advisor confirmation in the current dataset."
        )

    return {
        **summary,
        "capstone_readiness": capstone_readiness,
        "pathway_direction": pathway_direction,
        "unmapped_courses": unmapped_courses,
        "summary_lines": summary_lines,
    }

