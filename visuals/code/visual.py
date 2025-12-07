# <===============================================>

#   ██╗   ██╗██╗███████╗██╗   ██╗ █████╗ ██╗
#   ██║   ██║██║██╔════╝██║   ██║██╔══██╗██║
#   ██║   ██║██║███████╗██║   ██║███████║██║
#   ╚██╗ ██╔╝██║╚════██║██║   ██║██╔══██║██║
#    ╚████╔╝ ██║███████║╚██████╔╝██║  ██║███████╗
#     ╚═══╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝

# <===============================================>
#        Create visualizations for our data
# <===============================================>
#  Imports:
# <===============================================>
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import os
# <===============================================>
#  Configuration & Constants:
# <===============================================>
#  Script working directory
# <===============================================>
WKDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
# <===============================================>
#  Input data CSV path
# <===============================================>
CSV = WKDIR + '/../../dist/data.csv'
# <===============================================>
#  Output directory for visualizations
# <===============================================>
OUTDIR = WKDIR + '/../'
# <===============================================>
#  CSV separator
# <===============================================>
SEPARATOR='\t'
# <===============================================>
#  Figure sizes for the visualizations
# <===============================================>
FIGSIZES=((12, 8), (12, 8), (12, 8), (12, 8))
# <===============================================>
#  Opacity factor range for showing data age
# <===============================================>
OP_RANGE=(0.25, 1.0)
# <===============================================>
#  Size factor range for showing data size
# <===============================================>
SZ_RANGE=(0.4, 1.0)
# <===============================================>
#  Size range for showing data size
# <===============================================>
SZD_RANGE=(25, 100)
# <===============================================>
#  Code:
# <===============================================>
#  Read input CSV with Pandas
# <===============================================>
df = pd.read_csv(CSV, sep=SEPARATOR)
# <===============================================>
#  Get opacity factor for showing data age
# <===============================================>
#  -> Oldest is OP_RANGE[0]
#  -> Newest is OP_RANGE[1]
# <===============================================>
min_year, max_year = df['Year'].min(), df['Year'].max()
df['alpha_factor'] = OP_RANGE[0] + (OP_RANGE[1] - OP_RANGE[0]) * ((df['Year'] - min_year) / (max_year - min_year))
# <===============================================>
#  Get size factor for showing data size
# <===============================================>
#  -> Smallest is SZ_RANGE[0]
#  -> Biggest is SZ_RANGE[1]
# <===============================================>
min_pob, max_pob = df['POB'].min(), df['POB'].max()
df['size_factor'] = SZ_RANGE[0] + (SZ_RANGE[1] - SZ_RANGE[0]) * ((df['POB'] - min_pob) / (max_pob - min_pob))
# <===============================================>
#  Standarization (Z) of data for fair comparison
# <===============================================>
df[['POB_Z', 'POLL_Z']] = StandardScaler().fit_transform(df[['POB', 'POLL']])
# <===============================================>
#  Merge data for simultaneous comparison
# <===============================================>
df['POB_POLL_Z'] = (df['POB_Z'] + df['POLL_Z']) / 2
# <===============================================>
#  Set plot style
# <===============================================>
plt.style.use('seaborn-v0_8-whitegrid')
# <===============================================>
#  PLOT 1: PIBC & PIBG vs QOL
# <===============================================>
plt.figure(figsize=FIGSIZES[0])
# <===============================================>
COLORS=('cyan', 'blue', 'black')
# <===============================================>
#  Draw relationship (PIBC to PIBG) for latest year
# <===============================================>
label_set = False
for _, row in df[df['Year'] == max_year].iterrows():
    plt.plot([row['PIBC'], row['PIBG']], [row['QOL'], row['QOL']], color=COLORS[2], alpha=0.35, linestyle='dotted', label=f'Brecha del PIB de {max_year}' if not label_set else None)
    label_set = True
