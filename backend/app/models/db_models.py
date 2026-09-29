from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    repo_path = Column(String)

    files = relationship("File", back_populates="project")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    path = Column(String)

    project = relationship("Project", back_populates="files")
    nodes = relationship("Node", back_populates="file")


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    type = Column(String)
    name = Column(String)
    start_line = Column(Integer)
    end_line = Column(Integer)

    file = relationship("File", back_populates="nodes")


class Edge(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True)
    source_node_id = Column(Integer, ForeignKey("nodes.id"))
    target_node_id = Column(Integer, ForeignKey("nodes.id"))
    edge_type = Column(String)


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
