from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.auth.dependencies import get_current_teacher
from app.domains.auth.models import User
from app.domains.classroom.dependencies import get_classroom_service
from app.domains.classroom.service import ClassroomService
from app.domains.learning.dependencies import get_learning_record_service
from app.domains.learning.service import LearningRecordService
from app.interfaces.teacher.schemas import (
    TeacherClassesResponse,
    TeacherClassResponse,
    TeacherClassStudentsResponse,
    TeacherStudentSummaryResponse,
)

router = APIRouter(prefix="/teacher/classes", tags=["teacher"])


@router.get("", response_model=TeacherClassesResponse)
def list_my_classes(
    current_user: User = Depends(get_current_teacher),
    classroom_service: ClassroomService = Depends(get_classroom_service),
) -> TeacherClassesResponse:
    classrooms = classroom_service.list_classes_for_user(current_user)
    items = [
        TeacherClassResponse(
            class_id=classroom.class_id,
            name=classroom.name,
            teacher_id=classroom.teacher_id,
            student_count=len(classroom.student_ids),
        )
        for classroom in classrooms
    ]
    return TeacherClassesResponse(classes=items, total_count=len(items))


@router.get("/{class_id}/students", response_model=TeacherClassStudentsResponse)
def list_class_students(
    class_id: str,
    current_user: User = Depends(get_current_teacher),
    classroom_service: ClassroomService = Depends(get_classroom_service),
    learning_record_service: LearningRecordService = Depends(get_learning_record_service),
) -> TeacherClassStudentsResponse:
    classroom = classroom_service.get_class_for_user(class_id, current_user)
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="반을 찾을 수 없습니다.",
        )

    students = classroom_service.list_students_for_class(class_id, current_user)
    items = [
        _to_student_summary(student, learning_record_service)
        for student in students
    ]
    return TeacherClassStudentsResponse(
        class_id=class_id,
        students=items,
        total_count=len(items),
    )


def _to_student_summary(
    student: dict,
    learning_record_service: LearningRecordService,
) -> TeacherStudentSummaryResponse:
    records = learning_record_service.get_records(student["user_id"])
    profile = learning_record_service.get_weakness_profile(
        student["user_id"],
        min_wrong_count=1,
    )
    return TeacherStudentSummaryResponse(
        user_id=student["user_id"],
        email=student.get("email", ""),
        display_name=student.get("display_name", ""),
        weak_concepts=[
            weak_concept.concept_key
            for weak_concept in profile.weak_concepts[:3]
        ],
        recent_activity_at=records[0].created_at if records else None,
    )
