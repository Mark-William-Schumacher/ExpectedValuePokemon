import os
import importlib
import importlib.util
import sys


def setup_schema(conn):
    """
    Dynamically set up all defined tables by recursively scanning the schema folder,
    ensuring parent tables are created before their dependents.
    """
    cursor = conn.cursor()
    schema_folder = os.path.join(os.path.dirname(__file__), 'schema')

    # Define a priority order for tables with dependencies.
    # Paths are relative to the 'schema' directory.
    priority_order = [
        'set/sets.py',
        'set/cards.py',
    ]

    # Collect all schema files from the schema directory
    all_schema_files = []
    for root, _, files in os.walk(schema_folder):
        for filename in files:
            if filename.endswith('.py') and filename != '__init__.py':
                # Create a normalized relative path (e.g., 'sales/transactions.py')
                rel_path = os.path.relpath(os.path.join(root, filename), schema_folder)
                all_schema_files.append(rel_path.replace(os.path.sep, '/'))

    # Sort the collected files to ensure priority files are processed first
    def sort_key(file_path):
        try:
            # Priority files get their index, others are processed after
            return priority_order.index(file_path)
        except ValueError:
            # Assign a high index to non-priority files to sort them last
            return len(priority_order)

    all_schema_files.sort(key=sort_key)

    # Process the sorted list of schema files
    for file_rel_path in all_schema_files:
        file_path = os.path.join(schema_folder, file_rel_path.replace('/', os.path.sep))
        module_name_parts = file_rel_path[:-3].split('/')
        module_name = f"dynamic_schema.{'.'.join(module_name_parts)}"

        # Dynamically import the module from its file path
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Look for a create function convention (e.g., "create_<table>_table")
        create_function_names = [
            func
            for func in dir(module)
            if func.startswith("create_") and func.endswith("_table")
        ]
        for func_name in create_function_names:
            create_func = getattr(module, func_name)
            create_func(cursor)  # Execute the table creation function

    # Commit changes
    conn.commit()
