#%%
import pandas as pd
import json

# %%
jsonfile = open('relatorio.json', 'r')

# %%
jsonobj = json.load(jsonfile)

# %%
type(jsonobj)

# %%
df = pd.DataFrame
# %%
df = df.from_dict(jsonobj)

#%%
df.drop('relatorio', axis=0)

#%%
df = df.drop(["ocs_futuras", "relatorio", "ocs_para_antecipar", "timeline"], axis=0)

#%%
df

# %%
df.to_csv('relatorio.csv')

# %%
