version 14
set more off
preliminaries

program main
    tempfile educ
    load_educ "`educ'"
    load_gdp
    construct_panel "`educ'"
    save_panel
end

program load_educ
    args educ

    local rawdir  "datastore/raw/world_bank/orig"
    local educ_csv "`rawdir'/API_SE.XPD.TOTL.GD.ZS_DS2_en_csv_v2_1740282.csv"

    import delimited using "`educ_csv'", varnames(5) rowrange(5) stringcols(_all) clear
    keep countryname countrycode v5-v65
    forvalues c = 5/65 {
        local yr = `c' + 1955
        rename v`c' educ_exp`yr'
    }
    reshape long educ_exp, i(countrycode countryname) j(year)
    destring educ_exp, replace force
    drop countryname
    save "`educ'"
end


program load_gdp
    local rawdir  "datastore/raw/world_bank/orig"
    local gdp_csv  "`rawdir'/API_NY.GDP.PCAP.CD_DS2_en_csv_v2_1740213.csv"

    import delimited using "`gdp_csv'", varnames(5) rowrange(5) stringcols(_all) clear
    keep countryname countrycode v5-v65
    forvalues c = 5/65 {
        local yr = `c' + 1955
        rename v`c' gdp`yr'
    }
    reshape long gdp, i(countrycode countryname) j(year)
    destring gdp, replace force
end


program construct_panel
    args educ

    merge 1:1 countrycode year using "`educ'", keepusing(educ_exp)
    keep if _merge == 3
    drop _merge

    drop if missing(gdp) & missing(educ_exp)

    order countrycode countryname year gdp educ_exp
    sort countrycode year
end


program save_panel
    isid countrycode year
    export delimited using "output/derived/wb_clean/gdp_education_panel.csv", replace
end


main
