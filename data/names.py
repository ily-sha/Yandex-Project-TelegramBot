import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Name(SqlAlchemyBase):
    __tablename__ = 'names'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("lap.id"))
    user = orm.relation('User')