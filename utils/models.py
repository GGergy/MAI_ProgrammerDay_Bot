from datetime import datetime
from enum import IntEnum
from types import NoneType

from sqlalchemy import ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

from utils.config import settings


class SqlAlchemyBase(DeclarativeBase):
    ...


def create_connection(name):
    connection = f"sqlite:///{name}?check_same_thread=False"
    engine = create_engine(connection, echo=False)
    session_generator = sessionmaker(bind=engine)
    SqlAlchemyBase.metadata.create_all(engine)
    return session_generator


"""class AsyncConnection:
    def __init__(self, name):
        connection = f"sqlite+aiosqlite:///{name}?check_same_thread=False"
        self._engine = create_async_engine(connection, echo=True)
        self.session = async_sessionmaker(bind=self._engine)

    async def create_all(self):
        async with self._engine.begin() as session:
            await session.run_sync(SqlAlchemyBase.metadata.create_all)"""


class Pending(SqlAlchemyBase):
    __tablename__ = "pendings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"), unique=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    @classmethod
    def get_lock(cls, session: Session, user_id) -> "NoneType | Pending":
        return session.query(cls).filter(cls.user_id == user_id).one_or_none()

    @classmethod
    def get_num_pending(cls, session: Session, qr_id) -> int:
        return session.query(cls).join(Question, (Question.id == cls.question_id) & (Question.qrcode_id == qr_id)).count()


class User(SqlAlchemyBase):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()


class Question(SqlAlchemyBase):
    __tablename__ = "questions"

    class QTypes(IntEnum):
        BUTTONS = 1
        MESSAGE = 2

    class QStatuses(IntEnum):
        OPEN = 1
        PENDING = 2
        CLOSED = 3

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column()
    type: Mapped[QTypes] = mapped_column()
    status: Mapped[QStatuses] = mapped_column(default=QStatuses.OPEN)
    qrcode_id: Mapped[int] = mapped_column(ForeignKey("qrcodes.id"))

    answers: Mapped[list["AnswerOption"]] = relationship(backref="question")


class AnswerOption(SqlAlchemyBase):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    text: Mapped[str] = mapped_column()
    correct: Mapped[bool] = mapped_column()


class QRcode(SqlAlchemyBase):
    __tablename__ = "qrcodes"

    id: Mapped[int] = mapped_column(primary_key=True)

    questions: Mapped[list["Question"]] = relationship(backref="qrcode")


class AnsweredQuestion(SqlAlchemyBase):
    __tablename__ = "answered_questions"
    __table_args__ = (UniqueConstraint("question_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"))


conn = create_connection(settings.db_file)
