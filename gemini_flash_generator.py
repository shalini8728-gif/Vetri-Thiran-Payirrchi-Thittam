from app.config import settings
from app.gemini_client import generate_text


def _safe_goal(age: int, goal: str) -> str:
    if age < 18 and goal.lower() == "weight loss":
        return "general wellness"
    return goal


def generate_nutrition_tip_with_flash(user_input) -> str:
    safe_goal = _safe_goal(user_input.age, user_input.goal)

    prompt = f"""
You are FitBuddy, an AI fitness and wellness assistant.

Generate ONE short and practical nutrition/wellness tip
for the following user:

Name: {user_input.name}
Age: {user_input.age}
Weight: {user_input.weight}
Goal: {safe_goal}
Intensity: {user_input.intensity}

Requirements:

1. Keep the response under 120 words.
2. Give general healthy nutrition and wellness guidance.
3. Encourage balanced meals with a variety of foods.
4. Encourage adequate hydration.
5. Mention healthy recovery and sleep when relevant.
6. Do not provide medical diagnosis.
7. Do not recommend medicines.
8. Do not recommend supplements or supplement dosages.
9. Do not recommend extreme dieting.
10. Do not provide calorie restriction or calorie targets.
11. Do not promote appearance-based goals.
12. If the user is under 18, focus on healthy growth,
    balanced eating, hydration, sleep, recovery,
    and enjoyable physical activity.
13. Use simple language that is easy to understand.

Return only the nutrition/wellness tip.
"""

    try:
        return generate_text(
            prompt=prompt,
            model=settings.tip_model,
            temperature=0.3,
            max_output_tokens=500,
        )

    except Exception as error:
        error_text = str(error)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            return (
                "Nutrition tip is temporarily unavailable because "
                "the Gemini API request limit was reached. "
                "Please try again after a short wait. "
                "Meanwhile, focus on balanced meals, hydration, "
                "adequate sleep, and healthy recovery."
            )

        raise