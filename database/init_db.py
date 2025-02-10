from database.database import Base,engine
from database import models  # Імпорт моделей перед створенням таблиць

def db_init():
    models.Base.metadata.create_all(bind=engine)