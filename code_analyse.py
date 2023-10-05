import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm
from scipy.interpolate import griddata
from scipy.optimize import curve_fit
from openpyxl import Workbook

df = pd.read_csv(r'C:\Users\tifai\Documents\TPS\Stage 2A\Python stage\Exp5\Exp5.0(sans fentes ni polariseurs)\5.0.csv')
df['ROT2'] = df['ROT 2'].round()

with pd.ExcelWriter('data_exp5.0.xlsx', engine='openpyxl') as writer:
    grouped = df.groupby('ROT2')

    for rot2, group in grouped:
        sheet_name = f"ROT2_{int(rot2)}"

        df_sheet = pd.DataFrame()

        df_sheet['ROT 3'] = group['ROT 3']
        df_sheet['C0'] = group['A']
        df_sheet['C1'] = group['B']
        df_sheet['C2'] = group['AB']
        df_sheet['C3'] = 0
        df_sheet['C4'] = 0
        df_sheet['C5'] = 0
        df_sheet['C6'] = 0
        df_sheet['C7'] = 0

        df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
