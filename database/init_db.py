from database.database import Base, engine

print("Створюємо таблиці...")
Base.metadata.create_all(bind=engine)

print("Таблиці створені!")