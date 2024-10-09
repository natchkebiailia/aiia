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

# მთავარი ფუნქცია
def main():
    if len(sys.argv) < 2:
        print("გთხოვთ მიუთითოთ ფაილის სახელი.")
        return
    input_filename = sys.argv[1]
    content = read_file(input_filename)
    output = lexical_analyse(content)
    output_filename = input_filename + ".შედეგი"
    write_output(output_filename, output)
    print(f"შედეგი ჩაწერილია ფაილში: {output_filename}")

# პროგრამის საწყისი
if __name__ == "__main__":
    main()



