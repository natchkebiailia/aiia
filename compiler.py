import sys
import re

# Node class represents nodes in the AST
class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children else []

    def __repr__(self):
        return f'Node({self.value}, {self.children})'

    def pretty_print(self, indent=0, is_last=True, prefix=""):
        """Recursively prints the AST with ASCII visual formatting."""
        # Determine the connector based on whether this node is the last child
        connector = "└── " if is_last else "├── "
        # Print current node with appropriate prefix and connector
        print(f"{prefix}{connector}{self.value}")
        # Update prefix for children: add "|   " if this node is not the last, else "    "
        new_prefix = prefix + ("    " if is_last else "│   ")
        # Print children recursively
        child_count = len(self.children)
        for i, child in enumerate(self.children):
            is_last_child = (i == child_count - 1)
            if isinstance(child, Node):
                child.pretty_print(indent + 1, is_last_child, new_prefix)
            else:
                print(f"{new_prefix}{'└── ' if is_last_child else '├── '}{child}")


# Tokenizer class handles lexical analysis, splitting code into tokens.
class Tokenizer:
    TOKEN_PATTERNS = [
        ('COMMENT',     r'//.*'),                      # Single-line comment
        ('NUMBER',      r'\d+'),                       # Integer
        ('KEYWORD',     r'\b(თუ|თუარა|აი|დაბეჭდე)\b'), # Reserved words
        ('IDENTIFIER',  r'[_\u10A0-\u10FF][_\u10A0-\u10FF0-9]*'),  # Identifiers
        ('COMPARISON',  r'==|!=|<=|>=|<|>'),          # Comparison operators
        ('ASSIGNMENT',  r'='),                        # Assignment operator
        ('OPERATOR',    r'[+\-*/]'),                  # Arithmetic operators
        ('BRACKET',     r'[(){}]'),                   # Brackets
        ('SEMICOLON',   r';'),                        # Semicolon
        ('WHITESPACE',  r'\s+'),                      # Whitespace
    ]

    def __init__(self, code):
        self.code = code
        self.token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in self.TOKEN_PATTERNS)

    def tokenize(self):
        tokens = []
        for match in re.finditer(self.token_regex, self.code):
            kind = match.lastgroup
            value = match.group(kind)
            if kind not in ('WHITESPACE', 'COMMENT'):
                tokens.append((kind, value))
        return tokens

# Parser class processes tokens into an abstract syntax tree (AST).
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def consume(self, expected_type=None, expected_value=None):
        token = self.current_token()
        if token is None or (expected_type and token[0] != expected_type) or (expected_value and token[1] != expected_value):
            return None
        self.position += 1
        return token

    def parse_statement(self):
        token = self.current_token()
        if token is None:
            return None

        # Variable declaration
        if token[0] == 'KEYWORD' and token[1] == 'აი':
            self.consume('KEYWORD', 'აი')
            identifier = self.consume('IDENTIFIER')
            self.consume('ASSIGNMENT', '=')
            expr = self.parse_expression()
            self.consume('SEMICOLON', ';')
            return Node('Declaration', [identifier, expr])

        # Assignment
        if token[0] == 'IDENTIFIER':
            identifier = self.consume('IDENTIFIER')
            self.consume('ASSIGNMENT', '=')
            expr = self.parse_expression()
            self.consume('SEMICOLON', ';')
            return Node('Assignment', [identifier, expr])

        self.consume()
        return Node('Unknown', [])

    def parse_factor(self):
        token = self.current_token()
        if token[0] in ('NUMBER', 'IDENTIFIER'):
            self.consume()
            return Node(token[1])
        elif token[0] == "BRACKET" and token[1] == "(":
            self.consume("BRACKET", "(")
            node = self.parse_expression()
            self.consume("BRACKET", ")")
            return node
        else:
            return None

    def parse_term(self):
        node = self.parse_factor()
        while True:
            token = self.current_token()
            if token and token[0] == "OPERATOR" and token[1] in ("*", "/"):
                self.consume()
                right = self.parse_factor()
                node = Node(token[1], [node, right])
            else:
                break
        return node

    def parse_expression(self):
        node = self.parse_term()
        while True:
            token = self.current_token()
            if token and token[0] == "OPERATOR" and token[1] in ("+", "-"):
                self.consume()
                right = self.parse_term()
                node = Node(token[1], [node, right])
            else:
                break
        return node

    def parse(self):
        root = Node("Program")
        while self.position < len(self.tokens):
            stmnt = self.parse_statement()
            if stmnt:
                root.children.append(stmnt)
        return root

# Main function to orchestrate reading, tokenizing, parsing, and output.
def main():
    if len(sys.argv) < 2:
        print("Please provide a filename.")
        return

    input_filename = sys.argv[1]
    content = read_file(input_filename)
    tokenizer = Tokenizer(content)
    tokens = tokenizer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    ast.pretty_print()

# Utility function to read file content.
def read_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()

if __name__ == "__main__":
    main()
