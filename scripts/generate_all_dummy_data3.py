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

from faker import Faker
from datetime import datetime, timedelta
import uuid
import random

# 0. 공통 설정
db = SessionLocal()
fake = Faker()
Faker.seed(42)

ORG_CODES = [
    "우체국", "㈜KB국민카드", "주식회사 우리카드", "주식회사 한국스탠다드차타드은행", "농협은행 주식회사",
    "하나카드 주식회사", "롯데카드 주식회사", "(주)우리은행", "주식회사 국민은행", "중소기업은행",
    "주식회사 신한은행", "주식회사 하나은행", "삼성카드주식회사", "신한카드 주식회사",
    "현대카드 주식회사", "비씨카드 주식회사", "미래에셋생명보험 ㈜", "주식회사 카카오뱅크"
]

# 1. User 생성
print("🔄 사용자 더미 생성 중...")
users = []
for _ in range(100):
    users.append(User(
        id=str(uuid.uuid4()),
        name=fake.name(),
        email=fake.unique.email()
    ))
db.add_all(users)
db.commit()

# 사용자 조회 (생성된 id 사용을 위해 다시 조회)
users = db.query(User).all()
print(f"✅ 사용자 {len(users)}명 생성 완료")


# 2-1. 카드 + 청구정보 생성
print("🔄 카드 및 청구 정보 생성 중...")
cards = []
bills = []

for user in users:
    user_cards = []
    for _ in range(random.randint(1, 7)):
        card_id = f"CARD_{uuid.uuid4().hex[:8]}"
        card = Card(
            card_id=card_id,
            user_id=user.id,
            card_num=fake.credit_card_number(),
            is_consent=True,
            card_name=fake.credit_card_provider(),
            card_member=random.choice(["1", "2"]),
            card_type=random.choice(["01", "02"]),
            org_code=random.choice(ORG_CODES)
        )
        cards.append(card)
        user_cards.append((card_id, user.id))

    # 카드 청구 정보 (3~6개월)
    for _ in range(random.randint(3, 6)):
        charge_month = fake.date_between(start_date='-6M', end_date='today').strftime("%Y%m")
        paid_out_date = (datetime.strptime(charge_month + "15", "%Y%m%d") + timedelta(days=20)).strftime("%Y%m%d")
        bills.append(CardBill(
            user_id=user.id,
            org_code=random.choice(ORG_CODES),
            charge_amt=random.randint(50000, 1000000),
            charge_day=random.choice(["5", "10", "15", "25"]),
            charge_month=charge_month,
            paid_out_date=paid_out_date
        ))

db.add_all(cards + bills)
db.commit()
print(f"✅ 카드 {len(cards)}개, 청구정보 {len(bills)}건 생성 완료")

# 2-2. 카드 승인내역
print("🔄 카드 승인내역 생성 중...")
approvals = []

for card in cards:
    for _ in range(random.randint(5, 50)):
        approved_time = fake.date_time_between(start_date="-4M", end_date="now")
        approvals.append(CardApprovalDomestic(
            user_id=card.user_id,
            card_id=card.card_id,
            approved_dtime=approved_time.strftime("%Y%m%d%H%M"),
            approved_num=f"A{uuid.uuid4().hex[:6]}",
            status=random.choice(["01", "02"]),
            pay_type=random.choice(["01", "02"]),
            merchant_name=fake.company() + " " + fake.city(),
            merchant_regno=fake.bothify(text="###-##-#####"),
            approved_amt=random.randint(1000, 500000),
            total_install_cnt=random.choice([None, 2, 3, 6])
        ))

db.add_all(approvals)
db.commit()
print(f"✅ 승인내역 {len(approvals)}건 생성 완료")


# 3-1. 포인트 생성
print("🔄 포인트 정보 생성 중...")
points = []

for user in users:
    for org_code in random.sample(ORG_CODES, random.randint(1, 4)):
        points.append(Point(
            user_id=user.id,
            org_code=org_code,
            search_timestamp=datetime.now().strftime("%Y%m%d%H%M%S"),
            point_name=f"{org_code} 포인트",
            remain_point_amt=random.randint(1000, 30000),
            expiring_point_amt=random.randint(0, 5000)
        ))

db.add_all(points)
db.commit()
print(f"✅ 포인트 {len(points)}건 생성 완료")


# 3-2. 선불카드 잔액 및 승인내역
print("🔄 선불카드 잔액 및 승인내역 생성 중...")
prepaid_balances = []
prepaid_approvals = []

for user in users:
    for _ in range(random.randint(0, 4)):
        pp_id = f"PP_{uuid.uuid4().hex[:8]}"
        org_code = random.choice(ORG_CODES)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # 잔액
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

        # 승인내역
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
print(f"✅ 선불 잔액 {len(prepaid_balances)}건, 승인내역 {len(prepaid_approvals)}건 생성 완료")

# 3-3. 단기/장기 대출 생성
print("🔄 단기 및 장기 대출 정보 생성 중...")
short_loans = []
long_loans = []

for user in users:
    # 단기 대출 (0~1건)
    if random.choice([True, False]):
        short_loans.append(LoanShortTerm(
            user_id=user.id,
            org_code=random.choice(ORG_CODES),
            search_timestamp=datetime.now().strftime("%Y%m%d%H%M%S"),
            loan_dtime=fake.date_time_between(start_date="-2M", end_date="now").strftime("%Y%m%d%H%M%S"),
            loan_amt=random.randint(100000, 1000000),
            balance_amt=random.randint(10000, 900000),
            pay_due_date=(datetime.now() + timedelta(days=random.randint(7, 30))).strftime("%Y%m%d"),
            int_rate=round(random.uniform(10.0, 19.9), 1)
        ))

    # 장기 대출 (0~1건)
    if random.choice([True, False]):
        long_loans.append(LoanLongTerm(
            user_id=user.id,
            org_code=random.choice(ORG_CODES),
            search_timestamp=datetime.now().strftime("%Y%m%d%H%M%S"),
            loan_num=f"LN{uuid.uuid4().hex[:6]}",
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
print(f"✅ 단기대출 {len(short_loans)}건, 장기대출 {len(long_loans)}건 생성 완료")
