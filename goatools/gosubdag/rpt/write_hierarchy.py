"""Print a GO term's lower-level hierarchy."""

__copyright__ = "Copyright (C) 2016-2018, DV Klopfenstein, H Tang. All rights reserved."
__author__ = "DV Klopfenstein"

import sys
import collections as cx
from goatools.godag.consts import Consts
from goatools.gosubdag.go_paths import GoPaths


class WrHierGO(object):
    """Write hierarchy object."""

    kws_dct = set(['max_indent'])
    kws_set = set(['no_indent', 'concise'])
    consts = Consts()

    def __init__(self, gosubdag, **kws):
        self.gosubdag = gosubdag  # GoSubDag arg, children=True, must be used
        self.usrdct = {k:v for k, v in kws.items() if k in kws}
        self.usrset = set([k for k, v in kws.items() if k in kws and v])
        # ' {NS} {dcnt:6,} L{level:02} D{depth:02} {D1:5} {GO_name}'

    def prt_hier_all(self, prt=sys.stdout):
        """Write hierarchy for all GO Terms in obo file."""
        # Print: [biological_process, molecular_function, and cellular_component]
        gos_printed = set()
        for goid in ['GO:0008150', 'GO:0003674', 'GO:0005575']:
            gos_printed.update(self.prt_hier_down(goid, prt))
        return gos_printed

    def prt_hier_down(self, goid, prt=sys.stdout):
        """Write hierarchy for all GO IDs below GO ID in arg, goid."""
        obj = _WrHierPrt(self, prt)
        obj.prt_hier_rec(goid)
        return obj.gos_printed

    def prt_hier_up(self, goids, prt=sys.stdout):
        """Write hierarchy for all GO IDs below GO ID in arg, goid."""
        go2goterm_all = {go:self.gosubdag.go2obj[go] for go in goids}
        objp = GoPaths()
        gos_printed = set()
        for namespace, go2term_ns in self._get_namespace2go2term(go2goterm_all).items():
            go_root = self.consts.NAMESPACE2GO[namespace]
            goids_all = set()  # GO IDs from user-specfied GO to root
            for goid, goterm in go2term_ns.items():
                goids_all.add(goid)
                paths = objp.get_paths_from_to(goterm, goid_end=None, dn0_up1=True)
                goids_all.update(set(o.id for p in paths for o in p))
            # Only include GO IDs from user-specified GO to the root
            if 'include_only' not in self.usrdct:
                self.usrdct['include_only'] = set()
            self.usrdct['include_only'].update(goids_all)
            # Mark the user-specfied GO term
            if 'go_marks' not in self.usrdct:
                self.usrdct['go_marks'] = set()
            self.usrdct['go_marks'].update(go2term_ns.keys())
            obj = _WrHierPrt(self, prt)  # , goids_all, set(go2term_ns.keys()))
            gos_printed.update(obj.gos_printed)
            obj.prt_hier_rec(go_root)
        return gos_printed

    @staticmethod
    def _get_namespace2go2term(go2terms):
        """Group GO IDs by namespace."""
        namespace2go2term = cx.defaultdict(dict)
        for goid, goterm in go2terms.items():
            namespace2go2term[goterm.namespace][goid] = goterm
        return namespace2go2term


