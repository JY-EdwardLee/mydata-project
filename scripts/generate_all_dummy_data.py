# scripts/generate_all_dummy_data.py

from app.core.database import SessionLocal
from app.models.user import User
from app.models.card_list import Card
from app.models.card_bill import CardBill
from app.models.card_approval_domestic import CardApprovalDomestic
from app.models.point import Point
from app.models.prepaid_balance import PrepaidBalance
from app.models.prepaid_approval import PrepaidApproval
from app.models.loan_short_term import LoanShortTerm
from app.models.loan_long_term import LoanLongTerm
from app.core.security import hash_password 

import uuid
from faker import Faker
from datetime import datetime, timedelta
import random


fake = Faker()
Faker.seed(777)
db = SessionLocal()

ORG_CODES = {
"POST": "우체국",
"KB_CARD": "KB국민카드",
"WOORI_CARD": "우리카드",
"SC": "SC은행",
"NONGHYUP": "농협은행",
"HANA_CARD": "하나카드",
"LOTTE": "롯데카드",
"WOORI": "우리은행",
"KB_BANK": "국민은행",
"IBK": "IBK기업은행",
"SHINHAN_BANK": "신한은행",
"HANA_BANK": "하나은행",
"SAMSUNG": "삼성카드",
"SHINHAN_CARD": "신한카드",
"HYUNDAI": "현대카드",
"BC": "비씨카드",
"MIRAE": "미래에셋생명",
"KAKAO": "카카오뱅크"
}

