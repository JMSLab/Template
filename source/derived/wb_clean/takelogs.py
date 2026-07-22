import numpy as np
import pandas as pd
from source.lib.SaveData import SaveData
from pathlib import Path


def Main():
    data_dir = Path("output/derived/wb_clean")

    log_df = TakeLogs(data_dir)
    
    SaveData(
        df=log_df,
        keys=["countryname"],
        out_file=data_dir / "gdp_education_logs.csv",
        log_file=data_dir / "gdp_education_logs.log",
        append=False,
        sortbykey=True,
    )


def TakeLogs(data_dir):
    gdp_and_educ = pd.read_csv(
        data_dir / "gdp_education.csv", header=2
    )

    gdp_and_educ["log_gdp_2010"] = np.log(gdp_and_educ["GDP_2010"])
    gdp_and_educ["log_education_exp_2010"] = np.log(gdp_and_educ["Education_Exp_2010"])
    gdp_and_educ.columns = gdp_and_educ.columns.str.replace(" ", "").str.lower()
    
    return gdp_and_educ


if __name__ == "__main__":
    Main()
