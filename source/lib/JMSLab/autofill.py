import inspect

def Autofill(var, format = "{}", namespace = None):
    newcommand = f"\\newcommand{{{{\\{{}}}}}}{{{{{format}}}}}\n"
    
    # Look for var in parent frames
    if namespace is None:
        parent = inspect.currentframe().f_back
        while var not in parent.f_locals.keys() and parent.f_back:
            parent = parent.f_back
        
        if var not in parent.f_locals.keys() or parent is None:
            raise Warning(f"Autofill: Variable '{var}' not found")
        
        namespace = parent.f_locals
    
    commandname, content = var, namespace[var]
    
    return newcommand.format(commandname, content)

def GenerateAutofillMacros(list, outfile):
    autofill_file = open(outfile, 'w')
    output_macros = ''.join(Autofill(var) for var in list)
    autofill_file.write(output_macros)
    autofill_file.close()

