from __future__ import absolute_import, print_function, unicode_literals

from pyparsing import alphanums, alphas, dblQuotedString, delimitedList, Dict, Forward, Group, Keyword, Literal, OneOrMore, printables, quotedString, removeQuotes, stringEnd, stringStart, Word

RULE = Forward()

labracket = Keyword('{').suppress()
rabracket = Keyword('}').suppress()

RULE_ELEMENT = Group(
    Keyword('with-interface') + labracket + Group(OneOrMore(Word(alphanums + ':'))) + rabracket |
    Word(alphas+'-') + quotedString.setParseAction(removeQuotes) |
    Word(alphas+'-') + Word(printables)
)

RULE << stringStart.suppress() + Word(printables) + Group(OneOrMore(RULE_ELEMENT)) + stringEnd.suppress()

if __name__ == "__main__":
    # parsed_rule = RULE.parseString('allow id 1d6b:0002 serial "0000:00:14.0" name "xHCI Host Controller" hash "Miigb8mx72Z0q6L+YMai0mDZSlYC8qiSMctoUjByF2o=" parent-hash "G1ehGQdrl3dJ9HvW9w2HdC//pk87pKzFE1WY25bq8k4=" with-interface 09:00:00')
    parsed_rule = RULE.parseString('block id 04f2:b2ea serial "" name "Integrated Camera" hash "18xYrZpFsIyYEyw3SqedfmQFkrnVcPmbyLZIVLeFPPs=" with-interface { 0e:01:00 0e:02:00 0e:02:00 0e:02:00 0e:02:00 0e:02:00 0e:02:00 }')
    print(parsed_rule.dump())
