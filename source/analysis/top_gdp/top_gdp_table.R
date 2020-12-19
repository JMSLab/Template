library(dplyr)

Main <- function() {
  
  df <- read.csv("./output/derived/gdp_education/gdp_education.csv")
  
  df <- df %>%
    select(Country.Name, GDP_2010) %>%
    arrange(-GDP_2010) %>% top_n(5)
  
  tag <- "<tab:top_gdp>"
  
  write.table(tag, row.names = FALSE, quote = FALSE,
              file = "./output/analysis/top_gdp/top_gdp.txt",
              col.names = FALSE)
  
  write.table(df, row.names = FALSE, quote = FALSE,
              file = "./output/analysis/top_gdp/top_gdp.txt",
              append = TRUE, col.names = FALSE, sep = "\t")
  
}

Main()
