from enum import IntEnum

from sqlalchemy import create_engine, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, sessionmaker, declarative_base, Mapped, mapped_column

from utils.config import settings


SqlAlchemyBase = declarative_base()


def create_connection(name):
    connection = f"sqlite:///{name}?check_same_thread=False"
    engine = create_engine(connection, echo=False)
    session_generator = sessionmaker(bind=engine)
    SqlAlchemyBase.metadata.create_all(engine)
    return session_generator


class FacultyToCategory(SqlAlchemyBase):
    __tablename__ = "faculty_to_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))


class User(SqlAlchemyBase):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id"), nullable=True)


class Question(SqlAlchemyBase):
    __tablename__ = "questions"

    class QTypes(IntEnum):
        BUTTONS = 1
        MESSAGE = 2

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column()
    type: Mapped[QTypes] = mapped_column()
    pts: Mapped[int] = mapped_column()
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    answers: Mapped[list["Answer"]] = relationship(backref="question")


class Answer(SqlAlchemyBase):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    text: Mapped[str] = mapped_column()
    correct: Mapped[bool] = mapped_column()


class Category(SqlAlchemyBase):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()

    faculties: Mapped[list["Faculty"]] = relationship(secondary="faculty_to_category", backref="categories")
    questions: Mapped[list["Question"]] = relationship(backref="category")


class Faculty(SqlAlchemyBase):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(primary_key=True)


class AnsweredQuestion(SqlAlchemyBase):
    __tablename__ = "answered_questions"
    __table_args__ = (UniqueConstraint("question_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"))


conn: sessionmaker = create_connection(settings.db_file)
