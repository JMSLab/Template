library(dplyr)

Main <- function() {
  instub  <- "output/derived/wb_clean"
  outstub <- "output/analysis/top_gdp"

  df <- read.csv(file.path(instub, "gdp_education.csv"))

  df <- df %>%
    select(Country.Name, GDP_2010) %>%
    arrange(-GDP_2010) %>% top_n(5)

  WriteTable("<tab:top_gdp>", df, file.path(outstub, "top_gdp.txt"))

  df_diff <- data.frame(
    Countries = paste(df$Country.Name[5], "-", df$Country.Name[1]),
    Gap       = df$GDP_2010[5] - df$GDP_2010[1]
  )

  WriteTable("<tab:top_gdp_gap>", df_diff, file.path(outstub, "top_gdp_gap.txt"))
}


WriteTable <- function(tag, df, out) {
  write.table(tag, row.names = FALSE, quote = FALSE,
              file = out, col.names = FALSE)
  write.table(df, row.names = FALSE, quote = FALSE,
              file = out, append = TRUE, col.names = FALSE, sep = "\t")
}


Main()
