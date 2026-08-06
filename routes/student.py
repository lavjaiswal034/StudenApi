from flask import Blueprint, request
from models import Student
from extensions import db
student = Blueprint("student", __name__)

@student.route("/students", methods=["POST"])
def add_student():

    data = request.get_json()

    student_data = Student(
        name=data["name"],
        college=data["college"],
        course=data["course"]
    )

    db.session.add(student_data)
    db.session.commit()

    return {
        "message": "Student Added Successfully",
        "id": student_data.id
    }, 201

@student.route("/students", methods=["GET"])
def get_students():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    name = request.args.get("name")
    college = request.args.get("college")
    course = request.args.get("course")

    query = Student.query

    if name:
        query = query.filter(Student.name.ilike(f"%{name}%"))

    if college:
        query = query.filter(Student.college == college)

    if course:
        query = query.filter(Student.course == course)

    students = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    result = []

    for s in students.items:
        result.append({
            "id": s.id,
            "name": s.name,
            "college": s.college,
            "course": s.course
        })

    return {
        "page": page,
        "per_page": per_page,
        "total": students.total,
        "pages": students.pages,
        "students": result
    }