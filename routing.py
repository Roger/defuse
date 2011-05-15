"""
this module it's based on werkzeug routing system:
https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/routing.py
"""
import re

_rule_re = re.compile(r'''
(?P<static>[^<]*) # static rule data
<
(?P<variable>[a-zA-Z][a-zA-Z0-9_]*) # variable name
>
''', re.VERBOSE)


def parse_rule(rule):
    """Parse a rule and return it as generator. Each iteration yields tuples
in the form ``(variable, static)``. If static is
`True` it's a static url part, otherwise it's a dynamic one.
"""
    pos = 0
    end = len(rule)
    do_match = _rule_re.match
    used_names = set()
    while pos < end:
        m = do_match(rule, pos)
        if m is None:
            break
        data = m.groupdict()
        static = data['static']
        if static:
            yield static, True

        variable = data['variable']
        if variable in used_names:
            raise ValueError('variable name %r used twice.' % variable)
        used_names.add(variable)
        yield variable, False
        pos = m.end()
    if pos < end:
        remaining = rule[pos:]
        if '>' in remaining or '<' in remaining:
            raise ValueError('malformed url rule: %r' % rule)
        yield remaining, True

class Rule(object):
    def __init__(self, string):
        self.rule = string
        self.compile()

    def compile(self):
        """Compiles the regular expression and stores it."""

        rule = self.rule
        self._trace = []
        self._weights = []

        regex_parts = []
        for variable, static in parse_rule(rule):
            if static:
                regex_parts.append(re.escape(variable))
            else:
                regex_parts.append('(?P<%s>%s)' % (variable, r'[^\/]+'))

        regex = r'^%s%s$' % (
            u''.join(regex_parts), ''
        )
        self._regex = re.compile(regex, re.UNICODE)

    def match(self, path):
        m = self._regex.search(path)
        if m is not None:
            groups = m.groupdict()
            result = {}
            for name, value in groups.iteritems():
                result[str(name)] = value
            return result


if __name__ == '__main__':
    print Rule('/dev/<null>/').match('/dev/null/')
    print Rule('/dev/<asd>/man/').match('/dev/GASS/man/')
    print Rule('/my/<mp3>.mp3').match('/my/lol.mp3')
    print Rule('/my/<mp3>.mp3').match('/my/ .mp3')
    print Rule('/my/<filename>.<ext>').match('/my/asd asd asas......mp3')
    print Rule('/my/<filename>').match('/my/asd asd asas......mp3')
    print Rule('/').match('/')
