import sys
from lex import *

# Parser object keeps track of current token, checks if the code matches the grammar, and emits code along the way.
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()    # All variables we have declared so far.
        self.functions = set()
        
        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()    # Call this twice to initialize current and peek.
        self.inFunction = False

    # Return true if the current token matches.
    def checkToken(self, kind):
        return kind == self.curToken.kind

    # Return true if the next token matches.
    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    # Advances the current token.
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        # No need to worry about passing the EOF, lexer handles that.

    # Return true if the current token is a comparison operator.
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    def abort(self, message):
        sys.exit("Error! " + message)


    # Production rules.
    # program ::= {statement}
    def program(self):
        self.emitter.headerLine("import sys")
        
        # Since some newlines are required in our grammar, need to skip the excess.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # Parse all the statements in the program.
        while not self.checkToken(TokenType.EOF):
            self.statement()

    # One of the following statements...
    def statement(self):
        # Check the first token to see what kind of statement this is.

        # "PRINT" (expression | string | function_call | ident)
        if self.checkToken(TokenType.PRINT):
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                # Simple string, so print it.
                self.emitter.emitLine(f"print(\"{self.curToken.text}\")")
                self.nextToken()
                
            elif self.checkToken(TokenType.IDENT):
                function_name = self.curToken.text
                self.nextToken()  # Move past the identifier

                if self.checkToken(TokenType.LPARE):  # Check if it's a function call
                    self.match(TokenType.LPARE)  # Expect '('
                    self.emitter.emit(f"print({function_name}(")

                    # Handle function parameters
                    if self.checkToken(TokenType.IDENT) or self.checkToken(TokenType.NUMBER):
                        self.expression()  # Parse the first argument
                        while self.checkToken(TokenType.COMMA):
                            self.emitter.emit(", ")
                            self.nextToken()  # Skip the comma
                            self.expression()  # Parse the next argument

                    self.match(TokenType.RPARE)  # Expect ')'
                    self.emitter.emitLine("))")  # Complete the function call
                else:
                    # It's an identifier, not a function call.
                    self.emitter.emit("print(")
                    self.emitter.emit(function_name)
                    self.emitter.emitLine(")")

            else:
                # Expect an expression
                self.emitter.emit("print(")
                self.expression()
                self.emitter.emitLine(")")

        # "IF" comparison "THEN" nl {statement} ["ELSE" nl {statement}] "ENDIF" nl
        elif self.checkToken(TokenType.IF):
            self.nextToken()
            self.emitter.emit("if ")
            self.comparison()
            self.emitter.emitLine(":")
            self.emitter.increaseIndent()
            
            self.match(TokenType.THEN)
            self.nl()

            # Zero or more statements in the "if" body.
            while not (self.checkToken(TokenType.ELSE) or self.checkToken(TokenType.ENDIF)):
                self.statement()

            # Handle optional "else" block.
            if self.checkToken(TokenType.ELSE):
                self.emitter.decreaseIndent()
                self.nextToken()
                self.emitter.emitLine("else:")
                self.emitter.increaseIndent()
                
                self.nl()

                # Zero or more statements in the "else" body.
                while not self.checkToken(TokenType.ENDIF):
                    self.statement()

            self.emitter.decreaseIndent()

            self.match(TokenType.ENDIF)


        # "WHILE" comparison "REPEAT" {statement} "ENDWHILE"
        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            self.emitter.emit("while ")
            self.comparison()
            self.emitter.emitLine(":")
            self.emitter.increaseIndent()
            
            self.match(TokenType.REPEAT)
            self.nl()
            # Zero or more statements in the loop body.
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.emitter.decreaseIndent()
            self.match(TokenType.ENDWHILE)

        # "FUNC" ident "(" [ident {"," ident}] ")" nl {statement} "ENDFUNC"
        elif self.checkToken(TokenType.FUNC):
            self.inFunction = True
            self.nextToken()
            functionName = self.curToken.text
            if functionName not in self.symbols:
                self.symbols.add(functionName)

            self.emitter.emit("def ")
            self.emitter.emit(functionName)
            self.match(TokenType.IDENT)
            self.match(TokenType.LPARE)
            self.emitter.emit("(")
            if self.checkToken(TokenType.IDENT):
                # Emit the first parameter.
                self.emitter.emit(self.curToken.text)
                self.nextToken()

                # Handle additional parameters.
                while self.checkToken(TokenType.COMMA):
                    self.emitter.emit(", ")
                    self.nextToken()  # Skip the comma.
                    self.emitter.emit(self.curToken.text)
                    self.match(TokenType.IDENT)
            
            self.match(TokenType.RPARE)
            self.emitter.emitLine("):")
            self.nl()
            self.emitter.increaseIndent()
            
            # Parse function body, which can be zero or more statements.
            while not self.checkToken(TokenType.ENDFUNC):
                self.statement()

            # Decrease indent after the function body ends.
            self.emitter.decreaseIndent()
            self.match(TokenType.ENDFUNC)
            self.inFunction = False
            
        # "LET" ident = expression
        elif self.checkToken(TokenType.LET):
            self.nextToken()

            #  Check if ident exists in symbol table. If not, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
            
            self.emitter.emit(self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            self.emitter.emitLine("")
            
        # "INPUT" ident
        elif self.checkToken(TokenType.INPUT):
            self.nextToken()

            # If variable doesn't already exist, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)

            # Emit scanf but also validate the input. If invalid, set the variable to 0 and clear the input.
            self.emitter.emit(self.curToken.text + '=')
            self.emitter.emitLine("input()")
            self.match(TokenType.IDENT)
            
        # "RETURN" expression
        elif self.checkToken(TokenType.RETURN):
            if self.inFunction == True:
                self.nextToken()
                self.emitter.emit("return ")
                self.expression()
            else: # error handling
                raise SyntaxError("Return statement not in function")
            self.emitter.emitLine("")

        # This is not a valid statement. Error!
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        # Newline.
        self.nl()


    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        self.expression()
        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        # Can have 0 or more comparison operator and expressions.
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()


    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        self.term()
        # Can have 0 or more +/- and expressions.
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()


    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        self.unary()
        # Can have 0 or more *// and expressions.
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()


    # unary ::= ["+" | "-"] primary
    def unary(self):
        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()        
        self.primary()


    # primary ::= number | ident
    def primary(self):
        if self.checkToken(TokenType.NUMBER): 
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure the variable already exists.
            name = self.curToken.text
            if name not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)

            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token at " + self.curToken.text)

    # nl ::= '\n'+
    def nl(self):
        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()