from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.session import Base


class Cat(Base):
    __tablename__ = "cats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    years_of_experience = Column(Integer, nullable=False)
    specialization = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to missions one-to-one
    mission = relationship("Mission", back_populates="cat", uselist=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("years_of_experience >= 0", name="check_experience_positive"),
        CheckConstraint("salary > 0", name="check_salary_positive"),
    )


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(Integer, ForeignKey("cats.id"), nullable=True, unique=True)
    complete = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    cat = relationship("Cat", back_populates="mission")
    targets = relationship("Target", back_populates="mission", cascade="all, delete-orphan")


class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    notes = Column(Text, default="")
    complete = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    mission = relationship("Missions", back_populates="targets")
