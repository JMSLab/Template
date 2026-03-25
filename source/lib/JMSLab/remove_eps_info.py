'''
Stores program to remove dates from EPS files
'''
import re

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
    with open(infile, 'r') as eps_file:
        lines = eps_file.readlines()

    with open(infile, 'w') as outfile:
        for line in lines:
            if version_info in line:
                # matplotlib version pattern
                pattern = r'\s*\bv\S*(?=,\s*)'
                new_attribution = re.sub(pattern, '', line)
                outfile.write(new_attribution)
            elif to_remove not in line:
                outfile.write(line)
