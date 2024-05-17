# perc_summ_app
#--------------------------------------------------------------------
#
# to run: 
#
# $ streamlit run perc_summ_app.py
#
# or go to:
#
# http://perc_summ_app.streamlit.app
#
#--------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from scipy.stats import gaussian_kde

#--------------------------------------------------------------------

def color_red(col):
    return ['color: red' for _ in col]

def color_green(col):
    return ['color: green' for _ in col]

def plot_distributions(data, stack):  
    n_x = data.shape[0]

    entire_dataset = np.hstack([data.flatten(), stack])   
    x0 = np.min(entire_dataset)
    x1 = np.max(entire_dataset)
    xpts = np.linspace(x0, x1, 100)

    kde_stack = gaussian_kde(stack).pdf(xpts)
    
    fig, ax = plt.subplots(figsize=(6,3))
    for i in range(n_x):
        kde_dist = gaussian_kde(data[i, :]).pdf(xpts)
        ax.plot(xpts, kde_dist, label=labls[i])
    ax.plot(xpts, kde_stack, color='black', lw=3, label=operation)
    ax.legend(fontsize='small')    
    ax.set_xlim(x0, x1)
    return fig
#--------------------------------------------------------------------

st.set_page_config(page_title='Percentile Summation')

rng = np.random.default_rng()

cols = st.columns(3, gap='medium')
with cols[0]:
    n = st.number_input(
        'numero dataset',
        value=2, min_value=2, max_value=5, step=1, format='%d')
with cols[1]:  
    dist_type = st.selectbox('distribuzione', ('gaussiana', 'lognormale'))
with cols[2]:
    operation = st.radio('operazione ', ('somma', 'combinazione'))

size = 500
data = np.zeros((n, size))

labls = ["data {}".format(i) for i in range(n)]

cols = st.columns(n, gap='small')
for i, cc in enumerate(cols):
    with cc:
        st.markdown('**{}**'.format(labls[i]))
        if dist_type == 'gaussiana':
            loc = st.slider('media', value=15., min_value=5., max_value=50., step=0.5, key=i) 
            scl = st.slider('dev.std', value=1., min_value=1., max_value=5., step=0.1, key=i+9)
            data[i, :] = rng.normal(loc=loc, scale=scl, size=size) 
        else:
            loc = st.slider('media', value=1.0, min_value=0.0, max_value=3.0, step=0.25, key=i) 
            scl = st.slider('dev.std', value=0.5, min_value=0.1, max_value=2., step=0.1, key=i+9)
            data[i, :] = rng.lognormal(mean=loc, sigma=scl, size=size)

if operation == 'somma':
    stack = np.sum(data, axis=0)
else:
    stack = np.hstack(data)
    

fig = plot_distributions(data, stack)
st.pyplot(fig=fig, use_container_width=True)

metrics = np.zeros((n+2, 4))
for i in range(n):
    metrics[i, :3] = np.percentile(data[i, :], [10, 50, 90])
    metrics[i, 3] = np.mean(data[i, :])

# somma dei vari misuratori p10...p90... mean
metrics[n, :] = np.sum(metrics[:3, :], axis=0)
metrics[n+1, :3] = np.percentile(stack, [10, 50, 90])
metrics[n+1, 3] = np.mean(stack)
df = pd.DataFrame(metrics, columns=['p90','p50', 'p10', 'mean'], index=labls+['somma_perc', operation])

styled_df = (
    df.style.apply(
        color_red, subset=pd.IndexSlice[['somma_perc'], :]).apply(
            color_green, subset=pd.IndexSlice[[operation],    :]))

st.dataframe(styled_df, use_container_width=True)

descrizione = ''':x: :red[Rosso] = somme degli indicatori statistici P10, P50, P90, mean
:arrow_forward: **sbagliato** (tranne che per le medie).


:heavy_check_mark: :green[Verde] = indicatori ricalcolati sulla *{}* dei vari dataset'''

st.markdown(descrizione.format(operation))

