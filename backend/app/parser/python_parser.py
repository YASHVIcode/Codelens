import ast
import os

def parse_file(filepath):
    """
    Ye function ek .py file ko padhta hai aur uske
    andar ke saare functions aur classes nikaal ke
    return karta hai.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    tree = ast.parse(source_code, filename=filepath)
    
    functions = []
    classes = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "calls": extract_calls(node)
            })
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "start_line": node.lineno,
                "end_line": node.end_lineno
            })
    
    return {
        "file": filepath,
        "functions": functions,
        "classes": classes
    }


def extract_calls(func_node):
    """
    Ek function ke andar jo bhi doosre functions
    call kiye gaye hain, unke naam nikaalta hai.
    """
    calls = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.append(node.func.id)
    return calls


def parse_project(root_dir):
    all_results = {}
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # venv aur __pycache__ folders ko skip karo
        dirnames[:] = [d for d in dirnames if d not in ('venv', '__pycache__', '.git')]
        
        for fname in filenames:
            if fname.endswith('.py'):
                full_path = os.path.join(dirpath, fname)
                try:
                    result = parse_file(full_path)
                    all_results[full_path] = result
                except Exception as e:
                    print(f"Error parsing {full_path}: {e}")
    
    return all_results

if __name__ == "__main__":
    # Poore backend/app folder ko parse karo (test ke liye)
    project_root = os.path.join(os.path.dirname(__file__), '..')
    results = parse_project(project_root)
    
    print(f"\nTotal files parsed: {len(results)}\n")
    for filepath, data in results.items():
        print(f"File: {filepath}")
        print(f"  Functions: {[f['name'] for f in data['functions']]}")
        print(f"  Classes: {[c['name'] for c in data['classes']]}")
        print()