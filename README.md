# Python Import & Packaging Deep Dive

A hands-on exploration of Python's module/package resolution system. This repo is structured as a pedagogical tool to help intermediate Python developers understand the nuances of imports, package structure, and the Python module system.

## What This Repo Demonstrates

This repository demonstrates several key aspects of Python's import and packaging ecosystem:

1. **Package Structure**: The `src/` layout pattern with proper `__init__.py` files
2. **Import Behaviors**: How Python resolves imports differently based on context
3. **Package Installation**: Using `pyproject.toml` for modern packaging
4. **Module Introspection**: Examining `__name__`, `__package__`, and `sys.path`
5. **Manual Importing**: How to programmatically import modules using `importlib`

## Getting Started

Set up your environment:

```bash
# Create and activate virtual environment using uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

## Exploring the Code

### The Import System Visualized

```
┌─────────────────────────────────┐
│ Python Import System            │
├─────────────────────────────────┤
│                                 │
│  1. Find Module                 │
│     │                           │
│     ▼                           │
│  2. Load Module                 │
│     │                           │
│     ▼                           │
│  3. Execute Module Code         │
│     │                           │
│     ▼                           │
│  4. Add to sys.modules Cache    │
│     │                           │
│     ▼                           │
│  5. Return Module Object        │
└─────────────────────────────────┘

Module Search Path (sys.path):
[0] Script directory or CWD
[1] PYTHONPATH directories
[2] Standard library directories
[3] Site-packages (installed pkgs)
```

#### Detailed Import Example: Anatomy of `import requests`

Let's walk through exactly what happens when you run `import requests` in your code:

1. **Finding the Module**:
   - Python checks if `requests` is already in `sys.modules` (the module cache)
   - If not found, Python creates a new module object: `requests = types.ModuleType('requests')`
   - The interpreter then searches for the module using `sys.meta_path`

2. **Module Search Process**:
   - `sys.meta_path` contains finder objects that implement the import protocol
   - For each finder, Python calls `finder.find_spec('requests', None)`
   - The PathFinder checks each directory in `sys.path`:
     - First the current directory or script directory
     - Then PYTHONPATH directories
     - Then standard library locations
     - Finally, site-packages where third-party packages are installed
   - When `/path/to/site-packages/requests/__init__.py` is found, a ModuleSpec is created

3. **Loading the Module**:
   - The ModuleSpec contains a loader that is responsible for module creation
   - `module.__spec__ = spec` sets the spec on the module
   - `sys.modules['requests'] = module` registers the module in the cache
   - The loader executes the module's code in its namespace

4. **Module Initialization**:
   - `requests/__init__.py` is executed
   - Global variables, functions, and classes are defined in the module's `__dict__`
   - Any submodules are imported (e.g., `requests.models`)
   - `__all__` list controls what is exported with `from requests import *`

5. **Submodule Imports**:
   - When `requests/__init__.py` imports submodules like `from . import models`
   - The importer knows the parent package is `requests`
   - It looks for `requests/models.py` or `requests/models/__init__.py`
   - Each submodule has its own entry in `sys.modules` (e.g., `sys.modules['requests.models']`)

6. **Package Namespace**:
   - Submodules are added to the package namespace:
     ```python
     # Inside requests/__init__.py
     from . import models
     # Now models is accessible as requests.models
     ```
   - This is stored in the package's `__dict__` as an attribute

7. **Return Value**:
   - The `requests` module object is returned by the import statement
   - The caller receives this module object and binds it to a name
   - Example: `import requests as req` binds the module to the name `req`

Here's what the interpreter state looks like after `import requests`:

```python
# sys.modules now contains:
sys.modules['requests'] = <module 'requests'>
sys.modules['requests.models'] = <module 'requests.models'>
sys.modules['requests.api'] = <module 'requests.api'>
# etc.

# The requests module's namespace (__dict__) contains:
requests.__dict__ = {
    '__name__': 'requests',
    '__package__': 'requests',
    '__path__': ['/path/to/site-packages/requests'],
    '__file__': '/path/to/site-packages/requests/__init__.py',
    '__spec__': <ModuleSpec for 'requests'>,
    'models': <module 'requests.models'>,
    'api': <module 'requests.api'>,
    'get': <function get>,
    'post': <function post>,
    # etc.
}
```

#### The Import Protocol (PEP 302)

Python's import system is extensible through the import hooks protocol:

1. **Import Hooks**:
   - `sys.meta_path`: List of finder objects consulted to find modules
   - `sys.path_hooks`: List of callables that convert path entries to path-specific finders
   - These allow for custom import behavior (e.g., importing from zip files, databases)

2. **ModuleSpec and Loader Objects**:
   - `finder.find_spec(name, path, target)` returns a ModuleSpec
   - ModuleSpec encapsulates module loading information
   - The loader executes the module code with `loader.exec_module(module)`

3. **Custom Importers**:
   - You can create custom importers by adding to `sys.meta_path`
   - This is how tools like PyInstaller bundle Python applications
   - Example: Python's zipimport lets you import directly from .zip files

For an interactive exploration, try these commands:

```python
# Examine the import machinery
import sys
print(sys.meta_path)  # List of finders
print(sys.path_hooks)  # Functions that convert paths to finders
print(sys.modules)  # Currently loaded modules

