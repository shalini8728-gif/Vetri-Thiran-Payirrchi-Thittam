from app.config import settings
from app.gemini_client import generate_text


def _safe_goal(age: int, goal: str) -> str:
    """
    Keep the goal wellness-focused for users under 18.
    """
    if age < 18 and goal.lower() == "weight loss":
        return "general wellness"

    return goal


def update_workout_plan(user, original_plan: str, feedback: str) -> str:
    """
    Create an updated 7-day workout plan based on
    the original plan and the user's feedback.
    """

    safe_goal = _safe_goal(user.age, user.goal)

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

The user already has a 7-day fitness plan.
Create a revised version of the complete 7-day plan
based on the user's feedback.

USER INFORMATION
----------------
Name: {user.name}
Age: {user.age}
Weight: {user.weight}
Goal: {safe_goal}
Intensity: {user.intensity}

ORIGINAL 7-DAY PLAN
-------------------
{original_plan}

USER FEEDBACK
-------------
{feedback}

REQUIREMENTS
------------

1. Create exactly 7 days.
2. Clearly label Day 1 through Day 7.
3. Use the original plan as the starting point.
4. Apply the user's feedback where it is safe and practical.
5. For every day include:
   - Focus
   - Warm-up
   - Main Workout
   - Recovery/Cool-down
6. Include exercise names and useful details such as
   sets, repetitions, or duration when appropriate.
7. Include rest and recovery where appropriate.
8. Keep the plan practical and beginner-friendly.
9. Do not recommend dangerous or extreme exercises.
10. Do not provide medical diagnosis or medication advice.
11. Do not recommend supplements or supplement dosages.
12. Do not recommend extreme dieting or calorie restriction.
13. For users under 18, focus on healthy movement,
    general wellness, recovery, sleep, hydration,
    and balanced eating.
14. For users under 18, do not provide calorie targets
    or appearance-based goals.
15. Encourage proper exercise technique.
16. Encourage stopping an exercise if it causes pain
    or discomfort.
17. Keep the formatting clear and easy to read.
18. Return the complete revised plan, not only the changes.

Return ONLY the revised 7-day workout plan.
"""

    updated_plan = generate_text(
        prompt=prompt,
        model=settings.workout_model,
        temperature=0.4,
        max_output_tokens=3000,
    )

    return updated_plan