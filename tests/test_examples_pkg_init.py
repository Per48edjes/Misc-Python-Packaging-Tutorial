import pytest
import sys
import os

# Ensure src is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import examples_pkg
import examples_pkg.subpkg1 as sp1
import examples_pkg.subpkg2 as sp2

import examples_pkg.subpkg1.module1 as m1
import examples_pkg.subpkg2.module2 as m2

def test_examples_pkg_all():
    # examples_pkg __all__ should be empty by default
    assert examples_pkg.__all__ == []


def test_direct_module_import():
    # direct import of module1 should succeed
    assert hasattr(m1, 'greet_subpkg1')
    m1.greet_subpkg1()


def test_indirect_module1_import_via_init():
    # accessing module1 via package attr should succeed after explicit import in __init__.py
    assert hasattr(sp1, 'module1')
    sp1.module1.greet_subpkg1()

def test_direct_module2_import():
    assert hasattr(m2, 'greet_subpkg2')
    m2.greet_subpkg2()


def test_indirect_module2_import_via_init():
    # accessing module2 via package attr should succeed after explicit import in __init__.py
    assert hasattr(sp2, 'module2')
    sp2.module2.greet_subpkg2()
