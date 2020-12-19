# -*- coding: utf-8 -*-


import pandas as pd
import os

def Main():
    RAW_DIR = ".\\drive\\raw\\world_bank\\orig"
    OUT_DIR = ".\\output\\derived\\wb_clean"
    df = PrepareData(RAW_DIR)
    df.to_csv(os.path.join(OUT_DIR, "gdp_education.csv"), index = False)

def PrepareData(RAW_DIR):
    gdp_df = pd.read_csv(os.path.join(RAW_DIR,
                                      "API_NY.GDP.PCAP.CD_DS2_en_csv_v2_1740213.csv"),
                         header = 2)
    gdp_df = gdp_df[["Country Name","2010"]]
    gdp_df.rename(columns = {'2010':'GDP_2010'}, inplace = True)
    
    educ_df = pd.read_csv(os.path.join(RAW_DIR,
                                      "API_SE.XPD.TOTL.GD.ZS_DS2_en_csv_v2_1740282.csv"),
                          header = 2)
    educ_df = educ_df[["Country Name","2010"]]
    educ_df.rename(columns = {'2010':'Education_Exp_2010'}, inplace = True)
    
    gdp_and_educ = pd.merge(gdp_df, educ_df, on = ['Country Name'])
    
    return gdp_and_educ

Main()