try:
    # 1. 사용자 생성
    print("👥 사용자 생성 중...")
    users = []
    for _ in range(100):
        name = fake.user_name()
        users.append(User(
            id=str(uuid.uuid4()),
            username=name,
            email=fake.unique.email(),
            hashed_password=hash_password("test1234")  # 모든 유저 비밀번호는 동일하게
        ))
    db.add_all(users)
    db.commit()

    # 2. 카드 + 청구
    print("💳 카드 및 청구 정보 생성 중...")
    cards = []
    bills = []
    for user in users:
        for _ in range(random.randint(1, 7)):
            card_id = f"CARD_{uuid.uuid4().hex[:8]}"
            org_code = random.choice(list(ORG_CODES.keys()))
            cards.append(Card(
                user_id=user.id,
                card_id=card_id,
                card_name=fake.credit_card_provider(),
                card_num=fake.credit_card_number(),
                is_consent=True,
                card_member="1",
                card_type=random.choice(["01", "02"]),
                org_code=org_code
            ))

            for _ in range(random.randint(3, 6)):
                bills.append(CardBill(
                    user_id=user.id,
                    org_code=org_code,
                    charge_amt=random.randint(100000, 1000000),
                    charge_day=str(random.choice([5, 10, 15, 25])),
                    charge_month=fake.date_between(start_date="-6M", end_date="today").strftime("%Y%m"),
                    paid_out_date=fake.date_between(start_date="today", end_date="+30d").strftime("%Y%m%d")
                ))

    db.add_all(cards + bills)
    db.commit()

    # 3. 카드 승인내역
    print("🧾 카드 승인내역 생성 중...")
    approvals = []
    for card in cards:
        for _ in range(random.randint(5, 15)):
            approved_time = fake.date_time_between(start_date="-4M", end_date="now")
            approvals.append(CardApprovalDomestic(
                user_id=card.user_id,
                card_id=card.card_id,
                approved_dtime=approved_time.strftime("%Y%m%d%H%M"),
                approved_num=f"A{uuid.uuid4().hex[:8]}",
                status=random.choice(["01", "02"]),
                pay_type=random.choice(["01", "02"]),
                merchant_name=fake.company() + " " + fake.city(),
                merchant_regno=fake.bothify(text="###-##-#####"),
                approved_amt=random.randint(1000, 500000),
                total_install_cnt=random.choice([None, 2, 3, 6])
            ))
    db.add_all(approvals)
    db.commit()

    # 4. 포인트
    print("⭐ 포인트 정보 생성 중...")
    points = []
    for user in users:
        for org_code in random.sample(list(ORG_CODES.keys()), random.randint(1, 4)):
            points.append(Point(
                id=str(uuid.uuid4()),  # id 필드 추가
                user_id=user.id,
                org_code=org_code,
                search_timestamp=datetime.now().strftime("%Y%m%d%H%M%S"),
                point_name=f"{org_code} 포인트",
                remain_point_amt=random.randint(1000, 30000),
                expiring_point_amt=random.randint(0, 5000)
            ))
    db.add_all(points)
    db.commit()

    # 5. 선불카드 잔액 및 승인
    print("💰 선불카드 잔액 및 승인내역 생성 중...")
    prepaid_balances = []
    prepaid_approvals = []
    for user in users:
        for _ in range(random.randint(0, 4)):
            pp_id = f"PP_{uuid.uuid4().hex[:8]}"
            org_code = random.choice(list(ORG_CODES.keys()))
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            prepaid_balances.append(PrepaidBalance(
                user_id=user.id,
                org_code=org_code,
                pp_id=pp_id,
                search_timestamp=timestamp,
                total_balance_amt=random.randint(5000, 50000),
                charge_balance_amt=random.randint(3000, 30000),
                reserve_balance_amt=random.randint(1000, 15000),
                reserve_due_amt=random.randint(0, 3000),
                exp_due_amt=random.randint(0, 2000)
            ))

            for _ in range(random.randint(10, 15)):
                approved_time = fake.date_time_between(start_date="-3M", end_date="now")
                prepaid_approvals.append(PrepaidApproval(
                    user_id=user.id,
                    org_code=org_code,
                    pp_id=pp_id,
                    approved_dtime=approved_time.strftime("%Y%m%d%H%M"),
                    approved_num=f"PP{fake.unique.random_int(1000,9999)}",
                    status=random.choice(["01", "02"]),
                    pay_type=random.choice(["01", "02"]),
                    merchant_name=fake.company() + " " + fake.city(),
                    merchant_regno=fake.bothify(text="###-##-#####"),
                    approved_amt=random.randint(500, 30000)
                ))
    db.add_all(prepaid_balances + prepaid_approvals)
    db.commit()

    # 6. 대출
    print("🏦 단기 및 장기 대출 생성 중...")
    short_loans = []
    long_loans = []
    for user in users:
        if random.choice([True, False]):
            short_loans.append(LoanShortTerm(
                id=str(uuid.uuid4()),  # id 필드 추가
                user_id=user.id,
                org_code=random.choice(list(ORG_CODES.keys())),
                search_timestamp=datetime.now().strftime("%Y%m%d%H%M%S"),
                loan_dtime=fake.date_time_between(start_date="-2M", end_date="now").strftime("%Y%m%d%H%M%S"),
                loan_amt=random.randint(100000, 1000000),
                balance_amt=random.randint(10000, 900000),
                pay_due_date=(datetime.now() + timedelta(days=random.randint(7, 30))).strftime("%Y%m%d"),
                int_rate=round(random.uniform(10.0, 19.9), 1)
            ))

        if random.choice([True, False]):
            long_loans.append(LoanLongTerm(
                id=str(uuid.uuid4()),  # id 필드 추가
                user_id=user.id,
                org_code=random.choice(list(ORG_CODES.keys())),
                search_timestamp=datetime.now().strftime("%Y%m%d%H%M%S"),
                loan_num=f"LN{uuid.uuid4().hex[:8]}",
                loan_dtime=fake.date_between(start_date="-1y", end_date="today").strftime("%Y%m%d"),
                loan_type=random.choice(["신용대출", "학자금대출", "주택담보대출"]),
                loan_name=fake.bs().title(),
                loan_amt=random.randint(1000000, 30000000),
                int_rate=round(random.uniform(3.0, 15.0), 1),
                exp_date=(datetime.now() + timedelta(days=random.randint(180, 1080))).strftime("%Y%m%d"),
                balance_amt=random.randint(100000, 25000000),
                repay_method=random.choice(["01", "02"]),
                int_amt=random.randint(50000, 300000)
            ))
    db.add_all(short_loans + long_loans)
    db.commit()

    print("✅ 전체 더미 데이터 생성 완료!")

except Exception as e:
    db.rollback()
    print("❌ 에러 발생:", e)

finally:
    db.close()
