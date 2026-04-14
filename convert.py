import json
import os

NAMESPACES_DIR = "namespaces"
existing_info = {}

for namespace_dir in os.listdir(NAMESPACES_DIR):
    ns_path = os.path.join(NAMESPACES_DIR, namespace_dir)
    if not os.path.isdir(ns_path):
        continue
    existing_info[namespace_dir] = {}
    for filename in os.listdir(ns_path):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(ns_path, filename)
        with open(filepath, "r") as f:
            data = json.load(f)
        for hash_key, content in data.items():
            existing_info[namespace_dir][hash_key] = {}
            if "build" in content:
                existing_info[namespace_dir][hash_key]["build"] = content["build"]
            if "examples" in content:
                existing_info[namespace_dir][hash_key]["examples"] = content["examples"]

with open("input.json", "r") as f:
    input_data = json.load(f)

output_data = {}

for namespace, natives in input_data.items():
    output_data[namespace] = {}
    for hash_key, entry in natives.items():
        if not isinstance(entry, dict):
            continue
        name = entry.get("name", f"_{hash_key}")
        build = "unknown"
        examples = []
        if namespace in existing_info and hash_key in existing_info[namespace]:
            if "build" in existing_info[namespace][hash_key]:
                build = existing_info[namespace][hash_key]["build"]
            if "examples" in existing_info[namespace][hash_key]:
                examples = existing_info[namespace][hash_key]["examples"]
        converted = {
            "name": name,
            "comment": entry.get("description", ""),
            "params": [],
            "return_type": entry.get("results", "void"),
            "build": build,
            "examples": examples,
        }
        for param in entry.get("params", []):
            converted["params"].append({
                "type": param.get("type", "Any"),
                "name": param.get("name", "param")
            })
        if "hash" in entry:
            converted["gta_hash"] = entry["hash"]
        if entry.get("manualHash"):
            converted["gta_jhash"] = ""
        output_data[namespace][hash_key] = converted

with open("natives.json", "w") as f:
    json.dump(output_data, f, indent=4)
