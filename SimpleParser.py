import re

# Token specifications
TOKEN_SPECIFICATION = [
    ('KEYWORD', r'\b(თუ|თუარა|აი|დაბეჭდე)\b'),  # Keywords
    ('IDENTIFIER', r'[_\u10A0-\u10FF][_\u10A0-\u10FF0-9]*'),  # Identifiers (Georgian letters)
    ('NUMBER', r'\d+'),  # Integer numbers
    ('ASSIGNMENT', r'='),  # Assignment operator
    ('COMPARISON', r'==|!=|<=|>=|<|>'),  # Comparison operators
    ('OPERATOR', r'[+\-*/]'),  # Arithmetic operators
    ('BRACKET', r'[(){}]'),  # Parentheses and braces
    ('SEMICOLON', r';'),  # Semicolon
    ('COMMA', r','),  # Comma
    ('WHITESPACE', r'\s+'),  # Whitespace (to be skipped)
]

# Lexer function to tokenize the input code
def tokenize(code):
    token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)
    tokens = []
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup
        value = match.group(kind)
        if kind == 'WHITESPACE':
            continue  # Skip whitespace
        tokens.append((kind, value))
    return tokens

# Node class for building the Abstract Syntax Tree (AST)
class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children else []

    def __repr__(self):
        return f'Node({self.value}, {self.children})'

# Parser functions
def parse(tokens):
    tokens = tokens.copy()  # Create a copy to avoid modifying the original list
    position = [0]  # Using a list to make position mutable within nested functions

    def current_token():
        if position[0] < len(tokens):
            return tokens[position[0]]
        else:
            return None

    def consume(expected_kind=None, expected_value=None):
        token = current_token()
        if token is None:
            return None
        if expected_kind and token[0] != expected_kind:
            return None
        if expected_value and token[1] != expected_value:
            return None
        position[0] += 1
        return token

    def parse_factor():
        token = current_token()
        if token[0] == 'NUMBER' or token[0] == 'IDENTIFIER':
            consume()
            return Node(token[1])
        elif token[0] == 'BRACKET' and token[1] == '(':
            consume('BRACKET', '(')
            node = parse_expression()
            consume('BRACKET', ')')
            return node
        else:
            return None

    def parse_term():
        node = parse_factor()
        while True:
            token = current_token()
            if token and token[0] == 'OPERATOR' and token[1] in ('*', '/'):
                consume()
                right = parse_factor()
                node = Node(token[1], [node, right])
            else:
                break
        return node

    def parse_expression():
        node = parse_term()
        while True:
            token = current_token()
            if token and token[0] == 'OPERATOR' and token[1] in ('+', '-'):
                consume()
                right = parse_term()
                node = Node(token[1], [node, right])
            else:
                break
        return node

    def parse_condition():
        node = parse_expression()
        token = current_token()
        if token and token[0] == 'COMPARISON':
            consume()
            right = parse_expression()
            node = Node(token[1], [node, right])
        return node

    def parse_statement():
        token = current_token()
        if token is None:
            return None

        # Variable declaration
        if token[0] == 'KEYWORD' and token[1] == 'აი':
            consume('KEYWORD', 'აი')
            identifier = consume('IDENTIFIER')
            consume('ASSIGNMENT', '=')
            expr = parse_expression()
            consume('SEMICOLON', ';')
            return Node('Declaration', [Node(identifier[1]), expr])

        # Assignment
        elif token[0] == 'IDENTIFIER':
            identifier = consume('IDENTIFIER')
            consume('ASSIGNMENT', '=')
            expr = parse_expression()
            consume('SEMICOLON', ';')
            return Node('Assignment', [Node(identifier[1]), expr])

        # If statement
        elif token[0] == 'KEYWORD' and token[1] == 'თუ':
            consume('KEYWORD', 'თუ')
            consume('BRACKET', '(')
            condition = parse_condition()
            consume('BRACKET', ')')
            consume('BRACKET', '{')
            true_branch = []
            while current_token() and not (current_token()[0] == 'BRACKET' and current_token()[1] == '}'):
                stmt = parse_statement()
                if stmt:
                    true_branch.append(stmt)
            consume('BRACKET', '}')
            false_branch = []
            if current_token() and current_token()[0] == 'KEYWORD' and current_token()[1] == 'თუარა':
                consume('KEYWORD', 'თუარა')
                consume('BRACKET', '{')
                while current_token() and not (current_token()[0] == 'BRACKET' and current_token()[1] == '}'):
                    stmt = parse_statement()
                    if stmt:
                        false_branch.append(stmt)
                consume('BRACKET', '}')
            return Node('If', [condition, Node('TrueBranch', true_branch), Node('FalseBranch', false_branch)])

        # Print statement
        elif token[0] == 'KEYWORD' and token[1] == 'დაბეჭდე':
            consume('KEYWORD', 'დაბეჭდე')
            consume('BRACKET', '(')
            expr = parse_expression()
            consume('BRACKET', ')')
            consume('SEMICOLON', ';')
            return Node('Print', [expr])

        else:
            # Unrecognized statement
            return None

    # Main parsing loop
    root = Node('Program')
    while position[0] < len(tokens):
        stmt = parse_statement()
        if stmt:
            root.children.append(stmt)
        else:
            # Skip unrecognized tokens or handle errors
            break

    return root

# Main execution
if __name__ == "__main__":
    code = """
        აი ი = 37;
        აი ა = 77;
        თუ (ა >= 10) {
            ა = ი + 5;
        } თუარა {
            ა = ი - 5;
        }
        დაბეჭდე(ა);
    """
    tokens = tokenize(code)
    print("Tokens:", tokens)
    ast = parse(tokens)
    print("Abstract Syntax Tree:", ast)