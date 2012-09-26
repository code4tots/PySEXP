# 9.25.2012
# math4tots
# 
# Simple, S-expression parser in Python.
# Supports reasonably nice error messages.


# The following three methods (colno, lineno, and line) have been
# shamelessly stolen from pyparsing
def colno(loc,strg):
    return (loc<len(strg) and strg[loc] == '\n') and 1 or loc - strg.rfind("\n", 0, loc)

def lineno(loc,strg):
    return strg.count("\n",0,loc) + 1

def line( loc, strg ):
    lastCR = strg.rfind("\n", 0, loc)
    nextCR = strg.find("\n", loc)
    if nextCR >= 0:
        return strg[lastCR+1:nextCR]
    else:
        return strg[lastCR+1:]


# Base (and abstract class) of all Exceptions in this module
class SexpErr(Exception):
    def __init__(self, s, loc, msg=None):
        self.s = s
        self.loc = loc
        self.msg = type(self).__name__ + ( (': ' + msg) if msg else '')
        self.colno = colno(loc,s)
        self.lineno = lineno(loc,s)
        self.line = line(loc,s)
        super(Exception,self).__init__('line %s, col %s\n%s\n%s\n%s'%
            (self.lineno,self.colno,self.line,(' '*(self.colno-1))+'^',self.msg))
    

# Concrete Exceptions thrown by this module

class LexErr(SexpErr): pass
class ParseErr(SexpErr): pass



# Tokenizes the input, but also associates locations 
# with the tokens, (token, loc) so that the function
# parse can give intelligent error messages.
def lexWithLocations(s, loc=0):
    tokens = []
    
    # clear whitespace 
    while loc < len(s) and s[loc].isspace(): loc += 1
    
    while loc < len(s):
        if s[loc] in ['(',')']:
            # handle parentheses
            tokens.append( (s[loc], loc) )
            loc += 1
            
        elif s[loc] in ['"',"'"]:
            # handle string literals
            i = loc+1
            while i < len(s) and s[i] != s[loc]: i += 1
            
            if i == len(s):
                raise LexErr(s, loc, 'End quote not found!')
                
            tokens.append( (s[loc:i+1], loc) )
            loc = i+1
            
        elif s[loc] == ';':
            # handle end of line comments
            i = loc+1
            while i < len(s) and s[i] != '\n': i += 1
            loc = i
            
        else:
            # handle atoms
            i = loc+1
            while i < len(s) and not( (s[i] in ['(',')','"',"'"]) or (s[i].isspace()) ): i += 1
            tokens.append( (s[loc:i], loc) )
            loc = i
        
        # clear whitespace for next iteration
        while loc < len(s) and s[loc].isspace(): loc += 1
        
    return tokens

    

def parse(s):
    stack = [ [] ]
    locStack = []
    
    for token, loc in lexWithLocations(s):
    
        if token == '(':
            stack.append([])
            locStack.append(loc)
            
            
        elif token == ')':
        
            if len(stack) == 1:
                raise ParseErr(s,loc,'mismatched end parenthesis')
                
            stack[-2].append(stack.pop())
            locStack.pop()
            
            
        else:
            stack[-1].append(token)
        
    if len(stack) > 1:
        raise ParseErr(s,locStack[-1],'mismatched begin parenthesis')
        
    return stack[0]
