import inspect

def Autofill(var, format = "{}", namespace = None):
    newcommand = f"\\newcommand{{{{\\{{}}}}}}{{{{{format}}}}}\n"

    # Look for var in parent frames
    if namespace is None:
        parent = inspect.currentframe().f_back
        while var not in parent.f_locals.keys() and parent.f_back:
            parent = parent.f_back
        
        if var not in parent.f_locals.keys() or parent is None:
            raise Exception(f"Autofill: Variable '{var}' not found")
        
        namespace = parent.f_locals

    commandname, content = var, namespace[var]

    return newcommand.format(commandname, content)

def GenerateAutofillMacros(autofill_lists, autofill_formats = "{:.2f}", autofill_outfile = "autofill.tex"):
    '''

    Parameters
    ----------
    autofill_lists : TYPE - list
    autofill_formats : TYPE - str or list
    autofill_outfile : TYPE - str

    Returns
    -------
    .tex file

    '''
    if type(autofill_lists) != list:
            raise Exception("Argument 'autofill_lists' must be list")
            
    nested_list = any(isinstance(i, list) for i in autofill_lists)

    if ((nested_list and type(autofill_formats) is str) 
        or (not nested_list and type(autofill_formats) is list)):
        raise Exception("Arguments 'autofill_lists' and 'autofill_formats' are incompatible")

    autofill_file = open(autofill_outfile, 'w')

    if type(autofill_formats) == str:
        output_macros = ''.join(Autofill(autofill_var, autofill_formats) for autofill_var in autofill_lists)
    else:
        autofill_macros = []
        for autofill_list, autofill_format in zip(autofill_lists, autofill_formats):
            autofill_macros.append(''.join(Autofill(autofill_var, autofill_format) for autofill_var in autofill_list))
        output_macros = ''.join(autofill_macros)
        
    autofill_file.write(output_macros)
    autofill_file.close()

