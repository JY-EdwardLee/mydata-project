from faker import Faker
import random
from app.core.database import SessionLocal
from app.models.user import User
from app.models.card_list import Card

db = SessionLocal()
fake = Faker()
Faker.seed(0)

users = []
cards = []

try:
    for _ in range(100):
        user_id = fake.uuid4()
        user = User(
            id=user_id,
            name=fake.name(),
            email=fake.email()
        )
        users.append(user)

        # 카드 1~3개 생성
        for i in range(random.randint(1, 3)):
            card = Card(
                card_id=f"CARD_{fake.unique.random_int(1000, 9999)}",
                user_id=user_id,
                org_code=random.choice(["HANA", "KB", "SAMSUNG"]),
                card_num=fake.credit_card_number(card_type=None),
                is_consent=True,
                card_name=fake.word().capitalize() + " 카드",
                card_member=random.choice(["1", "2"]),
                card_type=random.choice(["01", "02"])
            )
            cards.append(card)

    db.add_all(users + cards)
    db.commit()
    print("✅ 유저 + 카드 더미 생성 완료")
except Exception as e:
    db.rollback()
    print("❌ 에러:", e)
finally:
    db.close()
