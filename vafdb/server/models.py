from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel


class MetadataRecord(SQLModel, table=True):
    id : Optional[int] = Field(default=None, primary_key=True)    
    central_sample_id : str = Field(index=True) 
    run_name : str = Field(index=True)
    pag_name : Optional[str] = Field(default=None, index=True)
    published_date : Optional[date] = Field(default=None, index=True)
    fasta_path : Optional[str] = Field(default=None, index=True)
    bam_path : Optional[str] = Field(default=None, index=True)


class VAFRecord(SQLModel, table=True):
    id : Optional[int] = Field(default=None, primary_key=True)
    metadata_id : Optional[int] = Field(default=None, foreign_key="metadatarecord.id")
    position : int = Field(index=True)
    coverage : Optional[int] = Field(default=None)
    a : Optional[int] = Field(default=None)
    c : Optional[int] = Field(default=None)
    g : Optional[int] = Field(default=None)
    t : Optional[int] = Field(default=None)
    ds : Optional[int] = Field(default=None)
    n : Optional[int] = Field(default=None)
