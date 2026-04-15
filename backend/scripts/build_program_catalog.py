from __future__ import annotations

import csv
import io
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
PROGRAMS_PATH = DATA_DIR / "programs.csv"
DEPARTMENTS_PATH = DATA_DIR / "departments.csv"
PROGRAM_SOURCE_URL = "https://www.morgan.edu/academics/undergraduate-studies/undergraduate-programs"

DEPARTMENT_OVERRIDES = {
    "Actuarial Science": {
        "office": "Key Hall 165",
        "email": "actuarialscience@morgan.edu",
        "phone": "443-885-1393",
        "overview": (
            "Actuarial Science advises students on probability, statistics, risk modeling, "
            "finance-aligned preparation, and Society of Actuaries exam readiness."
        ),
        "source_url": "https://www.morgan.edu/actuarial-science/prospective-students/degree-options",
    },
}


PROGRAM_SPECS = [
    {
        "major": "Accounting",
        "canonical_major": "Accounting",
        "degree_type": "BS",
        "department": "Department of Accounting & Finance",
        "school": "Business & Management",
        "aliases": "",
    },
    {
        "major": "Actuarial Science",
        "canonical_major": "Actuarial Science",
        "degree_type": "BS",
        "department": "Actuarial Science Program",
        "school": "Computer, Math, & Natural Sciences",
        "aliases": "",
    },
    {
        "major": "Applied Liberal Studies",
        "canonical_major": "Applied Liberal Studies",
        "degree_type": "BS",
        "department": "Applied Liberal Studies Program",
        "school": "Interdisciplinary & Continuing Studies",
        "aliases": "",
    },
    {
        "major": "Architecture and Environmental Design",
        "canonical_major": "Architecture",
        "degree_type": "BS",
        "department": "Department of Undergraduate Design",
        "school": "Architecture & Planning",
        "aliases": "Architecture",
    },
    {
        "major": "Biology",
        "canonical_major": "Biology",
        "degree_type": "BS",
        "department": "Department of Biology",
        "school": "Computer, Math, & Natural Sciences",
        "aliases": "",
    },
    {
        "major": "Chemistry",
        "canonical_major": "Chemistry",
        "degree_type": "BS",
        "department": "Department of Chemistry",
        "school": "Computer, Math, & Natural Sciences",
        "aliases": "",
    },
    {
        "major": "Civil Engineering",
        "canonical_major": "Civil Engineering",
        "degree_type": "BS",
        "department": "Department of Civil Engineering",
        "school": "Engineering",
        "aliases": "",
    },
    {
        "major": "Cloud Computing",
        "canonical_major": "Cloud Computing",
        "degree_type": "BS",
        "department": "Department of Computer Science",
        "school": "Computer, Math, & Natural Sciences",
        "aliases": "",
    },
    {
        "major": "Coastal Science and Policy",
        "canonical_major": "Coastal Science and Policy",
        "degree_type": "BS",
        "department": "Climate Science Division",
        "school": "Computer, Math, & Natural Sciences",
        "aliases": "",
    },
    {
        "major": "Computer Science",
        "canonical_major": "Computer Science",
        "degree_type": "BS",
        "department": "Department of Computer Science",
        "school": "Computer, Math, & Natural Sciences",
        "aliases": "",
    },
    {
        "major": "Construction Management",
        "canonical_major": "Construction Management",
        "degree_type": "BS",
        "department": "Department of Construction Management",
        "school": "Architecture & Planning",
        "aliases": "",
    },
    {
        "major": "Cybersecurity Intelligence Management",
        "canonical_major": "Cybersecurity Intelligence Management",
        "degree_type": "BS",
        "department": "",
        "school": "",
        "aliases": "",
    },
    {
        "major": "Economics",
        "canonical_major": "Economics",
        "degree_type": "BS / BA",
        "department": "Department of Economics",
        "school": "Liberal Arts",
        "aliases": "",
    },
    {
        "major": "Electrical and Computer Engineering",
        "canonical_major": "Electrical Engineering",
        "degree_type": "BS",
        "department": "Department of Electrical & Computer Engineering",
        "school": "Engineering",
        "aliases": "Electrical Engineering",
    },
    {
        "major": "Elementary Education",
        "canonical_major": "Elementary Education",
        "degree_type": "BS",
        "department": "Teacher Education and Professional Development",
        "school": "Education & Urban Studies",
        "aliases": "",
    },
    {
        "major": "English",
        "canonical_major": "English",
        "degree_type": "BA",
        "department": "Department of English and Language Arts",
        "school": "Liberal Arts",
        "aliases": "",
    },
    {
        "major": "Engineering Physics",
        "canonical_major": "Engineering Physics",
        "degree_type": "BS",
        "department": "Department of Physics & Engineering Physics",
        "school": "Computer, Math, & Natural Sciences",
        "aliases": "",
    },
    {
        "major": "Entrepreneurship",
        "canonical_major": "Entrepreneurship",
        "degree_type": "BS",
        "department": "Department of Business Administration",
        "school": "Business & Management",
        "aliases": "",
    },
    {
        "major": "Family Consumer Sciences",
        "canonical_major": "Family Consumer Sciences",
        "degree_type": "BS",
        "department": "Department of Family & Consumer Sciences",
        "school": "Community Health & Policy",
        "aliases": "",
    },
    {
        "major": "Finance",
        "canonical_major": "Finance",
        "degree_type": "BS",
        "department": "Department of Accounting & Finance",
        "school": "Business & Management",
        "aliases": "",
    },
    {
        "major": "Fine Arts",
        "canonical_major": "Fine Arts",
        "degree_type": "BA",
        "department": "Department of Fine & Performing Arts",
        "school": "Liberal Arts",
        "aliases": "",
    },
    {
        "major": "Health Education",
        "canonical_major": "Health Education",
        "degree_type": "BS",
        "department": "Health Education Program",
        "school": "Community Health & Policy",
        "aliases": "",
    },
    {
        "major": "History",
        "canonical_major": "History",
        "degree_type": "BA",
        "department": "Department of History, Geography, and Museum Studies",
        "school": "Liberal Arts",
        "aliases": "",
    },
    {
        "major": "Hospitality Management",
        "canonical_major": "Hospitality Management",
        "degree_type": "BS",
        "department": "Department of Business Administration",
        "school": "Business & Management",
        "aliases": "",
    },
    {
        "major": "Human Resource Management",
        "canonical_major": "Human Resource Management",
        "degree_type": "BS",
        "department": "Department of Business Administration",
        "school": "Business & Management",
        "aliases": "",
    },
    {
        "major": "Industrial Engineering",
        "canonical_major": "Industrial Engineering",
        "degree_type": "BS",
        "department": "Department of Industrial & Systems Engineering",
        "school": "Engineering",
        "aliases": "",
    },
    {
        "major": "Information Systems",
        "canonical_major": "Information Systems",
        "degree_type": "BS",
        "department": "Department of Information Science & Systems",
        "school": "Business & Management",
        "aliases": "",
    },
    {
        "major": "Interdisciplinary Educational Studies",
        "canonical_major": "Interdisciplinary Educational Studies",
        "degree_type": "BS",
        "department": "College of Interdisciplinary & Continuing Studies",
        "school": "Interdisciplinary & Continuing Studies",
        "aliases": "",
    },
    {
        "major": "Interdisciplinary Engineering, Information, and Computational Sciences",
        "canonical_major": "Interdisciplinary Engineering, Information, and Computational Sciences",
        "degree_type": "BS",
        "department": "College of Interdisciplinary & Continuing Studies",
        "school": "Interdisciplinary & Continuing Studies",
        "aliases": "",
    },
    {
        "major": "Interdisciplinary Global Perspectives & Practices",
        "canonical_major": "Interdisciplinary Global Perspectives & Practices",
        "degree_type": "BS",
        "department": "College of Interdisciplinary & Continuing Studies",
        "school": "Interdisciplinary & Continuing Studies",
        "aliases": "",
    },
    {
        "major": "Interdisciplinary Health and Human Sciences",
        "canonical_major": "Interdisciplinary Health and Human Sciences",
        "degree_type": "BS",
        "department": "College of Interdisciplinary & Continuing Studies",
        "school": "Interdisciplinary & Continuing Studies",
        "aliases": "",
    },
    {
        "major": "Interdisciplinary Organizational Administration",
        "canonical_major": "Interdisciplinary Organizational Administration",
        "degree_type": "BS",
        "department": "College of Interdisciplinary & Continuing Studies",
        "school": "Interdisciplinary & Continuing Studies",
        "aliases": "",
    },
    {
        "major": "Interdisciplinary Sciences",
        "canonical_major": "Interdisciplinary Sciences",
        "degree_type": "BS",
        "department": "College of Interdisciplinary & Continuing Studies",
        "school": "Interdisciplinary & Continuing Studies",
        "aliases": "",
    },
    {
        "major": "Interdisciplinary Studies in Societal Equity & Urbanism",
        "canonical_major": "Interdisciplinary Studies in Societal Equity & Urbanism",
        "degree_type": "BS",
        "department": "College of Interdisciplinary & Continuing Studies",
        "school": "Interdisciplinary & Continuing Studies",
        "aliases": "",
    },
    {
        "major": "Interdisciplinary Technology Services",
        "canonical_major": "Interdisciplinary Technology Services",
        "degree_type": "BS",
        "department": "College of Interdisciplinary & Continuing Studies",
        "school": "Interdisciplinary & Continuing Studies",
        "aliases": "",
    },
    {
        "major": "Interior Design",
        "canonical_major": "Interior Design",
        "degree_type": "BS",
        "department": "Department of Undergraduate Design",
        "school": "Architecture & Planning",
        "aliases": "",
    },
    {
        "major": "Management and Business Administration",
        "canonical_major": "Business Administration",
        "degree_type": "BS",
        "department": "Department of Business Administration",
        "school": "Business & Management",
        "aliases": "Business Administration",
    },
    {
        "major": "Marketing",
        "canonical_major": "Marketing",
        "degree_type": "BS",
        "department": "Department of Business Administration",
        "school": "Business & Management",
        "aliases": "",
    },
    {
        "major": "Mathematics",
        "canonical_major": "Mathematics",
        "degree_type": "BS",
        "department": "Department of Mathematics",
        "school": "Computer, Math, & Natural Sciences",
        "aliases": "",
    },
    {
        "major": "Mechatronics Engineering",
        "canonical_major": "Mechatronics Engineering",
        "degree_type": "BS",
        "department": "Department of Mechatronics Engineering",
        "school": "Engineering",
        "aliases": "",
    },
    {
        "major": "Medical Laboratory Science",
        "canonical_major": "Medical Laboratory Science",
        "degree_type": "BS",
        "department": "Medical Laboratory Science Program",
        "school": "Community Health & Policy",
        "aliases": "",
    },
    {
        "major": "Military Science",
        "canonical_major": "Military Science",
        "degree_type": "Program",
        "department": "Department of Military Science",
        "school": "",
        "aliases": "",
    },
    {
        "major": "Multimedia Journalism",
        "canonical_major": "Multimedia Journalism",
        "degree_type": "BS",
        "department": "Department of Multimedia Journalism",
        "school": "Global Journalism & Communication",
        "aliases": "",
    },
    {
        "major": "Multiplatform Production",
        "canonical_major": "Multiplatform Production",
        "degree_type": "BS",
        "department": "Department of Multiplatform Production",
        "school": "Global Journalism & Communication",
        "aliases": "",
    },
    {
        "major": "Music",
        "canonical_major": "Music",
        "degree_type": "BA",
        "department": "Department of Fine & Performing Arts",
        "school": "Liberal Arts",
        "aliases": "",
    },
    {
        "major": "Musical Theatre",
        "canonical_major": "Musical Theatre",
        "degree_type": "BFA",
        "department": "Department of Fine & Performing Arts",
        "school": "Liberal Arts",
        "aliases": "",
    },
    {
        "major": "Nursing",
        "canonical_major": "Nursing",
        "degree_type": "BS",
        "department": "Department of Nursing",
        "school": "Community Health & Policy",
        "aliases": "",
    },
    {
        "major": "Nutritional Sciences",
        "canonical_major": "Nutritional Sciences",
        "degree_type": "BS",
        "department": "Nutritional Sciences Program",
        "school": "Community Health & Policy",
        "aliases": "",
    },
    {
        "major": "Philosophy",
        "canonical_major": "Philosophy",
        "degree_type": "BA",
        "department": "Department of Philosophy & Religious Studies",
        "school": "Liberal Arts",
        "aliases": "",
    },
    {
        "major": "Physics",
        "canonical_major": "Physics",
        "degree_type": "BS",
        "department": "Department of Physics & Engineering Physics",
        "school": "Computer, Math, & Natural Sciences",
        "aliases": "",
    },
    {
        "major": "Political Science",
        "canonical_major": "Political Science",
        "degree_type": "BA",
        "department": "Department of Political Science",
        "school": "Liberal Arts",
        "aliases": "",
    },
    {
        "major": "Psychology",
        "canonical_major": "Psychology",
        "degree_type": "BS",
        "department": "Department of Psychology",
        "school": "Liberal Arts",
        "aliases": "",
    },
    {
        "major": "Screenwriting & Animation",
        "canonical_major": "Screenwriting & Animation",
        "degree_type": "BA / BFA",
        "department": "SWAN Program",
        "school": "Global Journalism & Communication",
        "aliases": "Screenwriting and Animation",
    },
    {
        "major": "Services and Supply Chain Management",
        "canonical_major": "Services and Supply Chain Management",
        "degree_type": "BS",
        "department": "Department of Information Science & Systems",
        "school": "Business & Management",
        "aliases": "",
    },
    {
        "major": "Social Work",
        "canonical_major": "Social Work",
        "degree_type": "BSW",
        "department": "School of Social Work",
        "school": "Social Work",
        "aliases": "",
    },
    {
        "major": "Sociology",
        "canonical_major": "Sociology",
        "degree_type": "BA",
        "department": "Department of Sociology & Anthropology",
        "school": "Liberal Arts",
        "aliases": "",
    },
    {
        "major": "Sports Administration and Movement Education",
        "canonical_major": "Sports Administration and Movement Education",
        "degree_type": "BS",
        "department": "School of Education and Urban Studies",
        "school": "Education & Urban Studies",
        "aliases": "",
    },
    {
        "major": "Strategic Communication",
        "canonical_major": "Strategic Communication",
        "degree_type": "BS",
        "department": "Department of Strategic Communication",
        "school": "Global Journalism & Communication",
        "aliases": "",
    },
    {
        "major": "Theater Arts",
        "canonical_major": "Theater Arts",
        "degree_type": "BA",
        "department": "Department of Fine & Performing Arts",
        "school": "Liberal Arts",
        "aliases": "Theatre Arts",
    },
    {
        "major": "Transportation Systems",
        "canonical_major": "Transportation Systems",
        "degree_type": "BS",
        "department": "Department of Transportation & Urban Infrastructure Studies",
        "school": "Engineering",
        "aliases": "",
    },
    {
        "major": "Transportation Systems Engineering",
        "canonical_major": "Transportation Systems Engineering",
        "degree_type": "BS",
        "department": "Department of Transportation & Urban Infrastructure Studies",
        "school": "Engineering",
        "aliases": "",
    },
]


