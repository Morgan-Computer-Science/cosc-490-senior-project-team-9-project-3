import { useEffect, useState } from "react";
import { fetchCourses } from "../api";

const CourseList = ({ token }) => {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    fetchCourses(token).then(setCourses).catch(console.error);
  }, [token]);

  return (
    <div>
      <h2>Available Courses</h2>
      <ul>
        {courses.map((course) => (
          <li key={course.id}>
            <strong>{course.code}</strong>: {course.title} ({course.credits}{" "}
            credits)
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CourseList;
