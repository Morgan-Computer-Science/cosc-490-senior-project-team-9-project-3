
import pytest


def test_catalog_endpoints_return_data(client, auth_headers):
    courses = client.get("/catalog/courses", headers=auth_headers)
    assert courses.status_code == 200
    assert isinstance(courses.json(), list)
    assert courses.json()

    departments = client.get("/catalog/departments", headers=auth_headers)
    assert departments.status_code == 200
    assert isinstance(departments.json(), list)
    assert departments.json()

    faculty = client.get("/catalog/faculty", headers=auth_headers)
    assert faculty.status_code == 200
    assert isinstance(faculty.json(), list)
    assert faculty.json()

    support = client.get("/catalog/support-resources", headers=auth_headers)
    assert support.status_code == 200
    assert isinstance(support.json(), list)
    assert support.json()


def test_course_search_filters_results(client, auth_headers):
    response = client.get("/catalog/courses?search=COSC", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()
    assert all("COSC" in (course["code"] + course["title"]) for course in response.json())


def test_course_level_filter_returns_matching_hundreds_level_courses(client, auth_headers):
    response = client.get("/catalog/courses?level=1", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(course["level"] == "100" for course in payload)


def test_course_major_filter_returns_only_computer_science_family_courses(client, auth_headers):
    response = client.get("/catalog/courses?major=Computer Science", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(course["code"].startswith("COSC") for course in payload)


def test_course_major_and_level_filter_returns_only_matching_computer_science_level_courses(client, auth_headers):
    response = client.get("/catalog/courses?major=Computer Science&level=3", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(course["code"].startswith("COSC") for course in payload)
    assert all(course["level"] == "300" for course in payload)


def test_course_major_filter_supports_program_aliases(client, auth_headers):
    response = client.get("/catalog/courses?major=Information Science", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(course["code"].startswith("INSS") for course in payload)
    assert {"INSS141", "INSS201", "INSS220", "INSS310", "INSS340"}.issubset(
        {course["code"] for course in payload}
    )


def test_course_major_filter_returns_non_empty_cloud_computing_family(client, auth_headers):
    response = client.get("/catalog/courses?major=Cloud Computing", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(course["code"].startswith("CLDC") for course in payload)


def test_course_major_filter_returns_biology_family_courses(client, auth_headers):
    response = client.get("/catalog/courses?major=Biology", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(course["code"].startswith("BIOL") for course in payload)


def test_course_major_filter_returns_nursing_family_courses(client, auth_headers):
    response = client.get("/catalog/courses?major=Nursing", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(course["code"].startswith("NURS") for course in payload)


def test_course_major_filter_returns_psychology_family_courses(client, auth_headers):
    response = client.get("/catalog/courses?major=Psychology", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(course["code"].startswith("PSYC") for course in payload)


@pytest.mark.parametrize(
    "major_name,min_count,prefix",
    [
        ("Finance", 3, "FINA"),
        ("Marketing", 4, "MKTG"),
    ],
)
def test_catalog_priority_business_filters_are_broad_enough_for_browsing(
    client,
    auth_headers,
    major_name,
    min_count,
    prefix,
):
    response = client.get(f"/catalog/courses?major={major_name}", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= min_count
    assert all(course["code"].startswith(prefix) for course in payload)


@pytest.mark.parametrize(
    "major_name,level,prefixes",
    [
        ("Computer Science", 3, {"COSC"}),
        ("Information Science", None, {"INSS"}),
        ("Cloud Computing", None, {"CLDC"}),
        ("Nursing", None, {"NURS"}),
        ("Biology", 1, {"BIOL"}),
        ("Psychology", 3, {"PSYC"}),
        ("Criminal Justice", None, {"CRJU"}),
        ("Elementary Education", 3, {"EDUC"}),
        ("Accounting", 3, {"ACCT"}),
        ("Finance", 3, {"FINA"}),
        ("Business Administration", None, {"BUSN", "MGMT"}),
        ("Marketing", 3, {"MKTG"}),
    ],
)
def test_catalog_major_filter_stays_inside_priority_major_family(client, auth_headers, major_name, level, prefixes):
    params = [f"major={major_name}"]
    if level is not None:
        params.append(f"level={level}")
    response = client.get(f"/catalog/courses?{'&'.join(params)}", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert {course["code"][:4] for course in payload}.issubset(prefixes)


def test_catalog_includes_launch_visible_departments_and_faculty(client, auth_headers):
    departments = client.get("/catalog/departments", headers=auth_headers)
    assert departments.status_code == 200
    department_majors = {row["major"] for row in departments.json()}
    assert "Cloud Computing" in department_majors
    assert "Architecture" in department_majors

    faculty = client.get("/catalog/faculty", headers=auth_headers)
    assert faculty.status_code == 200
    faculty_departments = {row["department"] for row in faculty.json()}
    assert "Cloud Computing" in faculty_departments
    assert "Architecture" in faculty_departments


def test_catalog_programs_endpoint_returns_broad_official_programs(client, auth_headers):
    response = client.get("/catalog/programs", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 50
    majors = {row["major"] for row in payload}
    assert "Actuarial Science" in majors
    assert "Architecture and Environmental Design" in majors
    assert "Transportation Systems Engineering" in majors


def test_catalog_departments_preserve_curated_contact_details(client, auth_headers):
    response = client.get("/catalog/departments", headers=auth_headers)

    assert response.status_code == 200
    rows_by_major = {row["major"]: row for row in response.json()}

    computer_science = rows_by_major["Computer Science"]
    architecture = rows_by_major["Architecture"]
    economics = rows_by_major["Economics"]
    political_science = rows_by_major["Political Science"]

    assert computer_science["email"] == "csdept@morgan.edu"
    assert computer_science["office"] == "Calloway Hall 312"
    assert architecture["email"] == "architecturedept@morgan.edu"
    assert architecture["office"] == "Banneker Hall 140"
    assert rows_by_major["Actuarial Science"]["email"] == "actuarialscience@morgan.edu"
    assert economics["email"] == "randal.reed@morgan.edu"
    assert political_science["phone"] == "443-885-3277"


def test_catalog_departments_include_new_high_impact_program_contacts(client, auth_headers):
    response = client.get("/catalog/departments", headers=auth_headers)

    assert response.status_code == 200
    rows_by_major = {row["major"]: row for row in response.json()}

    assert rows_by_major["Physics"]["email"]
    assert rows_by_major["Philosophy"]["email"]
    assert rows_by_major["Construction Management"]["office"]
