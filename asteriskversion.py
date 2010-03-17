#!/usr/bin/env python
'''
Copyright (C) 2010, Digium, Inc.
Russell Bryant <russell@digium.com>

This program is free software, distributed under the terms of
the GNU General Public License Version 2.
'''

import sys
import re
import unittest


VERSION_HDR = "/usr/include/asterisk/version.h"


class AsteriskVersion:
    def __init__(self, version=None):
        if version is not None:
            self.version_str = version
        else:
            self.version_str = self.__get_ast_version()

        if self.version_str[:3] == "SVN":
            self.__parse_svn_version()
        else:
            self.__parse_version()

    def __str__(self):
        return self.version_str

    def __cmp__(self, other):
        if self.svn or other.svn:
            print "ERROR: SVN version comparisons not yet implemented."
            return 0
        else:
            res = self.__cmp_version_part(self.concept, other.concept)
            if res != 0:
                return res

            res = self.__cmp_version_part(self.major, other.major)
            if res != 0:
                return res

            res = self.__cmp_version_part(self.minor, other.minor)
            if res != 0:
                return res

            return self.__cmp_version_part(self.patch, other.patch)

    @staticmethod
    def __cmp_version_part(selfpart, otherpart):
        if selfpart is None and otherpart is None:
            return 0
        if selfpart is None:
            return -1
        if otherpart is None:
            return 1
        return cmp(selfpart, otherpart)

    def __parse_version(self):
        self.svn = False
        parts = self.version_str.split(".")
        self.concept = parts[0]
        self.major = parts[1]
        try:
            self.minor = parts[2]
        except:
            self.minor = None
            self.patch = None
        if self.minor is not None:
            try:
                self.patch = parts[3]
            except:
                self.patch = None

    def __parse_svn_version(self):
        self.svn = True
        match = re.search(
                "SVN-(?P<branch>.*)-r(?P<revision>\d+M?)(?:-(?P<parent>.*))?",
                self.version_str
        )
        if match is not None:
            self.branch = match.group("branch")
            self.revision = match.group("revision")
            self.parent = match.group("parent")

    def __get_ast_version(self):
        '''
        Determine the version of Asterisk installed from the installed version.h.
        '''
        v = ""
        try:
            f = open(VERSION_HDR, "r")
        except:
            print "Failed to open %s to get Asterisk version." % VERSION_HDR
            return v

        match = re.search("ASTERISK_VERSION\s+\"(.*)\"", f.read())
        if match is not None:
            v = match.group(1)

        f.close()

        return v


class AsteriskVersionTests(unittest.TestCase):
    def test_version(self):
        v = AsteriskVersion("1.4.30")
        self.assertFalse(v.svn)
        self.assertEqual(str(v), "1.4.30")
        self.assertEqual(v.concept, "1")
        self.assertEqual(v.major, "4")
        self.assertEqual(v.minor, "30")

    def test_version2(self):
        v = AsteriskVersion("1.4.30.1")
        self.assertFalse(v.svn)
        self.assertEqual(str(v), "1.4.30.1")
        self.assertEqual(v.concept, "1")
        self.assertEqual(v.major, "4")
        self.assertEqual(v.minor, "30")
        self.assertEqual(v.patch, "1")

    def test_version3(self):
        v = AsteriskVersion("1.4")
        self.assertFalse(v.svn)
        self.assertEqual(str(v), "1.4")
        self.assertEqual(v.concept, "1")
        self.assertEqual(v.major, "4")

    def test_svn_version(self):
        v = AsteriskVersion("SVN-trunk-r252849")
        self.assertTrue(v.svn)
        self.assertEqual(str(v), "SVN-trunk-r252849")
        self.assertEqual(v.branch, "trunk")
        self.assertEqual(v.revision, "252849")

    def test_svn_version2(self):
        v = AsteriskVersion("SVN-branch-1.6.2-r245581M")
        self.assertTrue(v.svn)
        self.assertEqual(str(v), "SVN-branch-1.6.2-r245581M")
        self.assertEqual(v.branch, "branch-1.6.2")
        self.assertEqual(v.revision, "245581M")

    def test_svn_version3(self):
        v = AsteriskVersion("SVN-russell-cdr-q-r249059M-/trunk")
        self.assertTrue(v.svn)
        self.assertEqual(str(v), "SVN-russell-cdr-q-r249059M-/trunk")
        self.assertEqual(v.branch, "russell-cdr-q")
        self.assertEqual(v.revision, "249059M")
        self.assertEqual(v.parent, "/trunk")

    def test_svn_version4(self):
        v = AsteriskVersion("SVN-russell-rest-r12345")
        self.assertTrue(v.svn)
        self.assertEqual(str(v), "SVN-russell-rest-r12345")
        self.assertEqual(v.branch, "russell-rest")
        self.assertEqual(v.revision, "12345")

    def test_cmp(self):
        v1 = AsteriskVersion("1.4")
        v2 = AsteriskVersion("1.6.0")
        self.assertTrue(v1 < v2)

    def test_cmp2(self):
        v1 = AsteriskVersion("1.4")
        v2 = AsteriskVersion("1.4.15")
        self.assertTrue(v1 < v2)

    def test_cmp3(self):
        v1 = AsteriskVersion("1.4.30")
        v2 = AsteriskVersion("1.4.30.1")
        self.assertTrue(v1 < v2)

    def test_cmp4(self):
        v1 = AsteriskVersion("1.4")
        v2 = AsteriskVersion("1.4")
        self.assertTrue(v1 == v2)

    def test_cmp5(self):
        v1 = AsteriskVersion("1.6.0")
        v2 = AsteriskVersion("1.6.0")
        self.assertTrue(v1 == v2)

    def test_cmp6(self):
        v1 = AsteriskVersion("1.6.0.10")
        v2 = AsteriskVersion("1.6.0.10")
        self.assertTrue(v1 == v2)

    def test_cmp7(self):
        v1 = AsteriskVersion("1.8")
        v2 = AsteriskVersion("2.0")
        self.assertTrue(v1 < v2)


def main():
    unittest.main()


if __name__ == "__main__":
    main()