from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from .config import configuration

def get_connection_string():
    conn_str = 'postgresql+pg8000://{dbusername}:{dbpassword}'\
               '@{dbhost}:{dbport}/{dbname}'.format(**configuration)
    return conn_str

Base = declarative_base()

MAXUINT64 = 2**63-1

forward_sequence = Sequence(
    'forward_seq',
    start=1,
    minvalue=1,
    maxvalue=MAXUINT64,
    cycle=True,
)

backward_sequence = Sequence(
    'backward_seq',
    start=MAXUINT64,
    increment=-1,
    maxvalue=MAXUINT64,
    minvalue=1,
    cycle=True
)

engine = create_engine(
    get_connection_string(),
    pool_recycle=1800
)

session_factory = scoped_session(sessionmaker(bind=engine))


class CountersContainer(Base):
    '''
    Non traditional ORM table to hold core sequence counters.

    '''
    __tablename__ = 'counters_container'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fid = Column(
        Integer,
        forward_sequence
    )
    bid = Column(
        Integer,
        backward_sequence
    )


@contextmanager
def session_scope():
    '''
    Provides a transactional scope around a series of operations.
    '''
    session = session_factory()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def create_schema():
    Base.metadata.create_all(engine)

def drop_schema():
    assert 'prod' not in configuration.get('dbhost'), 'Production schema cannot be dropped'
    Base.metadata.drop_all(engine)

