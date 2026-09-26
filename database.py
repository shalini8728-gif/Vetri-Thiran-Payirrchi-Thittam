from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from app.config import settings


# --------------------------------------------------
# Database setup
# --------------------------------------------------

Base = declarative_base()


# SQLite needs this option when used with FastAPI
connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# --------------------------------------------------
# User table
# --------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        String(80),
        unique=True,
        index=True,
        nullable=False,
    )

    name = Column(
        String(120),
        nullable=False,
    )

    age = Column(
        Integer,
        nullable=False,
    )

    weight = Column(
        Float,
        nullable=False,
    )

    goal = Column(
        String(50),
        nullable=False,
    )

    intensity = Column(
        String(20),
        nullable=False,
    )

    plans = relationship(
        "Plan",
        back_populates="user",
        cascade="all, delete-orphan",
    )


# --------------------------------------------------
# Plan table
# --------------------------------------------------

class Plan(Base):
    __tablename__ = "plans"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    original_plan = Column(
        Text,
        nullable=False,
    )

    updated_plan = Column(
        Text,
        nullable=True,
    )

    nutrition_tip = Column(
        Text,
        nullable=True,
    )

    feedback = Column(
        Text,
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="plans",
    )


# --------------------------------------------------
# Create database tables
# --------------------------------------------------

def init_db():
    Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# Save user
# --------------------------------------------------

def save_user(
    user_id: str,
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
):
    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if user:
            user.name = name
            user.age = age
            user.weight = weight
            user.goal = goal
            user.intensity = intensity
        else:
            user = User(
                user_id=user_id,
                name=name,
                age=age,
                weight=weight,
                goal=goal,
                intensity=intensity,
            )

            db.add(user)

        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()


# --------------------------------------------------
# Save workout plan
# --------------------------------------------------

def save_plan(
    user_id: str,
    original_plan: str,
    nutrition_tip: str = "",
):
    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if not user:
            raise ValueError(
                f"User '{user_id}' does not exist."
            )

        plan = Plan(
            user_id=user.id,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )

        db.add(plan)
        db.commit()
        db.refresh(plan)

        return plan

    finally:
        db.close()


# --------------------------------------------------
# Update workout plan after feedback
# --------------------------------------------------

def update_plan(
    plan_id: int,
    updated_plan: str,
    feedback: str,
    nutrition_tip: str = "",
):
    db = SessionLocal()

    try:
        plan = db.query(Plan).filter(
            Plan.id == plan_id
        ).first()

        if not plan:
            raise ValueError(
                f"Plan with ID {plan_id} was not found."
            )

        plan.updated_plan = updated_plan
        plan.feedback = feedback

        if nutrition_tip:
            plan.nutrition_tip = nutrition_tip

        db.commit()
        db.refresh(plan)

        return plan

    finally:
        db.close()


# --------------------------------------------------
# Get user
# --------------------------------------------------

def get_user(user_id: str):
    db = SessionLocal()

    try:
        return db.query(User).filter(
            User.user_id == user_id
        ).first()

    finally:
        db.close()


# --------------------------------------------------
# Get latest plan for a user
# --------------------------------------------------

def get_latest_plan(user_id: str):
    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if not user:
            return None

        return (
            db.query(Plan)
            .filter(Plan.user_id == user.id)
            .order_by(Plan.id.desc())
            .first()
        )

    finally:
        db.close()


# --------------------------------------------------
# Get all users
# --------------------------------------------------

def get_all_users():
    db = SessionLocal()

    try:
        return (
            db.query(User)
            .order_by(User.id.desc())
            .all()
        )

    finally:
        db.close()


# --------------------------------------------------
# Get all plans
# --------------------------------------------------

def get_all_plans():
    db = SessionLocal()

    try:
        return (
            db.query(Plan)
            .order_by(Plan.id.desc())
            .all()
        )

    finally:
        db.close()


# --------------------------------------------------
# Delete user
# --------------------------------------------------

def delete_user(user_id: str):
    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if not user:
            return False

        db.delete(user)
        db.commit()

        return True

    finally:
        db.close()