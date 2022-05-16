from sqlmodel import SQLModel, create_engine
from .models import MetadataRecord, VariantAlleleRecord
import os


def make_engine():
    DB_URL = os.getenv('VAFDB_URL')
    if not DB_URL:
        raise Exception(f"Environment variable 'VAFDB_URL' was not found.")
    engine = create_engine(DB_URL)
    return engine


def make_db_and_tables(engine):
    # Takes engine, creates database and tables that have been registered in the MetaData class
    # A table is registered in the MetaData class if table=True
    SQLModel.metadata.create_all(engine)


if __name__ == '__main__':
    engine = make_engine()
    make_db_and_tables(engine)