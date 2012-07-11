# encoding: utf-8
#pylint: disable=R0904
""" The eaglexml writer test class """

# upconvert.py - A universal hardware design file format converter using
# Format:       upverter.com/resources/open-json-format/
# Development:  github.com/upverter/schematic-file-converter
#
# Copyright 2011 Upverter, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from upconvert.parser.t.eaglexml_t import get_design
from upconvert.writer.eaglexml import EagleXML

from functools import wraps

import os
import unittest
import tempfile


_cache = {} # filename -> DOM

def get_dom(filename):
    if filename not in _cache:
        design = get_design(filename)
        _cache[filename] = EagleXML().make_dom(design)
    return _cache[filename]


def use_file(filename):
    """ Return a decorator which will parse a gerber file
    before running the test. """

    def decorator(test_method):
        """ Add params to decorator function. """

        @wraps(test_method)
        def wrapper(self):
            """ Parse file then run test. """
            self.design = get_design(filename)
            self.dom = get_dom(filename)
            test_method(self)

        return wrapper

    return decorator


class EagleXMLTests(unittest.TestCase):
    """ The tests of the eaglexml writer """

    @use_file('E1AA60D5.sch')
    def test_write(self):
        """
        We can write out a complete design file.
        """

        writer = EagleXML()
        filedesc, filename = tempfile.mkstemp()
        os.close(filedesc)
        os.remove(filename)
        writer.write(self.design, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)


    @use_file('E1AA60D5.sch')
    def test_libraries(self):
        """
        The correct libraries are generated.
        """

        libnames = [lib.name for lib
                    in self.dom.drawing.schematic.libraries.library]
        self.assertTrue('atmel' in libnames, libnames)


    @use_file('E1AA60D5.sch')
    def test_devicesets(self):
        """
        The correct devicesets are generated.
        """

        lib = [lib for lib in self.dom.drawing.schematic.libraries.library
               if lib.name == 'atmel'][0]
        dsnames = [ds.name for ds in lib.devicesets.deviceset]
        self.assertTrue('TINY15L' in dsnames, dsnames)


    @use_file('E1AA60D5.sch')
    def test_parts(self):
        """
        The correct parts are generated.
        """

        parts = self.dom.drawing.schematic.parts
        names = [p.name for p in parts.part]
        self.assertTrue('R1' in names, names)


    @use_file('E1AA60D5.sch')
    def test_symbols(self):
        """
        The correct symbols are generated.
        """

        lib = [lib for lib
               in self.dom.drawing.schematic.libraries.library
               if lib.name == 'transistor-pnp'][0]
        self.assertEqual(len(lib.symbols.symbol), 1)
        self.assertEqual(lib.symbols.symbol[0].name, 'PNP')


    @use_file('E1AA60D5.sch')
    def test_symbol_wires(self):
        """
        The correct symbol wires are generated.
        """

        lib = [lib for lib
               in self.dom.drawing.schematic.libraries.library
               if lib.name == 'transistor-pnp'][0]
        sym = lib.symbols.symbol[0]
        self.assertEqual(len(sym.wire), 11)
        wire = sym.wire[0]
        self.assertEqual(wire.x1, 2.117)
        self.assertEqual(wire.y1, 1.693)
        self.assertEqual(wire.x2, 1.552)
        self.assertEqual(wire.y2, 2.54)


    @use_file('E1AA60D5.sch')
    def test_symbol_rectangles(self):
        """
        The correct symbol wires are generated.
        """

        lib = [lib for lib
               in self.dom.drawing.schematic.libraries.library
               if lib.name == 'transistor-pnp'][0]
        sym = lib.symbols.symbol[0]
        self.assertEqual(len(sym.rectangle), 1)
        rect = sym.rectangle[0]
        self.assertEqual(rect.x1, -0.282)
        self.assertEqual(rect.y1, -2.54)
        self.assertEqual(rect.x2, 0.565)
        self.assertEqual(rect.y2, 2.54)


    @use_file('E1AA60D5.sch')
    def test_nets(self):
        """
        The correct nets are generated.
        """

        nets = self.dom.drawing.schematic.sheets.sheet[0].nets
        names = [n.name for n in nets.net]
        self.assertTrue('GND' in names, names)


    @use_file('E1AA60D5.sch')
    def test_segments(self):
        """
        The correct segments are generated.
        """

        nets = self.dom.drawing.schematic.sheets.sheet[0].nets
        gnd = [n for n in nets.net if n.name == 'GND'][0]
        self.assertEqual(len(gnd.segment), 7)


    @use_file('E1AA60D5.sch')
    def test_segment_wires(self):
        """
        The correct wires in segments are generated.
        """

        nets = self.dom.drawing.schematic.sheets.sheet[0].nets
        net = [n for n in nets.net if n.name == 'N$7'][0]
        self.assertEqual(len(net.segment), 1)
        seg = net.segment[0]
        self.assertEqual(len(seg.wire), 2)
        self.assertEqual(seg.wire[0].x1, 76.2)
        self.assertEqual(seg.wire[0].y1, 68.58)
        self.assertEqual(seg.wire[0].x2, 83.82)
        self.assertEqual(seg.wire[0].y2, 68.58)
        self.assertEqual(seg.wire[1].x1, 83.82)
        self.assertEqual(seg.wire[1].y1, 48.26)
        self.assertEqual(seg.wire[1].x2, 83.82)
        self.assertEqual(seg.wire[1].y2, 68.58)


    @use_file('E1AA60D5.sch')
    def test_segment_pinrefs(self):
        """
        The correct pinrefs in segments are generated.
        """

        nets = self.dom.drawing.schematic.sheets.sheet[0].nets
        net = [n for n in nets.net if n.name == 'N$7'][0]
        self.assertEqual(len(net.segment), 1)
        seg = net.segment[0]
        self.assertEqual(len(seg.pinref), 2)
        self.assertEqual(seg.pinref[0].part, 'IC1')
        self.assertEqual(seg.pinref[0].gate, 'G$1')
        self.assertEqual(seg.pinref[0].pin, '(ADC1)PB2')
        self.assertEqual(seg.pinref[1].part, 'R3')
        self.assertEqual(seg.pinref[1].gate, 'G$1')
        self.assertEqual(seg.pinref[1].pin, '2')
