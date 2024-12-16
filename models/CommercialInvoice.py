from sqlalchemy import Column, ForeignKey, Integer, String, Date, Float
from sqlalchemy.orm import relationship
from database.connection import Base

class CommercialInvoice(Base):
    __tablename__ = 'commercialInvoice'
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    date_e = Column(Date, nullable=False)
    sale_id = Column(Integer)
    total = Column(Float, nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    customer = relationship('Customer', back_populates='commercial_invoice')