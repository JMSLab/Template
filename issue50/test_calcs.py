import sys

sys.path.append('./source/lib')

from JMSLab.autofill import GenerateAutofillMacros

Q_94 = 5.86
P_94 = 16.22
P_90 = 12.17

Epsilon = - 1.19

MarginalCost = (1 + 1 / Epsilon) * P_94

SurplusGain = P_94 - MarginalCost

VariableProfit = Q_94 * (P_94 - MarginalCost)

VariableProfitCF = Q_94 * (P_94 / P_94) \
    ** (Epsilon) * (P_90 - MarginalCost)

DeltaVariableProfit = VariableProfit - VariableProfitCF

GenerateAutofillMacros(["Epsilon", "MarginalCost", "SurplusGain", 
                        "VariableProfit", "VariableProfitCF", "DeltaVariableProfit"], 
                        "{:.2f}",
                       r"issue50\test0_calcs.tex")


GenerateAutofillMacros([["Epsilon", "MarginalCost", "SurplusGain"], 
                        ["VariableProfit", "VariableProfitCF", "DeltaVariableProfit"]], 
                       ["{:.2f}", "\\textnormal{{{:.2f}}}"],
                       r"issue50\test1_calcs.tex")