# <===============================================>
#  Draw PIBC & PIBG (Dots)
# <===============================================>
sns.scatterplot(data=df, x='PIBC', y='QOL', color=('tab:'+COLORS[0]), alpha=df['alpha_factor'], size='size_factor', sizes=SZD_RANGE, legend=False, label='Valores del PIB per Cápita)')
sns.scatterplot(data=df, x='PIBG', y='QOL', color=('tab:'+COLORS[1]), alpha=df['alpha_factor'], size='size_factor', sizes=SZD_RANGE, legend=False, label='Valores del PIB por Unidad de Consumo)')
# <===============================================>
#  Draw PIBC & PIBG (Lines)
# <===============================================>
sns.regplot(data=df, x='PIBC', y='QOL', scatter=False, truncate=False, color=('tab:'+COLORS[0]), ci=95, line_kws={'alpha': 0.8, 'linewidth': 2}, label='Recta de regresión del PIB per Cápita (i95)')
sns.regplot(data=df, x='PIBG', y='QOL', scatter=False, truncate=False, color=('tab:'+COLORS[1]), ci=95, line_kws={'alpha': 0.8, 'linewidth': 2}, label='Recta de regresión del PIB por Unidad de Consumo (i95)')
# <===============================================>
#  Set title, labels and legend
# <===============================================>
plt.title(f'Producto Interior Bruto vs Calidad de Vida ({min_year}-{max_year % 2000})')
# <===============================================>
plt.xlabel('Valor Económico (€)')
plt.ylabel('Calidad de Vida (QOL)')
# <===============================================>
plt.legend()
# <===============================================>
#  Save figure to file
# <===============================================>
plt.savefig(OUTDIR + 'pib_vs_qol.png')
# <===============================================>
#  PLOT 2: POB & POLL vs QOL
# <===============================================>
plt.figure(figsize=FIGSIZES[1])
# <===============================================>
COLORS=('red', 'blue', 'purple', 'black')
# <===============================================>
#  Draw POB & POLL & BOTH (Dots)
# <===============================================>
sns.scatterplot(data=df, x='POB_Z', y='QOL', color=('tab:'+COLORS[0]), alpha=df['alpha_factor'], size='size_factor', sizes=SZD_RANGE, legend=False, label='Valores de la Población')
sns.scatterplot(data=df, x='POLL_Z', y='QOL', color=('tab:'+COLORS[1]), alpha=df['alpha_factor'], size='size_factor', sizes=SZD_RANGE, legend=False, label='Valores de la Contaminación')
sns.scatterplot(data=df, x='POB_POLL_Z', y='QOL', color=('tab:'+COLORS[2]), alpha=df['alpha_factor'], size='size_factor', sizes=SZD_RANGE, legend=False, label='Valores de Ambos')
# <===============================================>
#  Draw POB & POLL & BOTH (Lines)
# <===============================================>
sns.regplot(data=df, x='POB_Z', y='QOL', scatter=False, truncate=False, color=('tab:'+COLORS[0]), ci=80, line_kws={'alpha': 0.8, 'linewidth': 2}, label='Recta de regresión de la Población (i80)')
sns.regplot(data=df, x='POLL_Z', y='QOL', scatter=False, truncate=False, color=('tab:'+COLORS[1]), ci=80, line_kws={'alpha': 0.8, 'linewidth': 2}, label='Recta de regresión de la Contaminación (i80)')
sns.regplot(data=df, x='POB_POLL_Z', y='QOL', scatter=False, truncate=False, color=('tab:'+COLORS[2]), ci=80, line_kws={'alpha': 0.8, 'linewidth': 2}, label='Recta de regresión de Ambos (i80)')
# <===============================================>
#  Draw central axis
# <===============================================>
plt.axvline(0, color=COLORS[3], linewidth=0.5, linestyle=':')
# <===============================================>
#  Set title, labels and legend
# <===============================================>
plt.title(f'Población y Contaminación vs Calidad de Vida ({min_year}-{max_year % 2000})')
# <===============================================>
plt.xlabel('Desviaciones Estándar (Z-Score)')
plt.ylabel('Calidad de Vida (QOL)')
# <===============================================>
plt.legend()
# <===============================================>
#  Save figure to file
# <===============================================>
plt.savefig(OUTDIR + 'poll_vs_qol.png')
# <===============================================>
#  PLOT 3: GINI vs QOL
# <===============================================>
plt.figure(figsize=FIGSIZES[2])
# <===============================================>
COLORS=('purple',)
# <===============================================>
#  Draw GINI (Dots)
# <===============================================>
sns.scatterplot(data=df, x='GINI', y='QOL', color=('tab:'+COLORS[0]), alpha=df['alpha_factor'], size='size_factor', sizes=SZD_RANGE, legend=False, label='Valores del Índice GINI')
# <===============================================>
#  Draw GINI (Lines)
# <===============================================>
sns.regplot(data=df, x='GINI', y='QOL', scatter=False, truncate=False, color=('tab:'+COLORS[0]), ci=95, line_kws={'alpha': 0.8, 'linewidth': 2}, label='Recta de regresión del Índice GINI (i95)')
# <===============================================>
#  Set title, labels and legend
# <===============================================>
plt.title(f'Desigualdad (GINI) vs Calidad de Vida ({min_year}-{max_year % 2000})')
# <===============================================>
plt.xlabel('Índice GINI')
plt.ylabel('Calidad de Vida (QOL)')
# <===============================================>
plt.legend()
# <===============================================>
#  Save figure to file
# <===============================================>
plt.savefig(OUTDIR + 'gini_vs_qol.png')
# <===============================================>
#  PLOT 4: Correlation Heatmap
# <===============================================>
plt.figure(figsize=FIGSIZES[3])
# <===============================================>
#  Features to take into account
# <===============================================>
features = ('PIBC', 'PIBG', 'POB', 'POLL', 'GINI', 'IPC')
# <===============================================>
#  Dataframe to store data to visualize into
# <===============================================>
df_res = pd.DataFrame(index=features, dtype=np.float64)
df_res.index.name = 'Variable'
# <===============================================>
#  Compute data for each relevant feature
# <===============================================>
for ft in features:
    # Pearson Correlation
    corr = df[ft].corr(df['QOL'])
    # Slope on the graph
    slope = LinearRegression().fit(df[ft].values.reshape(-1, 1), df['QOL'].values.reshape(-1, 1)).coef_.item()
    # Store results
    df_res.loc[ft, 'Correlación'] = corr
    df_res.loc[ft, 'Impacto'] =  slope
    df_res.loc[ft, 'Efecto Total'] = (abs(corr) * slope)
# <===============================================>
#  Normalize Impact and Total Effect
# <===============================================>
df_res['Impacto (Z)'] = StandardScaler().fit_transform(df_res['Impacto'].values.reshape(-1, 1))
df_res['Efecto Total (Z)'] = StandardScaler().fit_transform(df_res['Efecto Total'].values.reshape(-1, 1))
# <===============================================>
#  Draw Correlation & STD Impact (Heatmap)
# <===============================================>
sns.heatmap(
    df_res, annot=True, cmap='viridis',
    vmin=min(df_res['Impacto (Z)'].min(), df_res['Efecto Total (Z)'].min())*0.5,
    vmax=max(df_res['Impacto (Z)'].max(), df_res['Efecto Total (Z)'].max())*0.5,
    center=0
)
# <===============================================>
#  Set title
# <===============================================>
plt.title(f'Análisis de Influencia en QOL ({min_year}-{max_year % 2000})')
# <===============================================>
#  Save figure to file
# <===============================================>
plt.savefig(OUTDIR + 'heatmap.png')
# <===============================================>
