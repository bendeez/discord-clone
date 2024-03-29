# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app import models
#
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:discord@localhost:5432/discord"
#
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# with SessionLocal() as db:
#     models.Dm_Messages.__table__.drop(engine)
