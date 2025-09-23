import time
from dataclasses import dataclass

from sqlalchemy import desc, func
from utils.config import settings

from utils.models import conn, User, Question, AnsweredQuestion, Answer


@dataclass
class LadderPos:
    pos: int
    username: str
    userid: str
    points: int


class LadderCache:
    objects = dict()

    def __init__(self, faculty):
        self.faculty: int = faculty
        self.cache: list[LadderPos] = []
        self.create_time = 0
        LadderCache.objects[faculty] = self

    def calculate(self) -> list[LadderPos]:
        if self.cache and time.time() - self.create_time <= settings.cache_lifetime:
            return self.cache
        with conn() as session:
            users = session.query(User.telegram_id, User.username, func.sum(Question.pts).label("points")).filter(User.faculty_id == self.faculty)
            given_answers = users.join(AnsweredQuestion, AnsweredQuestion.user_id == User.telegram_id, isouter=True)
            answers = given_answers.join(Answer, (Answer.id == AnsweredQuestion.answer_id) & Answer.correct, isouter=True)
            questions = answers.join(Question, Answer.question_id == Question.id, isouter=True).group_by(User.telegram_id)
            rating = questions.order_by(desc("points")).all()
        self.cache.clear()
        pos = 1
        for tg_id, username, points in rating:
            self.cache.append(LadderPos(userid=tg_id, username=username, points=points if points else 0, pos=pos))
            pos += 1
        self.create_time = time.time()
        return self.cache

    @classmethod
    def get(cls, faculty):
        obj = cls.objects.get(faculty)
        if not obj:
            obj = LadderCache(faculty)
        return obj.calculate()
