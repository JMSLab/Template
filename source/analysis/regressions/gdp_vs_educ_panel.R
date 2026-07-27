Main <- function() {
  instub  <- "output/derived/wb_clean"
  outstub <- "output/analysis/regressions"

  panel <- read.csv(file.path(instub, "gdp_education_panel.csv"))
  panel <- panel[!is.na(panel$gdp) & !is.na(panel$educ_exp), ]
  panel$year        <- factor(panel$year)
  panel$countrycode <- factor(panel$countrycode)

  model <- lm(gdp ~ educ_exp + year + countrycode, data = panel)

  WriteResults(model, panel, file.path(outstub, "gdp_vs_educ_panel.txt"))
}


WriteResults <- function(model, df, out) {
  s    <- summary(model)
  beta <- s$coefficients["educ_exp", ]
  sep  <- strrep("-", 80)

  lines <- c(
    "Two-way fixed-effects panel regression",
    "gdp_{c,t} = phi_t (year FE) + psi_c (country FE) + beta * educ_exp_{c,t}",
    "Source: output/derived/wb_clean/gdp_education_panel.csv",
    sprintf("Observations: %d", nrow(df)),
    "",
    sprintf("%-28s %12s %12s %12s %12s", "Variable", "Coef.", "Std. Err.", "t", "P>|t|"),
    sep,
    sprintf("%-28s %12.4f %12.4f %12.4f %12.4f", "educ_exp",
            beta["Estimate"], beta["Std. Error"], beta["t value"], beta["Pr(>|t|)"]),
    sep,
    sprintf("%-16s%.4f", "R-squared:", s$r.squared),
    sprintf("%-16s%.4f", "Adj. R-squared:", s$adj.r.squared),
    "",
    sprintf("Country fixed effects: %d; Year fixed effects: %d",
            nlevels(df$countrycode), nlevels(df$year)),
    "(Fixed-effect coefficients estimated but omitted from the table above.)"
  )
  writeLines(lines, out)
}


Main()
