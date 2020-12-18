dataset = readtable('.\output\derived\gdp_education\gdp_education_logs.csv');

x = dataset{:,'log_education_exp_2010'};
y = dataset{:,'log_gdp_2010'};

scatter(x,y);
set(gca,'FontName','Times New Roman');
xlabel('Log of Total Government Expenditure on Education in 2010 (% of GDP)', 'FontSize', 10);
ylabel('Log of GDP per capita in 2010 (current US$)', 'FontSize', 10);
print ('-depsc','-painters', '.\output\analysis\plots\gdp_educ.eps');
close

exit
