import databases
from sqlalchemy import (
    Column, String, Integer,
    ForeignKey, DateTime,
    Text, create_engine, Boolean
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

from core.utils import get_config

DATABASE = get_config()['postgres']

SQLALCHEMY_DATABASE_URL = f'postgres://{DATABASE["username"]}:' \
                          f'{DATABASE["password"]}@{DATABASE["host"]}:' \
                          f'{DATABASE["port"]}/{DATABASE["database"]}'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

database = databases.Database(SQLALCHEMY_DATABASE_URL)

Base: DeclarativeMeta = declarative_base()


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    title = Column(String(125))
    slug = Column(String)
    description = Column(String(250))
    title_image = Column(String)
    text = Column(Text)
    date = Column(DateTime)
    user = Column(Integer, ForeignKey('user.id'))
    user_id = relationship('User')


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    avatar = Column(String)
    name = Column(String, unique=True)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    password = Column(String(length=72), nullable=False)
    date = Column(DateTime)
    is_admin = Column(Boolean, default=True)
    disabled = Column(Boolean, default=False)


users = User.__table__
posts = Post.__table__
