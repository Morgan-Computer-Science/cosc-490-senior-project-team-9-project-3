
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
