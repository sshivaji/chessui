from sqlalchemy import BigInteger, Column, Integer, String, Date, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Text

Base = declarative_base()


class ChessDBModel(Base):
    __tablename__ = "chessdb"

    date = Column(DateTime, primary_key=True)
    user_email = Column(String(20), primary_key=True)
    db_pgn_location = Column(String(20))
    db_leveldb_location = Column(String(20))
    db_sqlite_location = Column(String(20))
    db_name = Column(String(20))
    status = Column(String(20))

    create_dt = Column(DateTime)
    last_updated_dt = Column(DateTime)

    # def __repr__(self):
    #     return "<Telemetry(ds: '%s', cust_id: '%s', dc_id: '%s', rack_id: '%s', node_id: '%s', log_type: '%s', log_seq: '%d')>"\
    #            % (self.ds, self.cust_id, self.dc_id, self.rack_id, self.node_id, self.log_type, self.log_seq)

def init_db(engine):
    Base.metadata.create_all(bind=engine)