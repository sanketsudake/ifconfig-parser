"""
Copyright (c) 2015 by Armin Ronacher.

Some rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

    * The names of the contributors may not be used to endorse or
      promote products derived from this software without specific
      prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from __future__ import unicode_literals, print_function
from sre_compile import compile as sre_compile
from sre_constants import BRANCH, SUBPATTERN
from sre_parse import Pattern, SubPattern, parse


class _ScanMatch(object):
    def __init__(self, match, rule, start, end):
        self._match = match
        self._start = start
        self._end = end
        self._rule = rule

    def __getattr__(self, name):
        return getattr(self._match, name)

    def __group_proc(self, method, group):
        if group == 0:
            return method()
        if isinstance(group, basestring):
            return method(self._rule + '\x00' + group)
        real_group = self._start + group
        if real_group > self._end:
            raise IndexError('no such group')
        return method(real_group)

    def group(self, *groups):
        if len(groups) in (0, 1):
            return self.__group_proc(self._match.group, groups and groups[0] or
                                     0)
        return tuple(
            self.__group_proc(self._match.group, group) for group in groups)

    def groupdict(self, default=None):
        prefix = self._rule + '\x00'
        rv = {}
        for key, value in self._match.groupdict(default).items():
            if key.startswith(prefix):
                rv[key[len(prefix):]] = value
        return rv

    def span(self, group=0):
        return self.__group_proc(self._match.span, group)

    def groups(self):
        return self._match.groups()[self._start:self._end]

    def start(self, group=0):
        return self.__group_proc(self._match.start, group)

    def end(self, group=0):
        return self.__group_proc(self._match.end, group)

    def expand(self, template):
        raise RuntimeError('Unsupported on scan matches')


class ScanEnd(Exception):
    def __init__(self, pos):
        Exception.__init__(self, pos)
        self.pos = pos


class Scanner(object):
    def __init__(self, rules, flags=0):
        pattern = Pattern()
        pattern.flags = flags
        pattern.groups = len(rules) + 1
        _og = pattern.opengroup
        pattern.opengroup = lambda n: _og(n and '%s\x00%s' % (name, n) or n)

        self.rules = []
        subpatterns = []
        for group, (name, regex) in enumerate(rules, 1):
            last_group = pattern.groups - 1
            subpatterns.append(
                SubPattern(pattern, [(SUBPATTERN, (group, parse(regex, flags,
                                                                pattern))), ]))
            self.rules.append((name, last_group, pattern.groups - 1))
        self._scanner = sre_compile(
            SubPattern(pattern, [(BRANCH, (None, subpatterns))])).scanner

    def scan(self, string, skip=False):
        sc = self._scanner(string)

        match = None
        for match in iter(sc.search if skip else sc.match, None):
            rule, start, end = self.rules[match.lastindex - 1]
            yield rule, _ScanMatch(match, rule, start, end)

        if not skip:
            end = match and match.end() or 0
            if end < len(string):
                raise ScanEnd(end)

    def scan_with_holes(self, string):
        pos = 0
        for rule, match in self.scan(string, skip=True):
            hole = string[pos:match.start()]
            if hole:
                yield None, hole
            yield rule, match
            pos = match.end()
        hole = string[pos:]
        if hole:
            yield None, hole
