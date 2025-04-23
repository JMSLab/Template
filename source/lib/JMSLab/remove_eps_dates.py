'''
Stores program to remove dates from EPS files
'''

def remove_eps_dates(infile):
    '''
    Removes CreationDate comment applied by MatPlotLib
    when outputing eps files.

    Parameters
    ----------
    infile: str
        Directory of the eps file 
    '''
    to_remove = '%%CreationDate:'

    eps_file = open(f'{infile}', 'r')
    lines = eps_file.readlines()
    eps_file.close

    outfile = open(f'{infile}', 'w')
    for line in lines:
        if to_remove not in line:
            outfile.write(line)
    outfile.close()
