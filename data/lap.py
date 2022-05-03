import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
import datetime


class User(SqlAlchemyBase):
    __tablename__ = 'lap'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    format = sqlalchemy.Column(sqlalchemy.String, autoincrement=False, nullable=True)
    username = sqlalchemy.Column(sqlalchemy.String, autoincrement=False, nullable=True)
    language = sqlalchemy.Column(sqlalchemy.String, autoincrement=False, nullable=True)
    wait_promocod = sqlalchemy.Column(sqlalchemy.Boolean, autoincrement=False, nullable=True, default=False)
    wait_friend = sqlalchemy.Column(sqlalchemy.Boolean, autoincrement=False, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, autoincrement=False, nullable=True)
    file = sqlalchemy.Column(sqlalchemy.BLOB,autoincrement=False)
    user_status = sqlalchemy.Column(sqlalchemy.Integer,autoincrement=False)
    user_code = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=False)
    telegram_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    name = orm.relation("Name", back_populates='user')