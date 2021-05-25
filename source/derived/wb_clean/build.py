import os
import pandas as pd


def Main():
    raw_dir = "drive/raw/world_bank/orig"
    out_dir = "output/derived/wb_clean"

    df = PrepareData(raw_dir)
    df.to_csv(os.path.join(out_dir, "gdp_education.csv"),
              index = False, float_format = '%.9f')


def PrepareData(infolder):
    gdp_df = pd.read_csv(os.path.join(infolder, 
                                     "API_NY.GDP.PCAP.CD_DS2_en_csv_v2_1740213.csv"),
                         header = 2)

    gdp_df = gdp_df[["Country Name", "2010"]]
    gdp_df.rename(columns = {'2010': 'GDP_2010'}, inplace = True)

    educ_df = pd.read_csv(os.path.join(infolder, 
                                      "API_SE.XPD.TOTL.GD.ZS_DS2_en_csv_v2_1740282.csv"),
                          header = 2)

    educ_df = educ_df[["Country Name", "2010"]]
    educ_df.rename(columns = {'2010': 'Education_Exp_2010'}, inplace = True)

    gdp_and_educ = pd.merge(gdp_df, educ_df, on = ['Country Name'])

    return gdp_and_educ

if __name__ == "__main__":
    Main()
