dataset = readtable(fullfile('output/derived/wb_clean', 'gdp_education_logs.csv'));
outstub = fullfile('output/analysis/plots', 'gdp_educ');

x = dataset{:,'log_education_exp_2010'};
y = dataset{:,'log_gdp_2010'};

scatter(x,y);
set(gca,'FontName','Times New Roman');
xlabel('Log of Total Government Expenditure on Education in 2010 (% of GDP)', 'FontSize', 10);
ylabel('Log of GDP per capita in 2010 (current US$)', 'FontSize', 10);
print('-depsc','-painters', [outstub '.eps']);
print('-dpng','-painters', [outstub '.png']);
close;

exit
