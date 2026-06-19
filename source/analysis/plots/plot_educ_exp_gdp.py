import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from source.lib.JMSLab.remove_eps_info import remove_eps_info

def Main():
    indir = Path('output/derived/wb_clean')
    outdir = Path('output/analysis/plots')

    dataset = pd.read_csv(indir / 'gdp_education_logs.csv')
    x = dataset['log_gdp_2010']
    y = dataset['log_education_exp_2010']
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.figure()
    plt.scatter(x, y)
    plt.xlabel('Log of GDP per capita in 2010 (current US$)', fontsize=10)
    plt.ylabel('Log of Total Government Expenditure on Education in 2010 (% of GDP)', fontsize=10)
    plt.savefig(outdir / 'educ_gdp.png', format='png')
    plt.savefig(outdir / 'educ_gdp.eps', format='eps')
    remove_eps_info(outdir / 'educ_gdp.eps')

if __name__ == '__main__':
    Main()
