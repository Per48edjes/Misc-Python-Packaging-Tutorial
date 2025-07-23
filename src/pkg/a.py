import sys

print("sys.path[0]:", sys.path[0])
print("__name__:", __name__)
print("__package__:", __package__)


def f_in_a():
    print("f_in_a called")
    return "Hello from a.py"
