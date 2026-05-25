from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.domains.auth.dependencies import get_current_teacher
from app.domains.auth.models import User
from app.domains.instruction.dependencies import get_instruction_service
from app.domains.instruction.models import GeneratedProblem
from app.domains.instruction.schemas import (
    AssignmentListResponse,
    AssignmentResponse,
    CreateAssignmentDraftRequest,
)
from app.domains.instruction.service import (
    AssignmentAccessError,
    AssignmentNotFoundError,
    InstructionError,
    InstructionService,
    InvalidAssignmentTransitionError,
)

router = APIRouter(prefix="/teacher/instruction", tags=["teacher"])


@router.post("/assignments/draft", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment_draft(
    body: CreateAssignmentDraftRequest,
    current_user: User = Depends(get_current_teacher),
    instruction_service: InstructionService = Depends(get_instruction_service),
) -> AssignmentResponse:
    try:
        assignment = instruction_service.create_draft_assignment(
            teacher=current_user,
            target_type=body.target_type,
            class_id=body.class_id,
            student_id=body.student_id,
            unit_id=body.unit_id,
            lesson_id=body.lesson_id,
            stage=body.stage,
            concept_key=body.concept_key,
            problems=[
                GeneratedProblem(**problem.model_dump(exclude_none=True))
                for problem in body.problems
            ],
            generation_context=body.generation_context,
        )
        return AssignmentResponse(**assignment.model_dump())
    except AssignmentAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except InstructionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/assignments", response_model=AssignmentListResponse)
def list_assignments(
    status_filter: str | None = Query(default=None, alias="status"),
    class_id: str | None = Query(default=None),
    student_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_teacher),
    instruction_service: InstructionService = Depends(get_instruction_service),
) -> AssignmentListResponse:
    assignments = instruction_service.list_assignments(
        teacher=current_user,
        status=status_filter,
        class_id=class_id,
        student_id=student_id,
    )
    items = [
        AssignmentResponse(**assignment.model_dump())
        for assignment in assignments
    ]
    return AssignmentListResponse(assignments=items, total_count=len(items))


@router.patch("/assignments/{assignment_id}/assign", response_model=AssignmentResponse)
def assign_assignment(
    assignment_id: str,
    current_user: User = Depends(get_current_teacher),
    instruction_service: InstructionService = Depends(get_instruction_service),
) -> AssignmentResponse:
    return _transition_assignment(
        lambda: instruction_service.assign(current_user, assignment_id)
    )


@router.patch("/assignments/{assignment_id}/cancel", response_model=AssignmentResponse)
def cancel_assignment(
    assignment_id: str,
    current_user: User = Depends(get_current_teacher),
    instruction_service: InstructionService = Depends(get_instruction_service),
) -> AssignmentResponse:
    return _transition_assignment(
        lambda: instruction_service.cancel(current_user, assignment_id)
    )


@router.patch("/assignments/{assignment_id}/complete", response_model=AssignmentResponse)
def complete_assignment(
    assignment_id: str,
    current_user: User = Depends(get_current_teacher),
    instruction_service: InstructionService = Depends(get_instruction_service),
) -> AssignmentResponse:
    return _transition_assignment(
        lambda: instruction_service.complete(current_user, assignment_id)
    )


def _transition_assignment(operation) -> AssignmentResponse:
    try:
        assignment = operation()
        return AssignmentResponse(**assignment.model_dump())
    except AssignmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AssignmentAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except InvalidAssignmentTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
