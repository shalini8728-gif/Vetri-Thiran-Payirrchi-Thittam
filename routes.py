from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.database import (
    delete_user,
    get_all_plans,
    get_all_users,
    get_latest_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.gemini_generator import generate_workout_gemini
from app.schemas import FeedbackRequest, UserInput
from app.updated_plan import update_workout_plan
from app.config import settings


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
        },
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    name: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    try:
        user_input = UserInput(
            name=name,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        # Generate workout using Gemini
        try:
            workout_plan = generate_workout_gemini(user_input)
        except RuntimeError as error:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "request": request,
                    "error": str(error),
                },
                status_code=503,
            )

        # Generate nutrition tip
        try:
            nutrition_tip = generate_nutrition_tip_with_flash(user_input)
        except Exception:
            nutrition_tip = (
                "Nutrition tip is temporarily unavailable. "
                "Please focus on balanced meals, hydration, "
                "adequate sleep, and healthy recovery."
            )

        # Save user
        save_user(
            user_id=user_input.user_id,
            name=user_input.name,
            age=user_input.age,
            weight=user_input.weight,
            goal=user_input.goal,
            intensity=user_input.intensity,
        )

        # Save plan
        plan = save_plan(
            user_id=user_input.user_id,
            original_plan=workout_plan,
            nutrition_tip=nutrition_tip,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user_input,
                "plan": plan,
                "workout_plan": workout_plan,
                "nutrition_tip": nutrition_tip,
            },
        )

    except Exception as error:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": str(error),
            },
            status_code=500,
        )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
):
    try:
        feedback_request = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

        user = get_user(feedback_request.user_id)

        if not user:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "request": request,
                    "error": "User not found.",
                },
                status_code=404,
            )

        latest_plan = get_latest_plan(feedback_request.user_id)

        if not latest_plan:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "request": request,
                    "error": "No workout plan found for this user.",
                },
                status_code=404,
            )

        try:
            updated_plan = update_workout_plan(
                user,
                latest_plan.original_plan,
                feedback_request.feedback,
            )
        except RuntimeError as error:
            return templates.TemplateResponse(
                request=request,
                name="result.html",
                context={
                    "request": request,
                    "user": user,
                    "plan": latest_plan,
                    "workout_plan": latest_plan.original_plan,
                    "nutrition_tip": latest_plan.nutrition_tip,
                    "error": str(error),
                },
                status_code=503,
            )

        try:
            nutrition_tip = generate_nutrition_tip_with_flash(
                UserInput(
                    name=user.name,
                    user_id=user.user_id,
                    age=user.age,
                    weight=user.weight,
                    goal=user.goal,
                    intensity=user.intensity,
                )
            )
        except Exception:
            nutrition_tip = latest_plan.nutrition_tip or (
                "Focus on balanced meals, hydration, "
                "adequate sleep, and healthy recovery."
            )

        updated = update_plan(
            plan_id=latest_plan.id,
            updated_plan=updated_plan,
            feedback=feedback_request.feedback,
            nutrition_tip=nutrition_tip,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": updated,
                "workout_plan": updated_plan,
                "nutrition_tip": nutrition_tip,
                "updated": True,
            },
        )

    except Exception as error:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": str(error),
            },
            status_code=500,
        )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, token: str = ""):
    if not settings.admin_token or token != settings.admin_token:
        return HTMLResponse(
            content="Unauthorized",
            status_code=403,
        )

    users = get_all_users()
    plans = get_all_plans()

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "request": request,
            "users": users,
            "plans": plans,
        },
    )


@router.post("/admin/delete-user")
def admin_delete_user(user_id: str, token: str):
    if not settings.admin_token or token != settings.admin_token:
        return JSONResponse(
            content={"error": "Unauthorized"},
            status_code=403,
        )

    deleted = delete_user(user_id)

    if not deleted:
        return JSONResponse(
            content={"error": "User not found"},
            status_code=404,
        )

    return JSONResponse(
        content={
            "message": "User deleted successfully",
        }
    )


@router.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FitBuddy",
    }


@router.get("/api/users/{user_id}")
def get_user_api(user_id: str):
    user = get_user(user_id)

    if not user:
        return JSONResponse(
            content={"error": "User not found"},
            status_code=404,
        )

    latest_plan = get_latest_plan(user_id)

    return {
        "user": {
            "id": user.id,
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
        },
        "latest_plan": (
            {
                "id": latest_plan.id,
                "original_plan": latest_plan.original_plan,
                "updated_plan": latest_plan.updated_plan,
                "nutrition_tip": latest_plan.nutrition_tip,
                "feedback": latest_plan.feedback,
            }
            if latest_plan
            else None
        ),
    }