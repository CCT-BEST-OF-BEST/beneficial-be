"""학생이 교사가 배정한 학습 과제를 조회하는 Instruction 라우터.

경로 prefix: /student/learning/assignments
주 사용자: 학생

classroom/student_class_router.py와 다른 점:
- classroom/student_class_router.py는 학생의 소속 반 정보를 조회한다.
- 이 파일은 교사가 배정한 Stage 3 복습/과제 목록을 조회한다.
- 즉, 반 소속 정보가 아니라 instruction 도메인의 "배정 과제" 리소스다.
"""
from fastapi import APIRouter, Depends, Query

from app.domains.auth.dependencies import get_current_student
from app.domains.auth.models import User
from app.domains.instruction.dependencies import get_instruction_service
from app.domains.instruction.schemas import (
    StudentAssignmentListResponse,
    StudentAssignmentProblemResponse,
    StudentAssignmentResponse,
)
from app.domains.instruction.service import InstructionService

# 학생 관점의 배정 과제 조회 API.
router = APIRouter(prefix="/student/learning/assignments", tags=["student-learning"])


@router.get("", response_model=StudentAssignmentListResponse)
def list_my_assignments(
    lesson_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_student),
    instruction_service: InstructionService = Depends(get_instruction_service),
) -> StudentAssignmentListResponse:
    """현재 학생에게 배정된 Stage 3 과제를 조회한다."""
    assignments = instruction_service.list_student_assignments(
        student_id=current_user.user_id,
        lesson_id=lesson_id,
        stage=3,
    )
    items = []
    for assignment in assignments:
        items.append(
            StudentAssignmentResponse(
                assignment_id=assignment.assignment_id,
                lesson_id=assignment.lesson_id,
                unit_id=assignment.unit_id,
                stage=assignment.stage,
                concept_key=assignment.concept_key,
                status=assignment.status,
                completed_problem_ids=assignment.student_progress.get(
                    current_user.user_id,
                    [],
                ),
                assigned_at=assignment.assigned_at,
                problems=[
                    StudentAssignmentProblemResponse(
                        problem_id=str(problem.problem_id),
                        problem_key=problem.problem_key,
                        type=problem.type,
                        sentence_part1=problem.sentence_part1,
                        sentence_part2=problem.sentence_part2,
                        visual_hint=problem.visual_hint,
                        accent_color=problem.accent_color,
                    )
                    for problem in assignment.problems
                ],
            )
        )
    return StudentAssignmentListResponse(assignments=items, total_count=len(items))
