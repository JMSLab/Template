import unittest
import pandas as pd
import os
from pathlib import Path
import sys
import shutil
sys.path.append("source/lib")
from SaveData import SaveData
# Define path to the builder for use in patching
path = 'JMSLab.misc'

# Run tests from test folder
TESTDIR = Path(__file__).resolve().parent
os.chdir(TESTDIR)

class TestSaveData(unittest.TestCase):
    
    def test_wrong_extension(self):
        df = pd.read_csv('data/data.csv')
        with self.assertRaises(ValueError):
            SaveData(df, ['id'], 'dfs.pdf')

    def test_wrong_keytype(self):
        df = pd.read_csv('data/data.csv')
        with self.assertRaises(TypeError):
            SaveData(df, 'id', 'dfs.csv')        

    def test_wrong_key_column_list(self):
        df = pd.read_csv('data/data.csv')
        df['list_id'] = df['id'].apply(lambda x: [x])
        with self.assertRaises(TypeError):
            SaveData(df, 'list_id', 'dfs.csv')        

    def test_wrong_key_column_containing_list(self):
        df = pd.read_csv('data/data.csv')
        df['list_id'] = df['id'].apply(lambda x: [x] if x == 1 else x)
        with self.assertRaises(TypeError):
            SaveData(df, 'list_id', 'dfs.csv')      

    def test_wrong_non_key_column_containing_list(self):
        df = pd.read_csv('data/data.csv')
        df['list_column'] = df['id'].apply(lambda x: [x] if x == 1 else x)
        with self.assertRaises(TypeError):
            SaveData(df, 'id', 'dfs.csv')    
            
    def test_key_on_left(self):
        df = pd.read_csv('data/data.csv')
        df['id2'] = df['id']
        SaveData(df, ['id2'], 'df.csv')        
        df_saved = pd.read_csv('df.csv')
        self.assertEqual(df_saved.columns[0], 'id2')
        os.remove('df.csv')

    def test_two_keys_on_left(self):
        df = pd.read_csv('data/data.csv')
        df['id2'] = df['id']
        SaveData(df, ['id2', 'id'], 'df.csv')        
        df_saved = pd.read_csv('df.csv')
        self.assertEqual(True, all([x == y for x, y in zip(['id2', 'id'], df_saved.columns[:2])]))
        os.remove('df.csv')
    
    def test_missingkeys(self):
        df = pd.read_csv('data/data.csv')
        with self.assertRaises(ValueError):
            SaveData(df, ['num'], 'dfs.csv')

    def test_duplicate_keys(self):
        df = pd.read_csv('data/data.csv')
        with self.assertRaises(ValueError):
            SaveData(df, ['partid1'], 'dfs.csv')

    def test_multiple_keys(self):
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id', 'partid1','partid2'], 'df.csv')
        df_saved = pd.read_csv('df.csv')
        self.assertEqual(True, df.compare(df_saved).shape==(0,0))
        os.remove('df.csv')

    def test_saves_desired_file_dta(self):
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id'], 'df.dta')
        df_saved = pd.read_stata('df.dta')
        self.assertEqual(True, df.compare(df_saved).shape==(0,0))
        os.remove('df.dta')
                
    def test_saves_desired_file_without_log(self):
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id'], 'df.csv')
        exists = os.path.isfile('df.csv')
        df_saved = pd.read_csv('df.csv')
        self.assertEqual(True, df.compare(df_saved).shape==(0,0))
        os.remove('df.csv')
                
    def test_saves_with_log(self):    
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id'], 'df.csv', 'df.log')
        exists = os.path.isfile('df.log')
        self.assertEqual(exists, True)
        os.remove('df.log')
        os.remove('df.csv')
        
    def test_saves_when_append_given(self):    
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id'], 'df.csv')
        SaveData(df, ['id'], 'df.csv', 'df.log', append = True)
        exists = os.path.isfile('df.log')
        self.assertEqual(exists, True)
        os.remove('df.log')
        os.remove('df.csv')
        
    def test_saves_when_sort_is_false(self):    
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id'], 'df.csv', 'df.log', sortbykey = False)
        exists = os.path.isfile('df.csv')
        self.assertEqual(exists, True)
        os.remove('df.log')
        os.remove('df.csv')    

    def test_saves_with_path(self):  
        outdir_csv = 'data.csv'
        outdir_log = 'data.log'
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id'], outdir_csv, outdir_log)
        exists = os.path.isfile(str(outdir_log))
        self.assertEqual(exists, True)
        os.remove(str(outdir_csv))
        os.remove(str(outdir_log))
    
    def test_logs_forward_slashes(self):    
        df = pd.read_csv('data/data.csv')
        os.mkdir('temp_save')
        SaveData(df, ['id'], 'temp_save/df.csv', 'temp_save/df.log')
        with open('temp_save/df.log', 'r') as log_file:
            first_line = log_file.readline().strip()

        self.assertEqual(first_line, 'File: temp_save/df.csv')
        shutil.rmtree('temp_save')

        
if __name__ == '__main__':
    unittest.main()
