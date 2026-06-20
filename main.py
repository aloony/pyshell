from pathlib import Path

text = Path("file.crap").read_text().strip()
# text += "\n"


class Tokenizer:
    def __init__(self, text):
        self.text = text
        self.pos = -1

    def peek(self):
        if self.pos + 1 == len(self.text):
            return None
        return self.text[self.pos + 1]

    def advance(self):
        self.pos += 1

    def tokenize(self):
        tokens = []

        is_string = False
        word = ""

        def w():
            nonlocal word
            nonlocal tokens
            nonlocal is_string
            if word:
                tokens.append(word)
                is_string = False
            word = ""

        while True:
            char = self.peek()
            if char is None:
                break
            elif char in " \t":
                if is_string:
                    word += char
                else:
                    w()
            elif char == "\n":
                w()
                tokens.append("\n")
            elif char == "+":
                w()
                tokens.append(char)
            elif char == "-":
                w()
                tokens.append(char)
            elif char == '"':
                if is_string:
                    word += char
                    w()
                else:
                    is_string = True
                    word += char
            elif char == "|":
                w()
                tokens.append("|")
            elif char == "{":
                w()
                tokens.append("{")
            elif char == "}":
                w()
                tokens.append("}")
            else:
                word += char
            self.advance()
        w()

        tokens.append("EOF")
        return tokens


tokenizer = Tokenizer(text)
tokens = tokenizer.tokenize()
print(tokens)
