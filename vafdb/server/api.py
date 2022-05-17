from fastapi import Depends, FastAPI, Request, HTTPException
from sqlmodel import Session, select, sql
from .models import MetadataRecord, VAFRecord
from .db import make_engine
from typing import List
import os


sql.expression.SelectOfScalar.inherit_cache = True  # type: ignore
sql.expression.Select.inherit_cache = True  # type: ignore

vafdb_api = FastAPI()
engine = make_engine()


def get_session():
    with Session(engine) as session:
        yield session


@vafdb_api.post("/add")
def add(request : Request, metadata : MetadataRecord, vafs : List[VAFRecord], session : Session = Depends(get_session)):
    #If the incoming request has the required key to add records
    if request.headers.get('vafdb_add_key') == os.getenv('VAFDB_ADD_KEY'):    
        # Get current record with given central_sample_id and run_name (if it exists)
        statement = select(MetadataRecord).where(
            MetadataRecord.central_sample_id == metadata.central_sample_id, 
            MetadataRecord.run_name == metadata.run_name
        )

        # NOTE: I am assuming there's only one matching record
        existing_metadata = session.exec(statement).first()

        if existing_metadata:
            # Update the current record with new record data
            for attr, val in metadata.dict(exclude_unset=True).items():
                setattr(existing_metadata, attr, val)
            metadata = existing_metadata

        # Add model instance to the session, then save to the database
        session.add(metadata)
        session.commit()

        if metadata.id is not None:
            for vaf in vafs:
                # Get current record with given metadata id and position (if it exists)
                statement = select(VAFRecord).where(
                    VAFRecord.metadata_id == metadata.id, 
                    VAFRecord.position == vaf.position
                )

                # NOTE: I am assuming there's only one matching record
                existing_vaf = session.exec(statement).first()

                if existing_vaf:
                    # Update the current record with new record data
                    for attr, val in vaf.dict(exclude_unset=True).items():
                        setattr(existing_vaf, attr, val)
                    vaf = existing_vaf
                else:
                    vaf.metadata_id = metadata.id
                
                # Add model instance to the session, then save to the database
                session.add(vaf)
                session.commit()

        # Acknowledge new record
        return {'detail' : 'Record created'}
    else:
        # Forbidden
        raise HTTPException(status_code=403)
