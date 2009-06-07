# Unit Name: dupeguru.tests.ignore_test
# Created By: Virgil Dupras
# Created On: 2006/05/02
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import cStringIO
import xml.dom.minidom

from nose.tools import eq_

from ..ignore import *

def test_empty():
    il = IgnoreList()
    eq_(0,len(il))
    assert not il.AreIgnored('foo','bar')

def test_simple():
    il = IgnoreList()
    il.Ignore('foo','bar')
    assert il.AreIgnored('foo','bar')
    assert il.AreIgnored('bar','foo')
    assert not il.AreIgnored('foo','bleh')
    assert not il.AreIgnored('bleh','bar')
    eq_(1,len(il))

def test_multiple():
    il = IgnoreList()
    il.Ignore('foo','bar')
    il.Ignore('foo','bleh')
    il.Ignore('bleh','bar')
    il.Ignore('aybabtu','bleh')
    assert il.AreIgnored('foo','bar')
    assert il.AreIgnored('bar','foo')
    assert il.AreIgnored('foo','bleh')
    assert il.AreIgnored('bleh','bar')
    assert not il.AreIgnored('aybabtu','bar')
    eq_(4,len(il))

def test_clear():
    il = IgnoreList()
    il.Ignore('foo','bar')
    il.Clear()
    assert not il.AreIgnored('foo','bar')
    assert not il.AreIgnored('bar','foo')
    eq_(0,len(il))

def test_add_same_twice():
    il = IgnoreList()
    il.Ignore('foo','bar')
    il.Ignore('bar','foo')
    eq_(1,len(il))

def test_save_to_xml():
    il = IgnoreList()
    il.Ignore('foo','bar')
    il.Ignore('foo','bleh')
    il.Ignore('bleh','bar')
    f = cStringIO.StringIO()
    il.save_to_xml(f)
    f.seek(0)
    doc = xml.dom.minidom.parse(f)
    root = doc.documentElement
    eq_('ignore_list',root.nodeName)
    children = [c for c in root.childNodes if c.localName]
    eq_(2,len(children))
    eq_(2,len([c for c in children if c.nodeName == 'file']))
    f1,f2 = children
    subchildren = [c for c in f1.childNodes if c.localName == 'file'] +\
        [c for c in f2.childNodes if c.localName == 'file']
    eq_(3,len(subchildren))

def test_SaveThenLoad():
    il = IgnoreList()
    il.Ignore('foo','bar')
    il.Ignore('foo','bleh')
    il.Ignore('bleh','bar')
    il.Ignore(u'\u00e9','bar')
    f = cStringIO.StringIO()
    il.save_to_xml(f)
    f.seek(0)
    il = IgnoreList()
    il.load_from_xml(f)
    eq_(4,len(il))
    assert il.AreIgnored(u'\u00e9','bar')
    
def test_LoadXML_with_empty_file_tags():
    f = cStringIO.StringIO()
    f.write('<?xml version="1.0" encoding="utf-8"?><ignore_list><file><file/></file></ignore_list>')
    f.seek(0)
    il = IgnoreList()
    il.load_from_xml(f)
    eq_(0,len(il))
    
def test_AreIgnore_works_when_a_child_is_a_key_somewhere_else():
    il = IgnoreList()
    il.Ignore('foo','bar')
    il.Ignore('bar','baz')
    assert il.AreIgnored('bar','foo')


def test_no_dupes_when_a_child_is_a_key_somewhere_else():
    il = IgnoreList()
    il.Ignore('foo','bar')
    il.Ignore('bar','baz')
    il.Ignore('bar','foo')
    eq_(2,len(il))

def test_iterate():
    #It must be possible to iterate through ignore list
    il = IgnoreList()
    expected = [('foo','bar'),('bar','baz'),('foo','baz')]
    for i in expected:
        il.Ignore(i[0],i[1])
    for i in il:
        expected.remove(i) #No exception should be raised
    assert not expected #expected should be empty

def test_filter():
    il = IgnoreList()
    il.Ignore('foo','bar')
    il.Ignore('bar','baz')
    il.Ignore('foo','baz')
    il.Filter(lambda f,s: f == 'bar')
    eq_(1,len(il))
    assert not il.AreIgnored('foo','bar')
    assert il.AreIgnored('bar','baz')

def test_save_with_non_ascii_non_unicode_items():
    il = IgnoreList()
    il.Ignore('\xac','\xbf')
    f = cStringIO.StringIO()
    try:
        il.save_to_xml(f)
    except Exception as e:
        raise AssertionError(unicode(e))

def test_len():
    il = IgnoreList()
    eq_(0,len(il))
    il.Ignore('foo','bar')
    eq_(1,len(il))

def test_nonzero():
    il = IgnoreList()
    assert not il
    il.Ignore('foo','bar')
    assert il
