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

class DeclarationNode(Node):
    def __init__(self, identifier, expression):
        super().__init__('Declaration', [identifier, expression])

class AssignmentNode(Node):
    def __init__(self, identifier, expression):
        super().__init__('Assignment', [identifier, expression])

class BinaryOperationNode(Node):
    def __init__(self, operator, left, right):
        super().__init__(operator, [left, right])

class ValueNode(Node):
    def __init__(self, value):
        super().__init__(value)

class FunctionNode(Node):
    def __init__(self, name, parameters, body):
        super().__init__('Function', [name] + parameters + [body])
        self.name = name
        self.parameters = parameters
        self.body = body

# Symbol Table to store variables and functions
class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def declare(self, name, value):
        """Declare a symbol with a given name and value. If it's already declared, raise an error."""
        if not isinstance(name, str) or not name.isidentifier():
            raise ValueError(f"Invalid symbol name: '{name}'. Name must be a valid identifier.")
        
        if name in self.symbols:
            raise ValueError(f"Symbol '{name}' has already been declared. Use 'assign' for reassignment.")
        
        # Declare the new symbol
        self.symbols[name] = value

    def assign(self, name, value):
        """Assign a value to an existing variable. The variable must already be declared."""
        if name not in self.symbols:
            raise KeyError(f"Symbol '{name}' has not been declared yet. Use 'declare' first.")
        
        # Assign the value to the variable
        self.symbols[name] = value

    def lookup(self, name):
        """Look up a symbol by its name."""
        if not isinstance(name, str):
            raise ValueError(f"Invalid symbol name: '{name}'. Name must be a string.")

        value = self.symbols.get(name, None)
        if value is None:
            raise KeyError(f"Symbol '{name}' not found.")
        
        return value

    def __repr__(self):

        for key, value in self.symbols.items():
            print(f"{key}:\n")
            if isinstance(value, Node):
                value.pretty_print()
            else:
                print(f"  {value}\n")
        
        return ""

