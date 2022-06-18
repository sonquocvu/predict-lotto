from sqlalchemy.orm import Session
from . import schemas
from .models import HCMLotto as Hcm
from .models import Vietlott645 as Vl645
from datetime import datetime


class Lotto:

    def __init__(self):
        self.model = {
            "HCM": Hcm,
            "Vietlott645": Vl645
        }

    def get_date(self, db: Session, date: datetime, tableName):
        return db.query(self.model[tableName].date).distinct().filter(self.model[tableName].date == date).first()

    def get_results(self, db: Session, tableName):
        return db.query(self.model[tableName].result).distinct().all()

    def get_result_objects(self, db: Session, tableName):
        return db.query(self.model[tableName]).all()

    def get_last_day(self, db: Session, tableName):
        return db.query(self.model[tableName].date).distinct().filter(self.model[tableName].is_last_day == True).first()

    def update_last_day(self, db: Session, tableName):
        db.query(self.model[tableName]).filter(self.model[tableName].is_last_day == True).update({self.model[tableName].is_last_day: False}, synchronize_session=False)
        db.commit()

    def create_result(self, db: Session, result: schemas.LottoCreate, tableName):
        db_result = self.model[tableName](**result.dict())
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
