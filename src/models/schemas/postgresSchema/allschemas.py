from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,DateTime,func,String,ForeignKey
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import uuid
 
SQLAlchemyBase = declarative_base()


class Projects(SQLAlchemyBase):
    __tablename__="projects"
    project_id= Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    project_uuid=Column(UUID(as_uuid=True),default=uuid.uuid4,unique=True,nullable=False)

    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=Column(DateTime(timezone=True),onupdate=func.now(),nullable=True)



class Chunks(SQLAlchemyBase):
    __tablename__="Chunks"
    Chunks_id= Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    Chunks_uuid=Column(UUID(as_uuid=True),default=uuid.uuid4,unique=True,nullable=False)

    Chunk_text=Column(String,nullable=False)
    Chunk_metadata=Column(JSONB,nullable=False)
    Chunk_project_id=Column(Integer,ForeignKey("Projects.project_id"),nullable=False)

    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=Column(DateTime(timezone=True),onupdate=func.now(),nullable=True)


    __table_arg__=(
        Index("ix_Chunk_project_id",Chunk_project_id)
    )


class Assets(SQLAlchemyBase):
    __tablename__="Assets"

    Asset_id=Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    Asset_uuid=Column(UUID(as_uuid=True),default=uuid.uuid4,unique=True,nullable=False)

    Asset_name=Column(String,nullable=False)
    Asset_type=Column(String,nullable=False)
    Asset_size=Column(Integer,nullable=False)
    Asset_config=Column(JSONB,nullable=False)
    Asset_project_id=Column(Integer,ForeignKey("Projects.project_id"),nullable=False)

    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=Column(DateTime(timezone=True),onupdate=func.now(),nullabel=True)

    __table_args__=(
        Index("ix_Asset_project_id",Asset_project_id)
    )



