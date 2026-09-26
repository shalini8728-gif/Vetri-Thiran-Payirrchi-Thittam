from app.config import settings
from app.gemini_client import generate_text


def _safe_goal(age: int, goal: str) -> str:
    """
    Keep the goal wellness-focused for users under 18.
    """
    if age < 18 and goal.lower() == "weight loss":
        return "general wellness"

    return goal


def generate_workout_gemini(user_input) -> str:
    """
    Generate a personalized 7-day workout plan using Gemini.
    """

    safe_goal = _safe_goal(
        user_input.age,
        user_input.goal
    )

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a safe and practical 7-day fitness plan using the
following user information:

Name: {user_input.name}
Age: {user_input.age}
Weight: {user_input.weight}
Goal: {safe_goal}
Intensity: {user_input.intensity}

Requirements:

1. Create exactly 7 days.
2. Clearly label Day 1 through Day 7.
3. For each day include:
   - Focus
   - Warm-up
   - Main Workout
   - Recovery/Cool-down
4. Include exercise names and useful details such as
   sets, repetitions, or duration where appropriate.
5. Include rest or recovery when appropriate.
6. Keep the plan practical and beginner-friendly.
7. Do not recommend dangerous or extreme exercises.
8. Do not provide medical diagnosis or medication advice.
9. Do not recommend supplements or supplement dosages.
10. Do not recommend extreme dieting or calorie restriction.
11. If the user is under 18, focus on healthy movement,
    general wellness, recovery, sleep, hydration,
    and balanced eating.
12. For users under 18, do not provide calorie targets
    or appearance-based goals.
13. Encourage proper exercise technique.
14. Encourage stopping an exercise if it causes pain
    or discomfort.

Use clear headings and readable formatting.

Return only the complete 7-day workout plan.
"""

    return generate_text(
        prompt=prompt,
        model=settings.workout_model,
        temperature=0.4,
        max_output_tokens=3000,
    )