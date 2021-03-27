import sys
import pandas as pd

filename = sys.argv[1]

df = pd.read_csv(filename,index_col=0)
df = df[df.Prijs.eq(0)]
print(len(df.Prijs))