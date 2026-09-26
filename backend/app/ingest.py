import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser.python_parser import parse_project
from models.db_models import SessionLocal, Project, File, Node, Edge


def ingest_project(project_name, root_dir):
    session = SessionLocal()

    project = Project(name=project_name, repo_path=root_dir)
    session.add(project)
    session.commit()

    parsed_data = parse_project(root_dir)

    node_lookup = {}

    for filepath, data in parsed_data.items():
        file_obj = File(project_id=project.id, path=filepath)
        session.add(file_obj)
        session.commit()

        for func in data["functions"]:
            node = Node(
                file_id=file_obj.id,
                type="function",
                name=func["name"],
                start_line=func["start_line"],
                end_line=func["end_line"]
            )
            session.add(node)
            session.commit()
            node_lookup[func["name"]] = node.id

        for cls in data["classes"]:
            node = Node(
                file_id=file_obj.id,
                type="class",
                name=cls["name"],
                start_line=cls["start_line"],
                end_line=cls["end_line"]
            )
            session.add(node)
            session.commit()
            node_lookup[cls["name"]] = node.id

    for filepath, data in parsed_data.items():
        for func in data["functions"]:
            source_id = node_lookup.get(func["name"])
            if not source_id:
                continue
            for called_name in func["calls"]:
                target_id = node_lookup.get(called_name)
                if target_id:
                    edge = Edge(
                        source_node_id=source_id,
                        target_node_id=target_id,
                        edge_type="CALLS"
                    )
                    session.add(edge)
        session.commit()

    session.close()
    print(f"Ingestion complete for project: {project_name}")
    print(f"Total files: {len(parsed_data)}")
    print(f"Total nodes: {len(node_lookup)}")


if __name__ == "__main__":
    project_root = os.path.join(os.path.dirname(__file__), "parser")
    ingest_project("TestProject", project_root)
