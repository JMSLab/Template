library(dplyr)

Main <- function() {
  instub  <- "output/derived/wb_clean"
  outstub <- "output/analysis/top_gdp"

  df <- read.csv(file.path(instub, "gdp_education.csv"))
  
  df <- df %>%
    select(Country.Name, GDP_2010) %>%
    arrange(-GDP_2010) %>% top_n(5)
  
  tag <- "<tab:top_gdp>"
  out <- file.path(outstub, "top_gdp.txt")
  
  write.table(tag, row.names = FALSE, quote = FALSE,
              file = out, col.names = FALSE)
  
  write.table(df, row.names = FALSE, quote = FALSE,
              file = out, append = TRUE, col.names = FALSE, sep = "\t")
}

Main()
