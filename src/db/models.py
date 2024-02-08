from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Uuid
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    '''Таблица с пользователями.'''

    __tablename__ = 'users'

    uid = Column(Uuid, default=uuid4, primary_key=True)
    username = Column(
        String(length=100),
        unique=True,
        nullable=False,
        index=True
    )
    password = Column(String, nullable=False)
    files = relationship(
        'File',
        back_populates='user',
        lazy='selectin',
        order_by='File.created'
    )


class File(Base):
    '''Таблица с файлами.'''

    __tablename__ = 'file'

    fid = Column(Uuid, default=uuid4, primary_key=True)
    name = Column(String(length=250), nullable=False)
    created = Column(DateTime(timezone=True), default=datetime.utcnow)
    path = Column(String(length=250), nullable=True)
    size = Column(Float, nullable=True)
    extension = Column(String(length=10), nullable=True)
    user_id = Column(ForeignKey('users.uid', ondelete='CASCADE'))
    user = relationship('User', back_populates='files')
