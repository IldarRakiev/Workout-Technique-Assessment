from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from services.assessment_service import AssessmentService

router = APIRouter(
    prefix="/assessment",
    tags=["Assessment"],
    responses={404: {"description": "Not allowed"}}
)

@router.post("/")
async def assess_video(
    exercise_type: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Uploads a video, processes it through the rule-based and ML pipeline,
    and returns the assessment result as JSON.
    """
    try:
        service = AssessmentService()
        result = service.assess_uploaded_video(file, exercise_type)

        return JSONResponse(content=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")