class Tokenizer:
    TOKEN_PATTERNS = [
        ('COMMENT',     r'//.*'),                      # Single-line comment
        ('NUMBER',      r'\d+'),                       # Integer
        ('KEYWORD',     r'\b(თუ|თუარა|აი|დაბეჭდე|ფუნქცია)\b'), # Reserved words
        ('IDENTIFIER',  r'[_\u10A0-\u10FF][_\u10A0-\u10FF0-9]*'),  # Identifiers
        ('COMPARISON',  r'==|!=|<=|>=|<|>'),          # Comparison operators
        ('ASSIGNMENT',  r'='),                        # Assignment operator
        ('OPERATOR',    r'[+\-*/]'),                  # Arithmetic operators
        ('BRACKET',     r'[(){}]'),                   # Brackets
        ('SEMICOLON',   r';'),                        # Semicolon
        ('COMMA',       r','),                        # Comma for function parameters
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

# Parser for syntactic analysis
class Parser:
    def __init__(self, tokens, symbol_table, debug=False):
        self.tokens = tokens
        self.position = 0
        self.symbol_table = symbol_table
        self.debug = debug

    def current_token(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def consume(self, expected_type=None, expected_value=None):
        token = self.current_token()
        if not token or (expected_type and token[0] != expected_type) or (expected_value and token[1] != expected_value):
            self.error(f"Expected {expected_type} with value {expected_value} but got {token}")
        if self.debug:
            print(f"Consuming {token} at position {self.position}")
        self.position += 1
        return token

    def error(self, message):
        raise SyntaxError(f"Syntax error at position {self.position}: {message}")

    def parse_statement(self):
        token = self.current_token()
        if token is None:
            return None

        # Variable declaration
        if token[0] == 'KEYWORD' and token[1] == 'აი':
            return self.parse_declaration()
        elif token[0] == 'IDENTIFIER':
            return self.parse_assignment()
        elif token[0] == 'KEYWORD' and token[1] == 'ფუნქცია':
            return self.parse_function()
        self.consume()
        return Node('Unknown', [])

    def parse_declaration(self):
        self.consume('KEYWORD', 'აი')
        identifier = self.consume('IDENTIFIER')
        self.consume('ASSIGNMENT', '=')
        expr = self.parse_expression()
        self.consume('SEMICOLON', ';')
        self.symbol_table.declare(identifier[1], expr)
        return DeclarationNode(identifier, expr)

    def parse_assignment(self):
        identifier = self.consume('IDENTIFIER')
        self.consume('ASSIGNMENT', '=')
        expr = self.parse_expression()
        self.consume('SEMICOLON', ';')
        self.symbol_table.assign(identifier[1], expr)
        return AssignmentNode(identifier, expr)

    def parse_function(self):
        self.consume('KEYWORD', 'ფუნქცია')
        function_name = self.consume('IDENTIFIER')
        self.consume('BRACKET', '(')
        parameters = self.parse_parameters()
        self.consume('BRACKET', ')')
        self.consume('BRACKET', '{')
        body = self.parse_block()
        self.consume('BRACKET', '}')
        self.symbol_table.declare(function_name[1], FunctionNode(function_name, parameters, body))
        return FunctionNode(function_name, parameters, body)

    def parse_parameters(self):
        parameters = []
        if self.current_token() and self.current_token()[0] == 'IDENTIFIER':
            parameters.append(self.consume('IDENTIFIER'))
            while self.current_token() and self.current_token()[0] == 'COMMA':
                self.consume('COMMA')
                parameters.append(self.consume('IDENTIFIER'))
        return parameters

    def parse_block(self):
        block_node = Node("Block")
        while self.current_token() and self.current_token()[1] != '}':
            statement = self.parse_statement()
            if statement:
                block_node.children.append(statement)
        return block_node

    def parse_factor(self):
        token = self.current_token()
        if token[0] in ('NUMBER', 'IDENTIFIER'):
            self.consume()
            return ValueNode(token[1])
        elif token[0] == "BRACKET" and token[1] == "(":
            self.consume("BRACKET", "(")
            node = self.parse_expression()
            self.consume("BRACKET", ")")
            return node
        self.error("Expected factor")

    def parse_term(self):
        node = self.parse_factor()
        while True:
            token = self.current_token()
            if token and token[0] == "OPERATOR" and token[1] in ("*", "/"):
                op = self.consume("OPERATOR")
                right = self.parse_factor()
                node = BinaryOperationNode(op[1], node, right)
            else:
                break
        return node

    def parse_expression(self):
        node = self.parse_term()
        while True:
            token = self.current_token()
            if token and token[0] == "OPERATOR" and token[1] in ("+", "-"):
                op = self.consume("OPERATOR")
                right = self.parse_term()
                node = BinaryOperationNode(op[1], node, right)
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

class IntermediateCodeGenerator:
    def __init__(self):
        self.instructions = []  # List to store TAC instructions
        self.temp_counter = 0   # Counter to generate temporary variables

    def new_temp(self):
        """Generate a new temporary variable."""
        temp_name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp_name

    def generate(self, node):
        """Generate TAC for a given AST node."""
        method_name = f"gen_{type(node).__name__}"
        generator = getattr(self, method_name, self.generic_gen)
        return generator(node)

    def generic_gen(self, node):
        raise NotImplementedError(f"No generator for node type: {type(node).__name__}")

    def gen_DeclarationNode(self, node):
        identifier = node.children[0][1]  # Identifier name
        expression = self.generate(node.children[1])  # Evaluate expression
        self.instructions.append(f"{identifier} = {expression}")
        return identifier

    def gen_AssignmentNode(self, node):
        identifier = node.children[0][1]  # Identifier name
        expression = self.generate(node.children[1])  # Evaluate expression
        self.instructions.append(f"{identifier} = {expression}")
        return identifier

    def gen_BinaryOperationNode(self, node):
        left = self.generate(node.children[0])  # Generate TAC for left operand
        right = self.generate(node.children[1])  # Generate TAC for right operand
        temp = self.new_temp()  # Create a new temporary variable
        self.instructions.append(f"{temp} = {left} {node.value} {right}")
        return temp

    def gen_ValueNode(self, node):
        return node.value  # Leaf node (value or identifier)

    def gen_FunctionNode(self, node):
        function_name = node.name[1]
        parameters = [param[1] for param in node.parameters]
        self.instructions.append(f"func {function_name}({', '.join(parameters)}) {{")
        self.generate(node.body)
        self.instructions.append("}")
        return function_name

    def gen_Node(self, node):
        for child in node.children:
            self.generate(child)


def read_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()

# Main function to orchestrate reading, tokenizing, parsing, and output.
def main():
    if len(sys.argv) < 2:
        print("Please provide a filename.")
        return

    input_filename = sys.argv[1]
    content = read_file(input_filename)
    tokenizer = Tokenizer(content)
    tokens = tokenizer.tokenize()

    symbol_table = SymbolTable()
    parser = Parser(tokens, symbol_table, debug=False)
    ast = parser.parse()
    ast.pretty_print()
    print("\nSymbol Table:")
    print(symbol_table)

    # Generate intermediate code
    icg = IntermediateCodeGenerator()
    icg.generate(ast)

    print("\nThree-Address Code:")
    for instruction in icg.instructions:
        print(instruction)

if __name__ == "__main__":
    main()
