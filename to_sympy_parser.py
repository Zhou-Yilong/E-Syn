import ply.yacc as yacc
from sympy import symbols, And, Or, Not, Xor
from prop_lexer import PropLexer

class PropParser(object):
    tokens = PropLexer.tokens
    """
        id: symbol | ( prop )
        term : id
        prop: term
            | prop * prop
            | prop + prop
            | prop & prop
            | ! prop
    """

    # Parsing rules
    precedence = (
        ("left", "OR"),
        ("left", "AND"),
        ("left", "CONCAT"),
        ("right", "NOT"),
    )

    def __init__(self):
        self.lexer = PropLexer()
        self.lexer.build()
        self.atoms = {}
        self.concat_spliter = {}
        self.concat_spliter_id = 0

    # for parsing the proposition
    def p_prop_term(self, p):
        "prop : term"
        p[0] = p[1]

    def p_prop_and(self, p):
        "prop : prop AND prop"
        p[0] = And(p[1], p[3])

    def p_prop_or(self, p):
        "prop : prop OR prop"
        p[0] = Or(p[1], p[3])
        
    def p_prop_concat(self, p):
        "prop : prop CONCAT prop"
        p[0] = Xor(p[1], p[3])
        # if self.concat_spliter_id is 0, add p[1] and p[3] to concat_spliter
        if self.concat_spliter_id == 0:
            self.concat_spliter[self.concat_spliter_id] = p[1]
            self.concat_spliter[self.concat_spliter_id + 1] = p[3]
            self.concat_spliter_id += 2
        else:
            self.concat_spliter[self.concat_spliter_id] = p[3]
            self.concat_spliter_id += 1
        

    def p_prop_not(self, p):
        "prop : NOT prop"
        p[0] = Not(p[2])

    def p_term_id(self, p):
        "term : id"
        p[0] = p[1]

    def p_id_symbol(self, p):
        "id : SYMBOL"
        if p[1] not in self.atoms:
            self.atoms[p[1]] = symbols(p[1])
        p[0] = self.atoms[p[1]]

    def p_id_paren(self, p):
        "prop : LPAREN prop RPAREN"
        p[0] = p[2]

    def p_error(self, p):
        print("Syntax error at '%s'" % p)

    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, data):
        self.lexer.input(data)
        return self.parser.parse(data, lexer=self.lexer.lexer), self.concat_spliter

# test string
# parser = PropParser()
# parser.build()
# result = parser.parse("!( pi2 * pi3) + (pi1 * pi2)")
# print(result)
