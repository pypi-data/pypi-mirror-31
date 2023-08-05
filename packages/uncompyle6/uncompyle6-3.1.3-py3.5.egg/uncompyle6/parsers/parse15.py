#  Copyright (c) 2016 Rocky Bernstein
#  Copyright (c) 2000-2002 by hartmut Goebel <hartmut@goebel.noris.de>

from spark_parser import DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG
from uncompyle6.parser import PythonParserSingle
from uncompyle6.parsers.parse21 import Python21Parser

class Python15Parser(Python21Parser):

    def __init__(self, debug_parser=PARSER_DEFAULT_DEBUG):
        super(Python15Parser, self).__init__(debug_parser)
        self.customized = {}

    def p_import15(self, args):
        """
        import      ::= filler IMPORT_NAME STORE_FAST
        import      ::= filler IMPORT_NAME STORE_NAME

        import_from ::= filler IMPORT_NAME importlist
        import_from ::= filler filler IMPORT_NAME importlist POP_TOP

        importlist  ::= importlist IMPORT_FROM
        importlist  ::= IMPORT_FROM
        """

class Python15ParserSingle(Python21Parser, PythonParserSingle):
    pass

if __name__ == '__main__':
    # Check grammar
    p = Python15Parser()
    p.check_grammar()
    p.dump_grammar()

# local variables:
# tab-width: 4
