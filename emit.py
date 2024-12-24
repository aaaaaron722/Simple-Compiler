# Emitter object keeps track of the generated code and outputs it.
class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.header = ""
        self.code = ""
        self.indentLevel = 0
        self.indentPending = True
        
    def emit(self, code):
        if self.indentPending:
            self.code += "    " * self.indentLevel  # append indent
            self.indentPending = False  # reset indentation
        self.code += code

    def emitLine(self, code):
        # deal indentation
        if self.indentPending:
            self.code += "    " * self.indentLevel  # append indent
        self.code += code + '\n'
        self.indentPending = True
        
    def headerLine(self, code):
        self.header += code + '\n'

    def increaseIndent(self):
        self.indentLevel += 1
        
    def decreaseIndent(self):
        if self.indentLevel > 0:
            self.indentLevel -= 1
            
    def writeFile(self):
        with open(self.fullPath, 'w') as outputFile:
            outputFile.write(self.header + self.code)