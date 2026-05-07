from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.models import RuleMaster
from app.services.seed_rules import seed_all_product_rules


def create_database() -> None:
    Base.metadata.create_all(bind=engine)


def seed_database(db: Session) -> int:
    return seed_all_product_rules(db)


if __name__ == "__main__":
    from app.db.session import SessionLocal

    create_database()
    session = SessionLocal()
    try:
        inserted = seed_database(session)
        session.commit()
        print(f"Seeded {inserted} rules")
        print(f"Total rules: {session.query(RuleMaster).count()}")
    finally:
        session.close()
