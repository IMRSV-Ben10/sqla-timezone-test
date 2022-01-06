import sys
from datetime import datetime, timezone

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import Column, Integer, String, create_engine, types
from sqlalchemy.orm import declarative_base, sessionmaker

# Create Database
con = psycopg2.connect(
    database='postgres',
    user='postgres',
    password='admin',
    host='localhost',
    port='5432')
con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = con.cursor()
try:
    cur.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier('tz'))
        )
    print("Database created.")
except psycopg2.DatabaseError:
    print("Database already exists.")
except Exception as ex:
    print("Unexpected Error.")
    print(ex)
    sys.exit(1)

# Create Tables
engine = create_engine('postgresql://postgres:admin@localhost/tz', echo=True)
Base = declarative_base()


class TimeStamp(types.TypeDecorator):
    impl = types.DateTime
    LOCAL_TIMEZONE = datetime.utcnow().astimezone().tzinfo

    def process_bind_param(self, value: datetime, dialect):
        if value.tzinfo is None:
            value = value.astimezone(self.LOCAL_TIMEZONE)

        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)


class TrueDateTimeModelMixin():
    # func.now does now work with this specifically
    created_at = Column(TimeStamp(), nullable=False, default=datetime.now())
    last_modified = Column(TimeStamp(), nullable=False,
                           default=datetime.now(), onupdate=datetime.now())


class Parent(TrueDateTimeModelMixin, Base):
    __tablename__ = 'parent'

    id = Column(Integer, primary_key=True)
    job = Column(String)


Base.metadata.bind = engine
Base.metadata.create_all()

# Insert Data
Session = sessionmaker(bind=engine)
ses = Session()

ses.add_all([
    Parent(job="Goblin Caretaker")
])

print(ses.new)

ses.commit()
