# src/main.py


def main():
    print("Running main.py")

    import examples_pkg
    import examples_pkg.subpkg1
    import pkg.b

    examples_pkg.subpkg1.module1.greet_subpkg1()
    examples_pkg.subpkg2.module2.greet_subpkg2()


if __name__ == "__main__":
    main()
