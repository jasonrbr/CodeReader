# Test python file for parsing c++ code
from antlr4 import *
from MyGrammarLexer import MyGrammarLexer
from MyGrammarParser import MyGrammarParser


def main(argv):
    input = FileStream(argv[1])
    lexer = MyGrammarLexer(input)
    stream = CommonTokenStream(lexer)
    parser = MyGrammarParser(stream)
    tree = parser.StartRule()


if __name__ == '__main__':
    main(sys.argv)
