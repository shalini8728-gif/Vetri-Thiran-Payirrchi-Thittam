# FITBUDDY – AI FITNESS PLAN GENERATOR USING GEMINI MODELS

## 1. Introduction

FitBuddy is an AI-powered fitness plan generation application designed to create personalized 7-day workout plans based on user information such as name, age, weight, fitness goal, and workout intensity.

The application uses **Google Gemini AI models** to generate workout plans and nutrition/wellness tips. Users can also provide feedback, and FitBuddy uses the feedback to generate an updated workout plan.

The project is developed using **Python, FastAPI, Jinja2, SQLAlchemy, SQLite, HTML, CSS, and Google Gemini AI**.

---

# 2. Problem Statement

Creating a suitable workout plan manually can be difficult because every individual has different fitness goals, experience levels, and preferences.

FitBuddy solves this problem by providing an AI-based system that:

* Collects user fitness information.
* Generates a personalized 7-day workout plan.
* Provides nutrition and wellness tips.
* Allows users to give feedback.
* Updates the workout plan according to feedback.
* Stores user information and plans in a database.
* Provides an admin page to view registered users and their plans.

---

# 3. Objectives

The main objectives of FitBuddy are:

1. To develop an AI-based fitness planning application.
2. To generate personalized 7-day workout plans.
3. To integrate Google Gemini AI into a FastAPI application.
4. To provide nutrition and wellness suggestions.
5. To allow users to modify their plans using feedback.
6. To store user and workout information using SQLite.
7. To provide an admin interface for viewing users.
8. To create a simple and user-friendly web interface.

---

# 4. Technologies Used

| Technology       | Purpose                    |
| ---------------- | -------------------------- |
| Python           | Main programming language  |
| FastAPI          | Backend web framework      |
| Jinja2           | HTML template rendering    |
| HTML5            | Frontend structure         |
| CSS3             | Frontend styling           |
| SQLAlchemy       | Database ORM               |
| SQLite           | Database                   |
| Google Gemini    | AI-generated workout plans |
| Google GenAI SDK | Gemini API integration     |
| Uvicorn          | Application server         |
| Pydantic         | Data validation            |
| python-dotenv    | Environment configuration  |
| Pytest           | Testing                    |

---

# 5. System Architecture

The FitBuddy application follows a simple layered architecture.

```text
                    USER
                     |
                     v
              HTML / CSS UI
                     |
                     v
                FastAPI
                     |
          +----------+----------+
          |                     |
          v                     v
     Gemini AI Layer       SQLite Database
          |                     |
          v                     v
   Workout Generation       User Information
   Nutrition Tips           Workout Plans
   Plan Updates             Feedback
```

The main components are:

### Frontend

The frontend provides the interface through which users enter their information and view their generated plans.

### Backend

FastAPI handles requests, validation, AI processing, database operations, and HTML page rendering.

### AI Layer

Google Gemini is used to generate:

* 7-day workout plans.
* Nutrition and wellness tips.
* Updated workout plans based on feedback.

### Database Layer

SQLite stores:

* User information.
* Original workout plans.
* Updated workout plans.
* Nutrition tips.
* User feedback.

---

# 6. Project Folder Structure

```text
FitBuddy/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── schemas.py
│   ├── gemini_client.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   └── routes.py
│
├── templates/
│   ├── index.html
│   ├── result.html
│   └── all_users.html
│
├── static/
│   └── style.css
│
├── tests/
│   └── test_app.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── fitbuddy.db
```

---

# 7. Description of Important Files

## app/main.py

This is the main entry point of the FastAPI application.

Its responsibilities include:

* Creating the FastAPI application.
* Initializing the database.
* Mounting static files.
* Loading application routes.

The application can be started using Uvicorn.

---

## app/config.py

This file manages application configuration.

It loads values from the `.env` file, including:

```text
GEMINI_API_KEY
GEMINI_WORKOUT_MODEL
GEMINI_TIP_MODEL
DATABASE_URL
ADMIN_TOKEN
```

The Gemini API key is kept outside the source code so that it is not directly exposed.

---

## app/database.py

This file manages the SQLite database using SQLAlchemy.

It contains two major database models:

### User

Stores:

* User ID
* Name
* Age
* Weight
* Goal
* Intensity

### Plan

Stores:

* Original workout plan
* Updated workout plan
* Nutrition tip
* Feedback

The file also contains functions for:

* Saving users.
* Saving plans.
* Updating plans.
* Retrieving users.
* Retrieving plans.
* Listing users.
* Deleting users.

---

# 8. AI Integration

FitBuddy uses Google Gemini for AI-powered content generation.

## Workout Generation

The function:

```text
generate_workout_gemini()
```

generates a complete 7-day workout plan.

The generated plan contains:

* Day 1 to Day 7.
* Focus.
* Warm-up.
* Main workout.
* Recovery/cool-down.
* Exercise details.
* Sets, repetitions, or duration where appropriate.

---

## Nutrition and Wellness Tip

The function:

```text
generate_nutrition_tip_with_flash()
```

generates a short nutrition and wellness tip.

The tip focuses on:

* Balanced eating.
* Hydration.
* Recovery.
* Sleep.
* General wellness.

---

## Updating the Workout Plan

The function:

```text
update_workout_plan()
```

uses the existing workout plan and the user's feedback to generate a revised 7-day plan.

For example, a user can provide feedback such as:

```text
Add more cardio and include yoga.
```

FitBuddy sends the original plan and feedback to Gemini and generates a revised plan.

---

# 9. User Workflow

The application works in the following sequence:

```text
Start Application
       |
       v
Enter User Information
       |
       v
Validate Information
       |
       v
Generate Workout Plan
       |
       v
Generate Nutrition Tip
       |
       v
Save Information in Database
       |
       v
Display Result
       |
       v
User Provides Feedback
       |
       v
Generate Updated Plan
       |
       v
Display Updated Plan
```

---

# 10. User Input

The home page collects information such as:

* Name
* User ID
* Age
* Weight
* Fitness goal
* Workout intensity

The available goals include:

```text
Weight Loss
Muscle Gain
General Wellness
Flexibility
Strength
```

The intensity options include:

```text
Low
Medium
High
```

---

# 11. Workout Plan Generation

After the user submits the form, FastAPI receives the information.

The information is validated using Pydantic.

Then the application calls the Gemini workout generation function.

The AI creates a 7-day plan.

Example structure:

```text
Day 1
Focus:
Warm-up:
Main Workout:
Recovery/Cool-down:

Day 2
Focus:
Warm-up:
Main Workout:
Recovery
```
