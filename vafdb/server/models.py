from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel


class MetadataRecord(SQLModel, table=True):
    id : Optional[int] = Field(default=None, primary_key=True)    
    central_sample_id : str = Field(index=True) 
    run_name : str = Field(index=True)
    pag_name : str = Field(index=True)
    published_date : date = Field(index=True)
    fasta_path : str = Field(index=True)
    bam_path : str = Field(index=True)


class VariantAlleleRecord(SQLModel, table=True):
    id : Optional[int] = Field(default=None, primary_key=True)
    metadata_id : Optional[int] = Field(default=None, foreign_key="metadatarecord.id")
    position : int
    coverage : int
    pc_a : float
    pc_c : float
    pc_g : float
    pc_t : float
    pc_ds : float
    pc_n : float