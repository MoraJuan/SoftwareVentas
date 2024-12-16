from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base

class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    value = Column(Float)
    date = Column(Date)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship('Product', backref='stocks')