def _normalize(value: str) -> str:
    return value.strip()


def _normalize_lookup_key(value: str) -> str:
    normalized = _normalize(value).lower()
    for prefix in ("department of ", "school of ", "college of "):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    return normalized.replace("&", "and")


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _read_committed_csv_rows(relative_repo_path: str) -> list[dict[str, str]]:
    try:
        result = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={REPO_ROOT.as_posix()}",
                "show",
                f"HEAD:{relative_repo_path}",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

    return list(csv.DictReader(io.StringIO(result.stdout)))


def build_program_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for spec in PROGRAM_SPECS:
        department = _normalize(spec["department"])
        major = _normalize(spec["major"])
        rows.append(
            {
                "major": major,
                "canonical_major": _normalize(spec["canonical_major"]) or major,
                "degree_type": _normalize(spec["degree_type"]),
                "department": department,
                "school": _normalize(spec["school"]),
                "aliases": _normalize(spec["aliases"]),
                "source_url": PROGRAM_SOURCE_URL,
                "notes": (
                    "Official undergraduate program listed by Morgan State University. "
                    + (
                        f"This program is currently grouped under {department}. "
                        if department
                        else "The undergraduate program index does not show a department link for this program. "
                    )
                ).strip(),
            }
        )
    rows.sort(key=lambda row: row["major"])
    return rows


