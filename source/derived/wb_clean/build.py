import json
import pandas as pd
from source.lib.SaveData import SaveData
from pathlib import Path


def Main():
    raw_dir = Path("datastore/raw/world_bank/orig")
    out_dir = Path("output/derived/wb_clean")

    with open("temp/derived/wb_clean/wb_clean.json") as f:
        config = json.load(f)

    df = PrepareData(raw_dir, config["nrows"])
    SaveData(
        df=df,
        keys=["Country Name"],
        out_file=out_dir / "gdp_education.csv",
        log_file=out_dir / "gdp_education.log",
        append=False,
        sortbykey=True,
    )


def PrepareData(infolder, nrows):
    gdp_df = pd.read_csv(
        infolder / "API_NY.GDP.PCAP.CD_DS2_en_csv_v2_1740213.csv", header=2, nrows=nrows
    )

    gdp_df = gdp_df[["Country Name", "2010"]]
    gdp_df.rename(columns={"2010": "GDP_2010"}, inplace=True)

    educ_df = pd.read_csv(
        infolder / "API_SE.XPD.TOTL.GD.ZS_DS2_en_csv_v2_1740282.csv", header=2, nrows=nrows
    )

    educ_df = educ_df[["Country Name", "2010"]]
    educ_df.rename(columns={"2010": "Education_Exp_2010"}, inplace=True)

    gdp_and_educ = pd.merge(gdp_df, educ_df, on=["Country Name"])

    return gdp_and_educ


if __name__ == "__main__":
    Main()
