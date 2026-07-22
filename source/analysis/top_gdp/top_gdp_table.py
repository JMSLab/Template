from pathlib import Path
import pandas as pd
from source.lib.JMSLab.autofill import AutoFill

def Main():
    in_dir  = Path("output/derived/wb_clean")
    out_dir = Path("output/analysis/top_gdp")

    df_gdp = pd.read_csv(in_dir / "gdp_education.csv")
    df_top_gdp = df_gdp.sort_values(by='GDP_2010', ascending=False).iloc[0:5]
    df_top_gdp = df_top_gdp[["Country Name", "GDP_2010"]]

    WriteTable("<tab:top_gdp>", df_top_gdp, Path(out_dir, "top_gdp.txt"))


    top_country = df_top_gdp["Country Name"].iloc[0]
    fifth_country = df_top_gdp["Country Name"].iloc[4]

    df_diff = pd.DataFrame({
        "Countries": [f"{fifth_country} - {top_country}"],
        "Gap": [df_top_gdp["GDP_2010"].iloc[4] - df_top_gdp["GDP_2010"].iloc[0]]
    })

    WriteTable("<tab:top_gdp_gap>", df_diff, Path(out_dir, "top_gdp_gap.txt"))

def WriteTable(tag, df, out):
    with open(out, "w") as outfile:
        outfile.write(tag + "\n")
        df.to_csv(outfile, index=False, header=False, mode="a", sep="\t")

if __name__ == '__main__':
    Main()
