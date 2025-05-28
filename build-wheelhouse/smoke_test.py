import importlib
from importlib.metadata import PackageNotFoundError, distribution


def find_module_from_dist(pkg_name: str, attr: str):
    """
    Find a module in a package distribution's top-level __init__.py file
    and retrieve an attribute from it.

    Parameters
    ----------
    pkg_name : str
        The name of the package to search for.
    attr : str
        The attribute to look for in the package's module, e.g., '__version__'.

    Returns
    -------
    tuple
        A tuple containing the module path and the value of the specified attribute.

    Raises
    ------
    ImportError
        If the package is not found or if the specified attribute does not exist.

    """
    try:
        dist = distribution(pkg_name)
    except PackageNotFoundError:
        raise ImportError(f"Package '{pkg_name}' is not installed")

    # Examine files in the distribution to find likely module paths
    candidate_paths = [path for path in dist.files if path.name == "__init__.py"]
    if not candidate_paths:
        raise ImportError(f"No __init__.py found in package '{pkg_name}'")

    # Find the shortest paths to the init files
    candidate_paths.sort(key=lambda p: len(p.parts))

    # Drop the paths that are longer than the shortest one
    shortest_length = len(candidate_paths[0].parts)
    candidate_paths = [
        path for path in candidate_paths if len(path.parts) == shortest_length
    ]

    # Try to import each parent package and check for the desired attribute
    for path in candidate_paths:
        import_path = ".".join(path.parent.parts)
        try:
            mod = importlib.import_module(import_path)
            if hasattr(mod, attr):
                return import_path, getattr(mod, attr)
        except Exception:
            continue

    raise ImportError(
        f"Could not find a module in '{pkg_name}' with attribute '{attr}'"
    )


###########################################################################################

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python smoke_test.py <package_name> [attribute_name]\n")
        print("Default attribute is '__version__'.\n")
        print("Example: python smoke_test.py my_package __version__")
        print("Example: python smoke_test.py my_package")
        sys.exit(1)

    package_name = sys.argv[1]
    attribute_name = sys.argv[2] if len(sys.argv) > 2 else "__version__"

    try:
        module_path, version = find_module_from_dist(package_name, attribute_name)
        print(f"Module path: {module_path}, {attribute_name}: {version}")
    except ImportError as e:
        print(e)
        sys.exit(1)
