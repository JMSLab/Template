import os
import pandas as pd
from source.lib.JMSLab.autofill import Autofill

def Main():
    instub  = "output/derived/wb_clean"
    outstub = "output/analysis/top_gdp"

    df = pd.read_csv(os.path.join(instub, "gdp_education.csv"))
    df = df[['Country Name', 'GDP_2010']]
    df = df.sort_values('GDP_2010', ascending=False).head(1)

    top_gdp_value = round(df['GDP_2010'].iloc[0])

    macro = Autofill(
        var='TopGDPValue',
        format='{:,.0f}', 
        namespace={'TopGDPValue': top_gdp_value}
    )

    os.makedirs(outstub, exist_ok=True)
    with open(os.path.join(outstub, 'top_gdp.tex'), 'w') as f:
        f.write(macro)

if __name__ == '__main__':
    Main()
