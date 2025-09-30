import time
from dataclasses import dataclass

from sqlalchemy import desc, func
from utils.config import settings

from utils.models import conn, User, Question, AnsweredQuestion, AnswerOption


@dataclass
class LadderPos:
    pos: int
    username: str
    userid: str
    points: int


class LadderCache:
    instance: "LadderCache" = None

    def __init__(self):
        self.cache: list[LadderPos] = []
        self.create_time = 0

    def _calculate(self) -> list[LadderPos]:
        if self.cache and time.time() - self.create_time <= settings.cache_lifetime:
            return self.cache
        with conn() as session:
            users = session.query(User.telegram_id, User.username, func.count().label("points"))
            given_answers = users.join(AnsweredQuestion, AnsweredQuestion.user_id == User.telegram_id)
            answers = given_answers.join(AnswerOption, (AnswerOption.id == AnsweredQuestion.answer_id) & AnswerOption.correct)
            questions = answers.join(Question, AnswerOption.question_id == Question.id).group_by(User.telegram_id)
            rating = questions.order_by(desc("points")).all()
        self.cache.clear()
        pos = 1
        for tg_id, username, points in rating:
            self.cache.append(LadderPos(userid=tg_id, username=username, points=points if points else 0, pos=pos))
            pos += 1
        self.create_time = time.time()
        return self.cache

    @classmethod
    def get(cls):
        if not cls.instance:
            cls.instance = LadderCache()
        return cls.instance._calculate()
