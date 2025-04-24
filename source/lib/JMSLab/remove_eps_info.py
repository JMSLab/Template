import re
'''
Stores program to remove dates from EPS files
'''

def remove_eps_info(infile):
    '''
    Removes CreationDate comment and version information applied by MatPlotLib
    when outputing eps files.

    Parameters
    ----------
    infile: str
        Directory of the eps file 
    '''
    to_remove = '%%CreationDate:'
    version_info = '%%Creator: Matplotlib'
    eps_file = open(f'{infile}', 'r')
    lines = eps_file.readlines()
    eps_file.close

    outfile = open(f'{infile}', 'w')
    for line in lines:
        if version_info in line:
            # matplotlib version pattern
            pattern = r'\s*\bv\S*(?=,\s*)'
            new_attribution = re.sub(pattern, '', line)
            outfile.write(new_attribution)
        elif to_remove not in line:
            outfile.write(line)
    outfile.close()