def build_department_rows(program_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    existing_rows = _read_committed_csv_rows("backend/data/departments.csv")
    if not existing_rows:
        existing_rows = _read_csv_rows(DEPARTMENTS_PATH)

    existing_index: dict[tuple[str, str], dict[str, str]] = {}
    existing_by_major: dict[str, dict[str, str]] = {}
    for row in existing_rows:
        department = _normalize_lookup_key(row.get("department", ""))
        major = _normalize(row.get("major", "")).lower()
        if department and major:
            existing_index[(department, major)] = row
            existing_by_major[major] = row

    department_rows: list[dict[str, str]] = []
    for program in program_rows:
        department = _normalize(program.get("department", ""))
        canonical_major = _normalize(program.get("canonical_major", ""))
        if not department or not canonical_major:
            continue

        existing = existing_index.get(
            (_normalize_lookup_key(department), canonical_major.lower()),
            existing_by_major.get(canonical_major.lower(), {}),
        )
        overview = _normalize(existing.get("overview", ""))
        if not overview:
            overview = (
                f"Official Morgan undergraduate program mapping for {canonical_major}. "
                f"This program is associated with {department}."
            )
        override = DEPARTMENT_OVERRIDES.get(canonical_major, {})

        department_rows.append(
            {
                "department": department,
                "major": canonical_major,
                "office": _normalize(override.get("office", existing.get("office", ""))),
                "email": _normalize(override.get("email", existing.get("email", ""))),
                "phone": _normalize(override.get("phone", existing.get("phone", ""))),
                "overview": _normalize(override.get("overview", overview)),
                "school": _normalize(program.get("school", "")),
                "source_url": _normalize(override.get("source_url", PROGRAM_SOURCE_URL)),
            }
        )

    department_rows.sort(key=lambda row: (row["department"], row["major"]))
    return department_rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    program_rows = build_program_rows()
    department_rows = build_department_rows(program_rows)

    write_csv(
        PROGRAMS_PATH,
        ["major", "canonical_major", "degree_type", "department", "school", "aliases", "source_url", "notes"],
        program_rows,
    )
    write_csv(
        DEPARTMENTS_PATH,
        ["department", "major", "office", "email", "phone", "overview", "school", "source_url"],
        department_rows,
    )

    print(f"Wrote {len(program_rows)} program rows to {PROGRAMS_PATH}")
    print(f"Wrote {len(department_rows)} department rows to {DEPARTMENTS_PATH}")


if __name__ == "__main__":
    main()