# pylint: disable=too-many-instance-attributes,too-few-public-methods
class _WrHierPrt(object):
    """Print GO hierarchy."""

    def __init__(self, obj, prt=sys.stdout):
        self.gosubdag = obj.gosubdag
        self.max_indent = obj.usrdct.get('max_indent')
        self.include_only = obj.usrdct['include_only'] if 'include_only' in obj.usrdct else None
        self.go_marks = obj.usrdct['go_marks'] if 'go_marks' in obj.usrdct else set()
        self.concise_prt = 'concise' in obj.usrset
        self.indent = 'no_indent' not in obj.usrset
        # vars
        self.prt = prt
        self.gos_printed = set()
        self.prtfmt = self._init_prtfmt()
        self.dash_len = obj.usrdct.get('dash_len', 6) + 12

    def prt_hier_rec(self, goid, depth=1):
        """Write hierarchy for a GO Term record and all GO IDs down to the leaf level."""
        ntgo = self.gosubdag.go2nt[goid]
        ntobj = self.gosubdag.go2obj[goid]
        # Shortens hierarchy report by only printing the hierarchy
        # for the sub-set of user-specified GO terms which are connected.
        if self.include_only and goid not in self.include_only:
            return
        nrp = self.concise_prt and goid in self.gos_printed
        if self.go_marks:
            self.prt.write('{} '.format('>' if goid in self.go_marks else ' '))

        # '-' is default character indicating hierarchy level
        # '=' is used to indicate a hierarchical path printed in detail previously.
        dashgo = self._str_dashgoid(ntgo, depth, not nrp or not ntobj.children)
        self.prt.write('{DASHGO:{N}}'.format(DASHGO=dashgo, N=self.dash_len))

        self.prt.write("{GO_INFO}\n".format(GO_INFO=self.prtfmt.format(**ntgo._asdict())))
        self.gos_printed.add(goid)
        # Do not print hierarchy below this turn if it has already been printed
        if nrp:
            return
        depth += 1
        if self.max_indent is not None and depth > self.max_indent:
            return
        for child in ntobj.children:
            self.prt_hier_rec(child.id, depth)

    @staticmethod
    def _str_dash(depth, single_or_double):
        """Return a string containing dashes (optional) and GO ID."""
        # '-' is default character indicating hierarchy level
        # '=' is used to indicate a hierarchical path printed in detail previously.
        letter = '-' if single_or_double else '='
        return ''.join([letter]*depth)

    def _str_dashgoid(self, ntgo, depth, single_or_double):
        """Return a string containing dashes (optional) and GO ID."""
        dashes = self._str_dash(depth, single_or_double) if self.indent else ""
        return "{DASHES} {GO}{alt:1}".format(DASHES=dashes, GO=ntgo.GO, alt=ntgo.alt)

    def _init_prtfmt(self):
        """Initialize print format."""
        prtfmt = self.gosubdag.prt_attr['fmt']
        prtfmt = prtfmt.replace('{GO} # ', '')
        prtfmt = prtfmt.replace('{D1:5} ', '')
        return prtfmt

#### Examples:
####
#### Print the GO IDs associated with human genes
#### >>> python scripts/wr_hier.py BP --gene2go=gene2go --taxid=9606 --concise -o BP_9606.txt
####
#### Print the hierarchy below Term, GO:0030663
#### >>> python {SCR} GO:0030663
####
#### - GO:0030663	level-05	depth-07	COPI-coated vesicle membrane [cellular_component]
#### -- GO:0012508	level-05	depth-08	Golgi to ER transport vesicle membrane [cellular_component]
#### -- GO:0012509	level-05	depth-08	inter-Golgi transport vesicle membrane [cellular_component]
####
####
#### Write the hierarchy below Term, GO:0030663 into a file
#### >>> python {SCR} GO:0030663 --o=hier_GO_0030663.rpt
####
####   WROTE: hier_GO_0030663.rpt
####
#### Print the hierarchy for biological process, molecular_function, and cellular_component:
#### >>> python {SCR} --o=hier_BP_MF_CC.rpt
####
#### Print hierarchy for BP, MF, CC only printing the first 2 levels.
#### >>> python {SCR} --max_indent=2
#### >>> python {SCR} --max_indent=2 --dash_len=2
####
####
#### Print a conciseened version of the hierarchy for BP, MF, and CC.
#### This will only print a path to a leaf GO Term once.
#### If the path appears a second time, the term is printed again, but its path is not.
#### The presence of a compressed (unprinted) paths is marked by using '=" instead of '-'.
####
####     $ wc -l hier_BP_MF_CC*.rpt
####
####           789583 hier_BP_MF_CC.rpt
####            70152 hier_BP_MF_CC_concise.rpt
####
#### >>> python {SCR} --o=hier_BP_MF_CC_concise.rpt --concise
####
#### Print hierarchy
#### -  26894 GO:0008150	level-00	depth-00	biological_process [biological_process]
#### --    30 GO:0001906	level-01	depth-01	cell killing [biological_process]
#### --   555 GO:0002376	level-01	depth-01	immune system process [biological_process]
#### -- 11208 GO:0065007	level-01	depth-01	biological regulation [biological_process]
####
#### >>> python {SCR}
####
#### This program prints the hierarchy for all GO terms, if no argument is provided.
#### If a GO term is provided as an argument, then the hierarchy of all children
#### for that term is printed.
####
#### """.format(SCR='write_hierarchy')


# Copyright (C) 2016-2018, DV Klopfenstein, H Tang. All rights reserved.
