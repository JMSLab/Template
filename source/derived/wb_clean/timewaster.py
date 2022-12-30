# An insidious program that wastes time
from time import sleep
import pandas as pd

def Main():
    sleep(30)
    important_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    df = pd.DataFrame(important_data)
    df.to_csv("output/derived/wb_clean/wasteful_data.csv")

Main()
