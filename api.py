from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import Column, Integer, String, Date, create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

DATABASE_URL = "postgresql+psycopg://sc_shokum:linux@localhost:5432/scrapperdb"

app = FastAPI()

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Entity(Base):
    __tablename__ = 'entity_data'
    file_number = Column(Integer, primary_key=True, index=True)
    incorporation_date = Column(Date)
    entity_name = Column(String)
    entity_kind = Column(String)
    entity_type = Column(String)
    residency = Column(String)
    state = Column(String)

class EntityBase(BaseModel):
    file_number: int
    entity_name: str

class EntityDetail(EntityBase):
    incorporation_date: str
    entity_kind: str
    entity_type: str
    residency: str
    state: str

    class Config:
        orm_mode = True

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    logging.info("Database connected successfully")

@app.on_event("shutdown")
def shutdown():
    engine.dispose()
    logging.info("Database connection closed")

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@app.get("/entities/", response_model=List[EntityBase])
def read_entities(session: Session = Depends(get_session)):
    entities = session.query(Entity.file_number, Entity.entity_name).all()
    return [{"file_number": e.file_number, "entity_name": e.entity_name} for e in entities]

@app.get("/entities/{file_number}", response_model=EntityDetail)
def read_entity(file_number: int, session: Session = Depends(get_session)):
    entity = session.query(Entity).filter(Entity.file_number == file_number).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return EntityDetail(
        file_number=entity.file_number,
        entity_name=entity.entity_name,
        incorporation_date=entity.incorporation_date.strftime("%Y-%m-%d"),
        entity_kind=entity.entity_kind,
        entity_type=entity.entity_type,
        residency=entity.residency,
        state=entity.state
    )

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)
