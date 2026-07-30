infile  = fullfile('output/derived/wb_clean', 'gdp_education_logs.csv');
outfile = fullfile('output/analysis/regressions', 'gdp_vs_educ_logs_2010.txt');

dataset = readtable(infile);
x = dataset{:,'log_education_exp_2010'};
y = dataset{:,'log_gdp_2010'};

keep = ~isnan(x) & ~isnan(y);
x = x(keep);
y = y(keep);

n = numel(y);
X = [ones(n,1) x];
k = size(X,2);

b     = X \ y;
resid = y - X * b;
dof   = n - k;
se    = sqrt(diag((resid' * resid) / dof * inv(X' * X)));
tstat = b ./ se;
% Two-sided p-values from the t-distribution via the incomplete beta function
pval  = betainc(dof ./ (dof + tstat.^2), dof / 2, 0.5);

r2     = 1 - (resid' * resid) / sum((y - mean(y)).^2);
adj_r2 = 1 - (1 - r2) * (n - 1) / dof;

fid = fopen(outfile, 'w');
fprintf(fid, 'OLS regression (cross-section, 2010)\n');
fprintf(fid, 'log_gdp_2010 = alpha + beta * log_education_exp_2010\n');
fprintf(fid, 'Source: %s\n', infile);
fprintf(fid, 'Observations: %d\n\n', n);
fprintf(fid, '%-28s %12s %12s %12s %12s\n', 'Variable', 'Coef.', 'Std. Err.', 't', 'P>|t|');
fprintf(fid, '%s\n', repmat('-', 1, 80));
fprintf(fid, '%-28s %12.4f %12.4f %12.4f %12.4f\n', 'log_education_exp_2010', b(2), se(2), tstat(2), pval(2));
fprintf(fid, '%-28s %12.4f %12.4f %12.4f %12.4f\n', '_cons (alpha)', b(1), se(1), tstat(1), pval(1));
fprintf(fid, '%s\n', repmat('-', 1, 80));
fprintf(fid, '%-16s%.4f\n', 'R-squared:', r2);
fprintf(fid, '%-16s%.4f\n', 'Adj. R-squared:', adj_r2);
fclose(fid);

exit
