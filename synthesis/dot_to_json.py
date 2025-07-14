import networkx as nx
import sys
import csv
import os
import re

def parse_dot_to_csv(dot_file):
    """
    Parses a DOT file from a synthesized logic design to extract node and edge
    information into CSV files, with robust type detection.

    Args:
        dot_file (str): The path to the input DOT file.
    """
    if not os.path.exists(dot_file):
        sys.stderr.write(f"Error: The file '{dot_file}' was not found.\n")
        return

    base_name = os.path.splitext(dot_file)[0]
    nodes_csv_path = f"{base_name}_nodes.csv"
    edges_csv_path = f"{base_name}_edges.csv"

    try:
        graph = nx.drawing.nx_pydot.read_dot(dot_file)
    except Exception as e:
        sys.stderr.write(f"Error parsing DOT file: {e}\n")
        sys.stderr.write("Please ensure that pydot and graphviz are installed: 'pip install pydot graphviz'\n")
        return

    print("Processing nodes...")
    with open(nodes_csv_path, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "type"])

        for node_id, attrs in graph.nodes(data=True):
            clean_node_id = node_id.strip()
            raw_label = attrs.get("label", "").strip()
            
            inst_name = ""
            gate_type = clean_node_id

            # Rule-based type detection by node ID prefix
            if clean_node_id.startswith('x'):
                gate_type = "bit select"
                inst_name = raw_label.strip('"')
            elif clean_node_id.startswith('v'):
                gate_type = "constant"
                inst_name = raw_label.strip('"')
            elif clean_node_id.startswith('n'):
                gate_type = "port"
                inst_name = raw_label.strip('"')
            elif clean_node_id.startswith('c'):
                gate_type = ""
                
                # --- FINAL ROBUST LOGIC FOR 'c' NODES ---
                content = ""
                # This regex now correctly finds the content between port definitions, e.g., "...}|CONTENT|{..."
                match = re.search(r'\}\|(.+?)\|', raw_label)
                if match:
                    content = match.group(1).strip().replace(r'\n', '\n')
                
                # After finding the correct content, parse it for name and type
                if content:
                    if '\n' in content:
                        parts = content.split('\n', 1)
                        part1 = parts[0].strip()
                        part2 = parts[1].strip()
                        
                        # Heuristic to differentiate primitive gates from hierarchical blocks
                        if part2.startswith('$'):
                            inst_name = part1.lstrip('$')
                            gate_type = part2.lstrip('$')
                        else:
                            gate_type = part1
                            inst_name = part2
                    else: # Handle single-line content
                        gate_type = content.lstrip('$')
                # --- END FINAL LOGIC ---

            writer.writerow([clean_node_id, inst_name, gate_type])

    print(f"✅ Successfully created {nodes_csv_path}")

    print("Processing edges...")
    with open(edges_csv_path, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "source_port", "target_port"])

        for u, v in graph.edges():
            u_parts = u.strip().split(':', 1)
            v_parts = v.strip().split(':', 1)

            source_node = u_parts[0]
            source_port = u_parts[1] if len(u_parts) > 1 else ''
            target_node = v_parts[0]
            target_port = v_parts[1] if len(v_parts) > 1 else ''

            writer.writerow([source_node, target_node, source_port, target_port])
    print(f"✅ Successfully created {edges_csv_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Syntax: python %s <path_to_dot_file>\n" % sys.argv[0])
        sys.exit(1)

    dot_file_path = sys.argv[1]
    parse_dot_to_csv(dot_file_path)