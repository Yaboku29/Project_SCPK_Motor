import numpy as np
import pandas as pd
import streamlit as stl

# File bike_dataset.csv
data=pd.read_csv("bike_dataset.csv",usecols=lambda col: col!='links')

print(data.head(10))
