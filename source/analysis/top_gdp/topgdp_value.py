from pathlib import Path
import pandas as pd
from source.lib.JMSLab.autofill import GenerateAutofillMacros

def Main():
    instub  = Path("output/derived/wb_clean")
    outstub = Path("output/analysis/top_gdp")

    df = pd.read_csv(instub / "gdp_education.csv")
    TopGDPValue = df['GDP_2010'].sort_values(ascending=False).iloc[0]

    GenerateAutofillMacros(
        ["TopGDPValue"],
        "{:,.0f}",
        outstub / "top_gdp.tex"
    )


if __name__ == '__main__':
    Main()
