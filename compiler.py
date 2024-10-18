import sys
import re

# ტოკენების შაბლონები, რომლებიც განსაზღვრავენ თუ როგორ უნდა ამოვიცნოთ თითოეული ტიპის token
TOKEN_PATTERNS = [
    ('COMMENT',     r'//.*'),                      # ერთ-ხაზიანი კომენტარი
    ('NUMBER',      r'\d+'),                       # მთელი რიცხვი
    ('KEYWORD',     r'\b(თუ|თუარა|აი|დაბეჭდე)\b'), # რეზერვირებული სიტყვები
    ('IDENTIFIER',  r'[_\u10A0-\u10FF][_\u10A0-\u10FF0-9]*'),    # იდენტიფიკატორები
    ('COMPARISON',  r'==|!=|<=|>=|<|>'),          # შედარების ოპერატორები
    ('ASSIGNMENT',  r'='),                        # მინიჭების ოპერატორი
    ('OPERATOR',    r'[+\-*/]'),                  # არითმეტიკული ოპერატორები
    ('BRACKET',     r'[(){}]'),                   # ფრჩხილები (მრგვალი და ფიგურული)
    ('SEMICOLON',   r';'),                        # წერტილმძიმე
    ('WHITESPACE',  r'\s+'),                      # თეთრი სივრცე
]

# რეგულარული გამოხატვის აწყობა, რომელიც შეადგენს ყველა token-ის შაბლონს
token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_PATTERNS)

# ფუნქცია ლექსიკური ანალიზის შესასრულებლად
def lexical_analyse(code):
    tokens = []
    # regEx-იდთ კოდის თითოეული token-ის მოძიება
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup
        value = match.group(kind)
        # გამოტოვება თეთრი სივრცის და კომენტარების
        if kind == 'WHITESPACE' or kind == 'COMMENT':
            continue
        tokens.append((kind, value))
    return tokens

# ფაილის წაკითხვის ფუნქცია, რომელშიც მითითებული ფაილი იხსნება
def read_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()

# Token-ების შედეგების ჩაწერის ფუნქცია ახალ ფაილში
def write_output(filename, tokens):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(str(tokens))

class Node:
    def __init__(self,value, children=None):
            self.value = value
            self.children = children if children else []

    def __repr__(self):
        return f'Node({self.value}, {self.children})'

def parse(tokens):
    tokens = tokens.copy()
    position = [0]

    def current_token():
        if position[0] < len(tokens):
            return tokens[position[0]]
        else:
            return None

    def consume(expected_type=None, expected_value=None):
        token = current_token()
        if token is None:
            return None
        if expected_type and token[0] != expected_type:
           return None
        if expected_value and token[1] != expected_value:
           return None
        position[0] += 1
        print(position[0])
        return token

    def parse_statement():
        token = current_token()
        if token is None:
            return None

        #variable declaration
        if token[0] == 'KEYWORD' and token[1] == 'აი':
            consume('KEYWORD','აი')
            identifier = consume('IDENTIFIER')
            consume('ASSIGNMENT','=')
            expr = parse_expression()
            consume('SEMICOLON',';')
            return Node('Declaration',[identifier, expr])

        # Assignment
        if token[0] == 'IDENTIFIER':
            identifier = consume('IDENTIFIER')
            consume('ASSIGNMENT','=')
            expr = parse_expression()
            consume('SEMICOLON',';')
            return Node('Assignment',[identifier, expr])

        consume()
        return Node('Unknown',[])
            
    def parse_factor():
        token = current_token()
        if token[0] in ('NUMBER','IDENTIFIER'):
            consume()
            return Node(token[1])
        elif token[0] == "BRACKET" and token[1] == "(":
                consume("BRACKET","(")
                node = parse_expression()
                consume("BRACKET",")")
                return node
        else:
            return None
        
        
    def parse_term():
        node = parse_factor()
        while True:
            token = current_token()
            if token and token[0] == "OPERATOR" and token[1] in ("*","/"):
                consume()
                right = parse_factor()
                node = Node(token[1],[node,right])
            else:
                break
        return node
    

    def parse_expression():
        node = parse_term()
        while True:
            token = current_token()
            if token and token[0] == "OPERATOR" and token[1] in ("+","-"):
                consume()
                right = parse_term()
                node = Node(token[1],[node,right])
            else:
                break
        return node

        

    print(tokens)
    root = Node("Program")
    while position[0] < len(tokens):
        stmnt = parse_statement()
        if stmnt:
            root.children.append(stmnt)
    return root
        


# მთავარი ფუნქცია
def main():
    if len(sys.argv) < 2:
        print("გთხოვთ მიუთითოთ ფაილის სახელი.")
        return
    input_filename = sys.argv[1]
    content = read_file(input_filename)


    tokens = lexical_analyse(content)
    ast = parse(tokens)


    print(ast)
    #output = ''
    #output_filename = input_filename + ".შედეგი"
    #write_output(output_filename, output)
    #print(f"შედეგი ჩაწერილია ფაილში: {output_filename}")

# პროგრამის საწყისი
if __name__ == "__main__":
    main()



