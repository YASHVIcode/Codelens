import sys
import os
import shutil
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import git

from models.db_models import SessionLocal, Project, File, Node, Edge
from ingest import ingest_project
from analysis.graph_analysis import (
    build_graph_from_db,
    find_dead_code,
    find_most_called_functions,
    find_cycles
)

app = FastAPI(title="CodeLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GitHubRequest(BaseModel):
    repo_url: str


@app.get("/")
def root():
    return {"message": "CodeLens API is running"}


@app.get("/projects")
def list_projects():
    session = SessionLocal()
    projects = session.query(Project).all()
    result = [
        {"id": p.id, "name": p.name, "repo_path": p.repo_path}
        for p in projects
    ]
    session.close()
    return result


@app.post("/ingest")
def ingest(project_name: str, folder_path: str):
    ingest_project(project_name, folder_path)
    return {"status": "success", "message": f"{project_name} ingested"}


@app.post("/analyze-github")
def analyze_github(request: GitHubRequest):
    repo_url = request.repo_url

    session = SessionLocal()
    session.query(Edge).delete()
    session.query(Node).delete()
    session.query(File).delete()
    session.query(Project).delete()
    session.commit()
    session.close()

    temp_folder = os.path.join(os.path.dirname(__file__), "temp_repos", str(uuid.uuid4()))
    os.makedirs(temp_folder, exist_ok=True)

    try:
        git.Repo.clone_from(repo_url, temp_folder)
    except Exception as e:
        shutil.rmtree(temp_folder, ignore_errors=True)
        return {"status": "error", "message": f"Clone failed: {str(e)}"}

    project_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')

    try:
        ingest_project(project_name, temp_folder)
    except Exception as e:
        return {"status": "error", "message": f"Parsing failed: {str(e)}"}

    return {"status": "success", "message": f"{project_name} analyzed successfully"}


@app.get("/graph")
def get_graph():
    session = SessionLocal()
    nodes = session.query(Node).all()
    edges = session.query(Edge).all()

    node_list = [
        {
            "id": n.id,
            "name": n.name,
            "type": n.type,
            "start_line": n.start_line,
            "end_line": n.end_line
        }
        for n in nodes
    ]

    edge_list = [
        {"source": e.source_node_id, "target": e.target_node_id}
        for e in edges
    ]

    session.close()
    return {"nodes": node_list, "edges": edge_list}


@app.get("/dead-code")
def dead_code():
    G = build_graph_from_db()
    dead = find_dead_code(G)
    return {"dead_code": dead}


@app.get("/most-called")
def most_called():
    G = build_graph_from_db()
    top = find_most_called_functions(G)
    return {"most_called": [{"name": n, "count": c} for n, c in top]}


@app.get("/cycles")
def cycles():
    G = build_graph_from_db()
    result = find_cycles(G)
    return {"cycles": result}
