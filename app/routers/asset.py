from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from datetime import datetime

from app.models.point import Point
from app.schemas.point_response import PointListResponse

from app.models.loan_short_term import LoanShortTerm
from app.schemas.loan_short_term_response import LoanShortTermListResponse

from app.models.loan_long_term import LoanLongTerm
from app.schemas.loan_long_term_response import LoanLongTermListResponse

router = APIRouter(
    prefix="/v1/card",
    tags=["Asset"]
)

@router.get("/points", response_model=PointListResponse)
def get_points(
    user_id: str = Query(...),
    org_code: str = Query(...),
    search_timestamp: str = Query(...),
    db: Session = Depends(get_db)
):
    rows = db.query(Point).filter(
        Point.user_id == user_id,
        Point.org_code == org_code,
        Point.search_timestamp == search_timestamp
    ).all()

    return {
        "rsp_code": "00000",
        "rsp_msg": "정상처리",
        "search_timestamp": search_timestamp,
        "point_cnt": len(rows),
        "point_list": rows
    }


@router.get("/loans/short-term", response_model=LoanShortTermListResponse)
def get_loan_short_term(
    user_id: str = Query(...),
    org_code: str = Query(...),
    search_timestamp: str = Query(...),
    db: Session = Depends(get_db)
):
    rows = db.query(LoanShortTerm).filter(
        LoanShortTerm.user_id == user_id,
        LoanShortTerm.org_code == org_code,
        LoanShortTerm.search_timestamp == search_timestamp
    ).all()

    return {
        "rsp_code": "00000",
        "rsp_msg": "정상처리",
        "search_timestamp": search_timestamp,
        "short_term_cnt": len(rows),
        "short_term_list": rows
    }


@router.get("/loans/long-term", response_model=LoanLongTermListResponse)
def get_loan_long_term(
    user_id: str = Query(...),
    org_code: str = Query(...),
    search_timestamp: str = Query(...),
    db: Session = Depends(get_db)
):
    rows = db.query(LoanLongTerm).filter(
        LoanLongTerm.user_id == user_id,
        LoanLongTerm.org_code == org_code,
        LoanLongTerm.search_timestamp == search_timestamp
    ).all()

    return {
        "rsp_code": "00000",
        "rsp_msg": "정상처리",
        "search_timestamp": search_timestamp,
        "long_term_cnt": len(rows),
        "long_term_list": rows
    }