# Look at a module's internals
import requests
print(requests.__spec__)  # Module spec
print(requests.__dict__.keys())  # Module namespace
```

### Import Behavior Examples

The repo contains two main package examples:

1. **examples_pkg**: Demonstrates conventional package structure with subpackages
   - Notice how imports work in `__init__.py` files
   - See how subpackages are made available through parent packages
   - Observe the role of `__all__` in controlling what's exposed

2. **pkg**: Shows lower-level details of the import system
   - Prints `sys.path`, `__name__`, and `__package__` to show import context
   - `b.py` demonstrates manual module importing using `importlib`

### Running the Examples

Run the main module to see imports in action:
```bash
python -m src.main
```

Run the manual import example:
```bash
cd src && python -m pkg.b
```

## Key Import System Concepts

### 1. Import Edge Cases and Gotchas

When working with Python's import system, be aware of these common pitfalls:

1. **Circular Imports**:
   - Two modules importing each other can cause problems
   - Solution: Move one import inside a function (lazy import)
   - Example: `a.py` imports `b.py`, which imports `a.py`

2. **Shadowed Imports**:
   - A local file with the same name as a standard library or installed package
   - Example: Creating a `requests.py` in your project breaks `import requests`
   - Python will import your local file instead of the package

3. **Relative Import Issues**:
   - Cannot use relative imports (`from ..module import x`) in scripts run directly
   - Only work inside packages when modules are properly imported

4. **`PYTHONPATH` Manipulation**:
   - Changes to `PYTHONPATH` affect all Python processes
   - Can lead to unexpected import behavior when set system-wide

5. **`__all__` Variables**:
   - Controls what is imported with `from module import *`
   - Does not affect direct imports like `from module import specific_thing`

6. **Import Side Effects**:
   - Code at the module level runs on import
   - Can lead to unexpected behavior or performance issues
   - Good practice: Use `if __name__ == '__main__'` for script behavior

7. **Namespace Packages (PEP 420)**:
   - Packages without `__init__.py` that span multiple directories
   - Parts can be installed in different locations but appear as one package

### 2. The `__init__.py` Files

- **Purpose**: Marks a directory as a package and initializes it
- **Behavior**: Executed when the package is imported
- **Usage in this repo**: 
  - `examples_pkg/__init__.py` demonstrates importing subpackages
  - Subpackage `__init__.py` files show adding modules to the package namespace

### 2. Import Resolution

- The `sys.path` list determines where Python looks for modules
- Absolute vs relative imports behave differently
- Package imports are resolved relative to the location of the importing module

### 3. Modern Python Packaging

- `pyproject.toml` replaces `setup.py` for configuring packages
- The `src/` layout pattern isolates package code from development code
- Editable installs with `-e` enable in-place development

### 4. Module Attributes

- `__name__`: Shows how a module was imported
- `__package__`: Indicates the package a module belongs to
- These change depending on how the module is run (directly vs imported)

### 5. Understanding `sys.path` in Different Contexts

How Python searches for modules varies dramatically depending on how code is executed:

#### Script Mode (`python script.py`)

When you run a Python file directly as a script:
- `sys.path[0]` is set to the directory containing the script
- The script's directory takes precedence in module searches
- Relative imports don't work at the top level (since the script isn't part of a package)
- Example: `python src/main.py` sets `sys.path[0]` to the `src/` directory

#### Module Mode (`python -m module`)

When you run a Python file using the `-m` flag:
- `sys.path[0]` is set to the current working directory
- The module is properly recognized as part of its package
- Relative imports work correctly
- `__name__` is set to `__main__` but `__package__` maintains the proper package name
- Example: `python -m pkg.b` sets proper package context while running as main

#### Import Context

When code is imported rather than executed directly:
- Module is loaded within its proper package hierarchy
- `__name__` reflects the fully qualified module name (e.g., `pkg.b`)
- `sys.path` is not modified by the import itself
- Relative imports resolve against the package structure

Try the different execution modes with this repo's modules to see these differences in action!

#### Demonstration in this Repo

This repository's code is specifically designed to show these differences:

```bash
# Script mode - Run main.py as a script
cd src
python main.py
# Notice import issues and sys.path differences

# Module mode - Run main.py as a module
cd ..
python -m src.main
# Notice how imports work correctly

# Compare running pkg/b.py directly vs as a module
cd src
python pkg/b.py  # Will likely fail due to import issues
python -m pkg.b  # Works correctly with proper package context
```

Look at the output in each case to see how `sys.path[0]`, `__name__`, and `__package__` differ!

## Tests

The tests in `tests/` demonstrate:
- How imported modules are accessible
- Package initialization behavior
- Module resolution through different import paths

## Learning Exercises

1. **Modify Import Behavior**: Try changing what's imported in `__init__.py` files and observe effects
2. **Import Path Exploration**: Run different modules directly vs importing them
3. **Manual Module Loading**: Expand the manual importing in `pkg/b.py`
4. **Add New Subpackages**: Create additional packages and observe import behavior

---

*This repository is for educational purposes, demonstrating Python's import system rather than providing useful functionality.*