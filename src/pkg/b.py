import importlib
import sys

print("sys.path[0]:", sys.path[0])
print("__name__:", __name__)
print("__package__:", __package__)

if __name__ == "__main__":
    print("b.py is being run directly; importing `pkg.a` by hand")

    import importlib.util

    import pkg  # saves us a step of importing pkg to have a parent namespace

    ### Hand-importing `pkg.a` submodule
    # Find the module spec
    spec = importlib.util.find_spec("pkg.a")
    print(spec.origin)

    # Load the module spec
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Add module object to sys.modules dictionary
    sys.modules["pkg.a"] = module

    # Bind to `pkg` namespace
    pkg.a = module

    # Call function in hand-imported module
    pkg.a.f_in_a()
