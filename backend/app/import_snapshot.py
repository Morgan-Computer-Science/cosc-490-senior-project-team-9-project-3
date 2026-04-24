import json
from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas


def load_saved_import_preview(user: models.User) -> schemas.CompletedCoursesImportPreview | None:
    snapshot = getattr(user, "import_snapshot", None)
    if not snapshot or not snapshot.payload_json:
        return None

    try:
        payload = json.loads(snapshot.payload_json)
        return schemas.CompletedCoursesImportPreview.model_validate(payload)
    except Exception:
        return None


def save_import_preview(
    db: Session,
    user: models.User,
    preview: schemas.CompletedCoursesImportPreview | None,
) -> None:
    existing = getattr(user, "import_snapshot", None)
    if preview is None:
        if existing:
            db.delete(existing)
        return

    payload_json = json.dumps(preview.model_dump(mode="json"))
    if existing:
        existing.payload_json = payload_json
        db.add(existing)
        return

    db.add(
        models.UserImportSnapshot(
            user_id=user.id,
            payload_json=payload_json,
        )
    )


def merge_degree_progress_with_import_preview(
    base_summary: dict[str, object],
    preview: schemas.CompletedCoursesImportPreview | None,
) -> dict[str, object]:
    if not preview:
        return base_summary

    completed = list(preview.completed_course_codes or [])
    in_progress = list(preview.planned_course_codes or [])
    remaining = list(preview.remaining_course_codes or [])

    effective_done = {*(code for code in completed), *(code for code in in_progress)}
    total_recognized = {*(code for code in effective_done), *(code for code in remaining)}
    completion_percent = (
        round((len(effective_done) / len(total_recognized)) * 100, 1)
        if total_recognized
        else float(base_summary.get("completion_percent", 0.0) or 0.0)
    )

    capstone_status = preview.cs_audit_summary.capstone_readiness.status if preview.cs_audit_summary else None
    blocked_courses = list(base_summary.get("blocked_courses", []))
    if capstone_status == "in_progress":
        blocked_courses = [code for code in blocked_courses if code != "COSC490"]

    merged = dict(base_summary)
    merged["completed_courses"] = sorted(effective_done)
    merged["remaining_courses"] = remaining or list(base_summary.get("remaining_courses", []))
    merged["recommended_next_courses"] = remaining[:4] or list(base_summary.get("recommended_next_courses", []))
    merged["blocked_courses"] = blocked_courses
    merged["completion_percent"] = completion_percent

    if preview.cs_audit_summary:
        merged["cs_audit_summary"] = preview.cs_audit_summary.model_dump()
        merged["capstone_readiness"] = preview.cs_audit_summary.capstone_readiness.model_dump()

    notes = merged.get("notes") or ""
    summary_note = preview.summary or ""
    confidence_note = preview.confidence_note or ""
    note_parts = [part for part in [notes, summary_note, confidence_note] if part]
    if note_parts:
        merged["notes"] = " ".join(dict.fromkeys(note_parts))

    return merged


def build_saved_import_summary_context(
    preview: schemas.CompletedCoursesImportPreview | None,
) -> str:
    if not preview:
        return ""

    lines = ["Saved degree-progress import context:"]
    if preview.transcript_summary:
        if preview.transcript_summary.gpa:
            lines.append(f"- GPA shown in the uploaded document: {preview.transcript_summary.gpa}")
        if preview.transcript_summary.earned_credits:
            lines.append(f"- Earned credits shown in the uploaded document: {preview.transcript_summary.earned_credits}")
        if preview.transcript_summary.standing:
            lines.append(f"- Standing shown in the uploaded document: {preview.transcript_summary.standing}")
    if preview.completed_course_codes:
        lines.append(f"- Imported completed courses: {', '.join(preview.completed_course_codes)}")
    if preview.planned_course_codes:
        lines.append(f"- Imported in-progress or planned courses: {', '.join(preview.planned_course_codes)}")
    if preview.remaining_course_codes:
        lines.append(f"- Imported remaining or needed courses: {', '.join(preview.remaining_course_codes)}")
    if preview.summary:
        lines.append(f"- Import summary: {preview.summary}")
    return "\n".join(lines)


def answer_from_saved_import_summary(
    question: str,
    preview: schemas.CompletedCoursesImportPreview | None,
) -> Optional[str]:
    if not preview or not preview.transcript_summary:
        return None

    lowered = (question or "").lower()
    summary = preview.transcript_summary
    if "gpa" in lowered and summary.gpa:
        return f"Your uploaded document shows a GPA of {summary.gpa}."
    if ("earned credit" in lowered or "earned credits" in lowered) and summary.earned_credits:
        return f"Your uploaded document shows {summary.earned_credits} earned credits."
    if "standing" in lowered and summary.standing:
        return f"Your uploaded document lists your standing as {summary.standing}."
    return None
