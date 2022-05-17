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


@vafdb_api.get("/get/metadata/central_sample_id/{central_sample_id}")
def get_metadata_central_sample_id(central_sample_id : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord).where(MetadataRecord.central_sample_id == central_sample_id)
    records = session.exec(statement).all()
    return records


@vafdb_api.get("/get/metadata/run_name/{run_name}")
def get_metadata_run_name(run_name : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord).where(MetadataRecord.run_name == run_name)
    records = session.exec(statement).all()
    return records


@vafdb_api.get("/get/metadata/pag_name/{pag_name}")
def get_metadata_pag_name(pag_name : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord).where(MetadataRecord.pag_name == pag_name)
    records = session.exec(statement).all()
    return records


@vafdb_api.get("/get/metadata/published_date/{published_date}")
def get_metadata_published_date(published_date : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord).where(MetadataRecord.published_date == published_date)
    records = session.exec(statement).all()
    return records


@vafdb_api.get("/get/metadata/fasta_path/{fasta_path}")
def get_metadata_fasta_path(fasta_path : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord).where(MetadataRecord.fasta_path == fasta_path)
    records = session.exec(statement).all()
    return records


@vafdb_api.get("/get/metadata/bam_path/{bam_path}")
def get_metadata_bam_path(bam_path : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord).where(MetadataRecord.bam_path == bam_path)
    records = session.exec(statement).all()
    return records


@vafdb_api.get("/get/vafs/central_sample_id/{central_sample_id}")
def get_vafs_central_sample_id(central_sample_id : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord, VAFRecord).where(MetadataRecord.central_sample_id == central_sample_id).where(MetadataRecord.id == VAFRecord.metadata_id)
    records = session.exec(statement).all()
    return records


@vafdb_api.get("/get/vafs/run_name/{run_name}")
def get_vafs_run_name(run_name : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord, VAFRecord).where(MetadataRecord.run_name == run_name).where(MetadataRecord.id == VAFRecord.metadata_id)
    records = session.exec(statement).all()
    return records


@vafdb_api.get("/get/vafs/pag_name/{pag_name}")
def get_vafs_pag_name(pag_name : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord, VAFRecord).where(MetadataRecord.pag_name == pag_name).where(MetadataRecord.id == VAFRecord.metadata_id)
    records = session.exec(statement).all()
    return records


@vafdb_api.get("/get/vafs/published_date/{published_date}")
def get_vafs_published_date(published_date : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord, VAFRecord).where(MetadataRecord.published_date == published_date).where(MetadataRecord.id == VAFRecord.metadata_id)
    records = session.exec(statement).all()
    return records


@vafdb_api.get("/get/vafs/fasta_path/{fasta_path}")
def get_vafs_fasta_path(fasta_path : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord, VAFRecord).where(MetadataRecord.fasta_path == fasta_path).where(MetadataRecord.id == VAFRecord.metadata_id)
    records = session.exec(statement).all()
    return records


@vafdb_api.get("/get/vafs/bam_path/{bam_path}")
def get_vafs_bam_path(bam_path : str, session : Session = Depends(get_session)):
    statement = select(MetadataRecord, VAFRecord).where(MetadataRecord.bam_path == bam_path).where(MetadataRecord.id == VAFRecord.metadata_id)
    records = session.exec(statement).all()
    return records
