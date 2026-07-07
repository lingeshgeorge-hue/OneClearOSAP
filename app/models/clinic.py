from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)

    clinic_name = Column(String)

    phone = Column(String)

    email = Column(String)

    website = Column(String)

    city = Column(String)

    state = Column(String)

    specialty = Column(String)