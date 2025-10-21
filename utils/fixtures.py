import random

from utils.models import conn, Question, QRcode, AnswerOption
from routers.shared.handlers import normalize_text

questions_per_qr = 5


def gen_qr_id():
    with conn() as session:
        qr_ids = [qr.id for qr in session.query(QRcode).all()]
    while True:
        qr_id = random.randint(10 ** 6, 10 ** 9)
        while qr_id in qr_ids:
            qr_id = random.randint(10 ** 6, 10 ** 9)
        qr_ids.append(qr_id)
        yield qr_id


def load_questions(data: list[dict]):
    qr_ids = gen_qr_id()
    with conn() as session:
        for i, obj in enumerate(data):
            if i % questions_per_qr == 0:
                qr = QRcode(id=next(qr_ids))
                session.add(qr)
            text = obj["text"]
            question = Question(qrcode_id=qr.id, text=text, type=Question.QTypes.BUTTONS)
            session.add(question)
            session.flush()
            for j, opt in enumerate(obj["options"]):
                option = AnswerOption(question_id=question.id, text=opt, correct=(j == obj["answer_index"]))
                session.add(option)
        session.commit()