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

def GenerateAutofillMacros(autofill_lists,  autofill_formats, autofill_outfile):
    """
    
    Parameters
    ----------
    autofill_lists : TYPE - list
    autofill_formats : TYPE - str or list
    autofill_outfile : TYPE - str

    Returns
    -------
    .tex file

    """
    file = open(autofill_outfile, 'w')
    
    if type(autofill_formats) == str:
        output_macros = ''.join(Autofill(var, autofill_formats) for var in autofill_lists)
    else:
        macros = []
        for autofill_list, autofill_format in zip(autofill_lists, autofill_formats):
            macros.append(''.join(Autofill(var, autofill_format) for var in autofill_list))
        output_macros = ''.join(macros)
        
    file.write(output_macros)
    file.close()
