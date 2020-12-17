
local instub  "source/raw/test"
local outstub "output/derived/test"

import delimited `instub'/data.csv, clear varnames(1)

save_data `outstub'/test.dta, replace key(col1)
