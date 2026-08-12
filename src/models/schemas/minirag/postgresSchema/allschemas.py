from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from sqlalchemy import Column,Integer,DateTime,func,String,ForeignKey
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import uuid
 
SQLAlchemyBase = declarative_base()


class Project(SQLAlchemyBase):
    __tablename__="Projects"
    project_id= Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    project_uuid=Column(UUID(as_uuid=True),default=uuid.uuid4,unique=True,nullable=False)

    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=Column(DateTime(timezone=True),onupdate=func.now(),nullable=True)

    chunks=relationship("Chunk",back_populates="project")
    assets=relationship("Asset",back_populates="project")



class Chunk(SQLAlchemyBase):
    __tablename__="Chunks"
    Chunks_id= Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    Chunks_uuid=Column(UUID(as_uuid=True),default=uuid.uuid4,unique=True,nullable=False)

    Chunk_text=Column(String,nullable=False)
    Chunk_metadata=Column(JSONB,nullable=False)
    Chunk_project_id=Column(Integer,ForeignKey("Projects.project_id"),nullable=False)
    Chunk_asset_id=Column(Integer,ForeignKey("Assets.Asset_id"),nullable=False)

    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=Column(DateTime(timezone=True),onupdate=func.now(),nullable=True)


    project=relationship("Project",back_populates="chunks")
    asset=relationship("Asset",back_populates="chunks")
    
    __table_args__=(
        Index("ix_Chunk_project_id",Chunk_project_id),
    )



class Retrived_chunks(BaseModel):
    text: str
    score: float






class Asset(SQLAlchemyBase):
    __tablename__="Assets"

    Asset_id=Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    Asset_uuid=Column(UUID(as_uuid=True),default=uuid.uuid4,unique=True,nullable=False)

    Asset_name=Column(String,nullable=False)
    Asset_type=Column(String,nullable=False)
    Asset_size=Column(Integer,nullable=False)
    Asset_config=Column(JSONB,nullable=True)
    Asset_project_id=Column(Integer,ForeignKey("Projects.project_id"),nullable=False)

    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=Column(DateTime(timezone=True),onupdate=func.now(),nullable=True)

    chunks=relationship("Chunk",back_populates="asset")
    project=relationship("Project",back_populates="assets")

    __table_args__=(
        Index("ix_Asset_project_id",Asset_project_id),
    )



