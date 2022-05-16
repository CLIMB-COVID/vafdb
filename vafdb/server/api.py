from fastapi import Depends, FastAPI, Request, HTTPException
from sqlmodel import Session, select, sql
from .models import MetadataRecord, VariantAlleleRecord
from .db import make_engine
import os


sql.expression.SelectOfScalar.inherit_cache = True  # type: ignore
sql.expression.Select.inherit_cache = True  # type: ignore

vafdb_api = FastAPI()
engine = make_engine()


def get_session():
    with Session(engine) as session:
        yield session


@vafdb_api.post("/add")
def add(request : Request, metadata_record : MetadataRecord, va_record : VariantAlleleRecord, session : Session = Depends(get_session)):
    #If the incoming request has the required key to add records
    if request.headers.get('api_key') == os.getenv('VAFDB_ADD_KEY'):    
        # Get current record with given pag_name (if it exists)
        statement = select(MetadataRecord).where(MetadataRecord.pag_name == metadata_record.pag_name)
        # NOTE: I am assuming there's only one matching record
        existing_metadata_record = session.exec(statement).first()

        if existing_metadata_record:
            # Update the current record with new record data
            for attr, val in metadata_record.dict(exclude_unset=True).items():
                setattr(existing_metadata_record, attr, val)
            metadata_record = existing_metadata_record

        # Add model instance to the session
        session.add(metadata_record)
        # Commit the changes (save to database)
        session.commit()

        if metadata_record.id is not None:
            # Get current record with given pag_name (if it exists)
            statement = select(VariantAlleleRecord).where(VariantAlleleRecord.metadata_id == metadata_record.id, VariantAlleleRecord.position == va_record.position)
            # NOTE: I am assuming there's only one matching record
            existing_va_record = session.exec(statement).first()

            if existing_va_record:
                # Update the current record with new record data
                for attr, val in va_record.dict(exclude_unset=True).items():
                    setattr(existing_va_record, attr, val)
                va_record = existing_va_record
            else:
                va_record.metadata_id = metadata_record.id
            # Add model instance to the session
            session.add(va_record)
            # Commit the changes (save to database)
            session.commit()

        # Acknowledge new record
        return {'detail' : 'Record created'}
    else:
        # Forbidden
        raise HTTPException(status_code=403)
