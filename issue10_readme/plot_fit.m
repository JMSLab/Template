issue   = 'issue10_readme'
dataset = readtable(fullfile('output/derived/wb_clean', 'gdp_education_logs.csv'));
outstub = fullfile(issue, 'gdp_educ');

x = dataset{:,'log_education_exp_2010'};
y = dataset{:,'log_gdp_2010'};

sub = ~(isnan(x) | isnan(y));
X   = [ones(size(x)) x];
X   = X(sub, :);
b   = inv(X' * X) * X' * y(sub);
fit = X * b;

scatter(x,y);
set(gca,'FontName','Times New Roman');
xlabel('Log of Total Government Expenditure on Education in 2010 (% of GDP)', 'FontSize', 10);
ylabel('Log of GDP per capita in 2010 (current US$)', 'FontSize', 10);
print('-dpng','-painters', [outstub '.png']);
close;

scatter(x,y);
line(x(sub),fit);
set(gca,'FontName','Times New Roman');
xlabel('Log of Total Government Expenditure on Education in 2010 (% of GDP)', 'FontSize', 10);
ylabel('Log of GDP per capita in 2010 (current US$)', 'FontSize', 10);
print('-dpng','-painters', [outstub '_fit.png']);
close;

exit
