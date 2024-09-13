# -*- coding: utf-8 -*-

import pandas as pd
import hashlib
import re
import pathlib

def SaveData(df, keys, out_file, log_file = '', append = False, sortbykey = True):
    extension = CheckExtension(out_file)
    CheckColumnsNotList(df)
    CheckKeys(df, keys)
    # reorder df so keys are on the left
    cols_reordered = keys + [col for col in df.columns if col not in keys]
    df = df[cols_reordered]
    df_hash = hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest() 
    summary_stats = GetSummaryStats(df)
    SaveDf(df, keys, out_file, sortbykey, extension)
    SaveLog(df_hash, keys, summary_stats, out_file, append, log_file)
    

def CheckExtension(out_file):
    if type(out_file) == str:
        extension = re.findall(r'\.[a-z]+$', out_file)
    elif type(out_file) == pathlib.PosixPath:
        extension = [out_file.suffix]
    else:
        raise ValueError('Output file format must either be string or pathlib.PosixPath')
    if not extension[0] in ['.csv', '.dta']:
        raise ValueError("File extension should be one of .csv or .dta.")
    return extension[0]

def CheckColumnsNotList(df):
    type_list = [any(df[col].apply(lambda x: type(x) == list)) for col in df.columns]
    if any(type_list):
        type_list_columns = df.columns[type_list]
        raise TypeError("No column can be of type list - check the following columns: " + ", ".join(type_list_columns))
       
      

def CheckKeys(df, keys):
    if not isinstance(keys, list):
        raise TypeError("Keys must be specified as a list.")
        
    for key in keys:
        if not key in df.columns:
            print('%s is not a column name.' % (key))
            raise ValueError('One of the keys you specified is not among the columns.')
    
    df_keys = df[keys]
    
    keys_with_missing = df_keys.columns[df_keys.isnull().any()]
    if keys_with_missing.any():
        missings_string = ', '.join(keys_with_missing)
        raise ValueError(f'The following keys are missing in some rows: {missings_string}.')

    

    
    type_list = any([any(df[keycol].apply(lambda x: type(x) == list)) for keycol in keys])
    if type_list:
        raise TypeError("No key can contain keys of type list")

        
    if not all(df.groupby(keys).size() == 1):
        raise ValueError("Keys do not uniquely identify the observations.")
        

def GetSummaryStats(df):
    var_types = df.dtypes
    with pd.option_context("future.no_silent_downcasting", True):
        var_stats = df.describe(include='all').transpose().fillna('').infer_objects(copy=False)

    var_stats['count'] = df.notnull().sum()
    var_stats = var_stats.drop(columns=['top', 'freq'], errors='ignore')
    
    summary_stats = pd.DataFrame({'type': var_types}).\
        merge(var_stats, how = 'left', left_index = True, right_index = True)
    summary_stats = summary_stats.round(4)
    
    return summary_stats


def SaveDf(df, keys, out_file, sortbykey, extension):
    if sortbykey:
        df.sort_values(keys, inplace = True)
    
    if extension == '.csv':
        df.to_csv(out_file, index = False)
    if extension == '.dta':
        df.to_stata(out_file, write_index = False)

    print(f"File '{out_file}' saved successfully.")
    

def SaveLog(df_hash, keys, summary_stats, out_file, append, log_file):
    if log_file: 
        if append:
            with open(log_file, 'a') as f:
                f.write('\n\n')
                f.write('File: %s\n\n' % (out_file))
                f.write('MD5 hash: %s\n\n' % (df_hash))
                f.write('Keys: ')
                for item in keys:
                    f.write('%s ' % (item))
                f.write('\n\n')
                f.write(summary_stats.to_string(header = True, index = True))
                f.write("\n\n")
        else:
            with open(log_file, 'w') as f:
                f.write('File: %s\n\n' % (out_file))
                f.write('MD5 hash: %s\n\n' % (df_hash))
                f.write('Keys: ')
                for item in keys:
                    f.write('%s ' % (item))
                f.write('\n\n')
                f.write(summary_stats.to_string(header = True, index = True))
                f.write("\n\n")
        
        f.close()    
    else:
        pass
