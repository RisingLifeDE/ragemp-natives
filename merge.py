import json
import os
import jsonschema
import traceback

def merge_json_namespaces(output_file, schema_file):
    input_dir = 'namespaces'
    current_file = None
    current_namespace = None

    try:
        if not os.path.exists(input_dir):
            print(f"Input directory {input_dir} does not exist")
            return

        merged_data = {}

        for namespace in sorted(os.listdir(input_dir)):
            current_namespace = namespace
            namespace_path = os.path.join(input_dir, namespace)

            if os.path.isdir(namespace_path):
                print(f"Processing namespace: {namespace}")
                namespace_data = {}
                files = sorted(os.listdir(namespace_path))

                for file in files:
                    current_file = os.path.join(namespace_path, file)
                    print(f"  Processing file: {current_file}")

                    try:
                        with open(current_file, 'r', encoding='utf-8') as infile:
                            data = json.load(infile)
                            namespace_data.update(data)
                    except json.JSONDecodeError as e:
                        print(f"ERROR: JSON decode error in file {current_file}")
                        print(f"  Line {e.lineno}, Column {e.colno}: {e.msg}")
                        raise
                    except UnicodeDecodeError as e:
                        print(f"ERROR: Unicode decode error in file {current_file}")
                        print(f"  {e}")
                        raise
                    except Exception as e:
                        print(f"ERROR: Unexpected error while reading file {current_file}")
                        print(f"  {type(e).__name__}: {e}")
                        raise

                merged_data[namespace] = namespace_data
                print(f"  Completed namespace: {namespace}")

        print(f"Loading schema from: {schema_file}")
        current_file = schema_file

        try:
            with open(schema_file, 'r', encoding='utf-8') as file:
                schema = json.load(file)
        except FileNotFoundError:
            print(f"ERROR: Schema file {schema_file} not found")
            raise
        except json.JSONDecodeError as e:
            print(f"ERROR: JSON decode error in schema file {schema_file}")
            print(f"  Line {e.lineno}, Column {e.colno}: {e.msg}")
            raise

        print("Validating merged data against schema...")
        try:
            jsonschema.validate(instance=merged_data, schema=schema)
            print("✓ Merged JSON is valid according to the schema.")
        except jsonschema.exceptions.ValidationError as err:
            print(f"ERROR: Schema validation failed")
            print(f"  Path: {' -> '.join(str(x) for x in err.absolute_path) if err.absolute_path else 'root'}")
            print(f"  Message: {err.message}")
            print(f"  Failed value: {err.instance}")
            raise
        except jsonschema.exceptions.SchemaError as err:
            print(f"ERROR: Invalid schema")
            print(f"  Message: {err.message}")
            raise

        print(f"Writing output to: {output_file}")
        current_file = output_file

        try:
            with open(output_file, 'w', encoding='utf-8') as outfile:
                json.dump(merged_data, outfile, indent=4, ensure_ascii=False)
            print(f'✓ Merged JSON successfully written to {output_file}')
        except Exception as e:
            print(f"ERROR: Failed to write output file {output_file}")
            print(f"  {type(e).__name__}: {e}")
            raise

    except KeyboardInterrupt:
        print(f"\nProcess interrupted by user")
        if current_file:
            print(f"Last file being processed: {current_file}")
    except Exception as e:
        print(f"\nERROR: Process failed")
        print(f"Last file being processed: {current_file}")
        if current_namespace:
            print(f"Current namespace: {current_namespace}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    output_file = 'natives.json'
    schema_file = 'schema.json'

    try:
        merge_json_namespaces(output_file, schema_file)
    except Exception:
        print("\nScript execution failed. Check the error messages above.")
        exit(1)