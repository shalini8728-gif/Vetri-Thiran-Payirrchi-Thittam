from pydantic import BaseModel, Field, field_validator

ALLOWED_GOALS = {
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
    "strength",
}

ALLOWED_INTENSITIES = {
    "low",
    "medium",
    "high",
}


class UserInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    user_id: str = Field(..., min_length=1, max_length=80)
    age: int = Field(..., ge=13, le=100)
    weight: float = Field(..., ge=20, le=500)
    goal: str
    intensity: str

    @field_validator("name", "user_id")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ALLOWED_GOALS:
            raise ValueError(
                f"Invalid goal. Choose one of: {', '.join(sorted(ALLOWED_GOALS))}"
            )
        return value

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ALLOWED_INTENSITIES:
            raise ValueError(
                f"Invalid intensity. Choose one of: {', '.join(sorted(ALLOWED_INTENSITIES))}"
            )
        return value


class FeedbackRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=80)
    feedback: str = Field(..., min_length=3, max_length=1200)

    @field_validator("user_id", "feedback")
    @classmethod
    def validate_feedback_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value