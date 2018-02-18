#!/usr/bin/env python
"""Test the loading of all optional GO term attributes.

Maximum number of fields on a GO term:

  required:
      1 name
      1 namespace
     10 is_a
     16 alt_id

  optional scalar:
      1 def
      1 comment

  optional set:
     12 subset    goslim_mouse

  optional special:
      3 relationship
    284 synonym   synonym: "peptidase inhibitor complex" EXACT [GOC:bf, GOC:pr]
    827 xref      Wikipedia:Zygotene


In go-basic.obo fmt(1.2) rel(2018-02-11) 15,329 out of 47,120 GO Terms have synonym types:
  90444 EXACT
  18574 NARROW
  15037 RELATED
   3562 BROAD
"""

from __future__ import print_function

import sys
from goatools.test_data.optional_attrs import OptionalAttrs


def test_optional_attrs():
    """Test loading optional GO term field, 'synonym'."""
    prt = sys.stdout
    prt = None
    # Summary for all fields in a GO DAG
    opt_attrs = ['def', 'comment', 'subset', 'synonym', 'xref', 'relationship']
    obj = OptionalAttrs("go-basic.obo", opt_attrs)
    obj.prt_summary()

    # SCALAR: Check optional attributes whose information is stored in string
    for attr in ['def', 'comment']:
        # Check that all GO IDs that should have relationships do have relationships.
        obj.chk_cnt_go(attr)
        print("PASSED: {ATTR}".format(ATTR=attr))

    # SET: Check optional attributes whose information is stored in a set
    for attr in ['subset', 'synonym', 'xref']:
        # Check that all GO IDs that should have relationships do have relationships.
        obj.chk_cnt_go(attr)
        # For each GO ID, check that actual count of a set attr equals expected count
        obj.chk_cnt_set(attr)
        print("PASSED: {ATTR}".format(ATTR=attr))

    # RELATIONSHIP: Stored in a dict with values being sets
    obj.chk_cnt_go('relationship')
    obj.chk_cnt_relationship()
    print("PASSED: relationship")

    # SYNONYM: Stored in a namedtuple
    obj.chk_synonyms(prt)
    print("PASSED: synonyms")


def test_no_optional_attrs():
    """Test loading DAG with no optional attributes."""
    OptionalAttrs("go-basic.obo", None)
    OptionalAttrs("go-basic.obo", [])
    OptionalAttrs("go-basic.obo", set([]))


if __name__ == '__main__':
    #test_no_optional_attrs()
    test_optional_attrs()

# Copyright (C) 2010-2018, H Tang et al., All rights reserved.