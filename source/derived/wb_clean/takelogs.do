version 14
set more off
preliminaries

program main

    import delimited "output/derived/wb_clean/gdp_education.csv", clear

    gen log_gdp_2010 = log(gdp_2010)
    gen log_education_exp_2010 = log(education_exp_2010)

    export delimited "output/derived/wb_clean/gdp_education_logs.csv"

end

main
