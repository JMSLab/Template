import sys

sys.path.append('./source/lib')

from JMSLab.autofill import Autofill
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

with open(r"issue50\test0_calcs.tex","w") as file:
    file.write(''.join(Autofill(s, "\\textnormal{{{:.2f}}}") for s in ["VariableProfit", 
                                                                       "VariableProfitCF", 
                                                                       "DeltaVariableProfit"]))
    file.write(''.join(Autofill(s, "{:.2f}") for s in ["Epsilon", "MarginalCost", "SurplusGain"]))

GenerateAutofillMacros(["Epsilon", "MarginalCost", "SurplusGain", 
                        "VariableProfit", "VariableProfitCF", "DeltaVariableProfit"], r"issue50\test1_calcs.tex", "{:.2f}")

