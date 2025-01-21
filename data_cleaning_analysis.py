# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 11:26:45 2025

@author: swapn
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
# access data and metadata
data = pd.read_csv('84917ENG_TypedDataSet_15012025_115740.csv', sep = ';', index_col = 0,skiprows = 0, 
                   names = ['Source', 'Application', 'Year', 'Total renewable', 'Relative'])
metadata = pd.read_csv('84917ENG_metadata.csv', sep = ';')

#clean dataframe columns for leading and trailing whitespace
data.iloc[:,0] = data.iloc[:,0].str.strip()
data.iloc[:,1] = data.iloc[:,1].str.strip()
metadata.iloc[:,0] = metadata.iloc[:,0].str.strip()

#create custom dictionary to match the code with the title
code = dict(zip(metadata.iloc[:,0], metadata.iloc[:,1]))
data['Year'] = data['Year'].replace(code)

columns_to_convert = ['Year', 'Total renewable', 'Relative']
data[columns_to_convert] = data[columns_to_convert].apply(pd.to_numeric, errors='coerce')

#%%
#Plot total renewable energy with/out statistical transfer
data_clean = data[data['Application'] == 'E007022']
tot_exc_st_tr = data_clean[data_clean.iloc[:,0] == 'T001028']
tot_inc_st_tr = data_clean[data_clean.iloc[:,0] == 'E007210']

tot_exc_st_tr['Total Renewable per Year'] = tot_exc_st_tr.groupby('Year')['Total renewable'].transform('sum')
tot_inc_st_tr['Total Renewable per Year'] = tot_inc_st_tr.dropna(subset=['Total renewable']).groupby('Year')['Total renewable'].transform('sum')


# Plot data
fig, [ax1, ax2] = plt.subplots(1,2, figsize = (10,6))
colors = plt.cm.Set2.colors
# First line on left y-axis
ax1.scatter(tot_exc_st_tr['Year'], tot_exc_st_tr['Total Renewable per Year'], label='Excluding statistical transfer', color=colors[3], ls = '-')
ax1.set_xlabel('Year')
ax1.set_ylabel('Total Renewable per Year')

ax1.scatter(tot_inc_st_tr['Year'], tot_inc_st_tr['Total Renewable per Year'], label='Including statistical transfer', color=colors[2], ls = '-')
ax1.axvline(x=2020, color=colors[1], linestyle='--')
ax1.text(2020 + 0.5, ax1.get_ylim()[0]+20000, 'Year of COVID', rotation=90, color=colors[1], verticalalignment='bottom')

# Add legend
fig.legend(loc="upper left", bbox_to_anchor=(0.1,0.9))

# Titles
ax1.set_title('Total Renewable per Year')


ax2.plot(tot_exc_st_tr['Year'], tot_exc_st_tr['Relative'], '-o', color=colors[4])
ax2.set_title('Renewable as % of final gross consumption')
ax2.scatter(2030, 42.5, color='gray', s=70, zorder=5)  # Add a dot
ax2.text(
    2017, 8,  # Text location
    'General upward trend',  # Text content
    fontsize=10,
    color='gray',
    rotation=64,  # Text angle
    rotation_mode='anchor',  # Anchor the rotation to the text position
    horizontalalignment='left',  # Align horizontally
    verticalalignment='bottom'   # Align vertically
)

ax2.annotate(
    'New renewable energy target by 2030', 
    xy=(2030, 42.5),  # Arrowhead location (intersection)
    xytext=(1994, 40),  # Text location
    arrowprops=dict(facecolor=colors[1], edgecolor=colors[1], arrowstyle='-|>'),
    fontsize=10,
    color='gray'
)

ax2.set_ylabel('%')
ax2.set_xlabel('Year')
ax2.set_ylim(0, 50)
ax2.set_xlim(1990, 2035)
ax2.axhline(y = 42.5, color=colors[1], linestyle='--')
ax2.axvline(x = 2030, color=colors[1], linestyle='--')


# Show plot
plt.tight_layout()
plt.show()

#%%
#year wise analysis
# E006587 hydro power
# E006588 wind power
# E006589 solar power
# E006594 geothermal
# E006656 aerothermal
# E006566 biomass
year_to_check = 2020
application_to_check = 'E007022'
data_sub = data[data['Year'] == year_to_check]
data_sub = data_sub[data_sub['Application'] == application_to_check]
data_sub = data_sub.drop(['Year'], axis = 1)
source_code = ['E006587', 'E006588', 'E006589', 'E006594', 'E006656', 'E006566']

data_source = data_sub[data_sub['Source'].isin(source_code)]
data_source['Source'] = data_source['Source'].replace(code)
data_source['Application'] = data_source['Application'].replace(code)
data_source.fillna(value = 0, inplace = True)

fig, ax = plt.subplots(figsize=(11,10))
plt.subplots_adjust(bottom = 0.25)

ax.pie(data_source['Total renewable'], 
       labels=data_source['Source'], 
       autopct='%1.1f%%', 
       startangle=140, 
       colors = colors)
ax.set_title(f'Distribution of Renewable Sources for {code[application_to_check]} in {year_to_check}')
ax_slider = plt.axes([0.05, 0.1, 0.65, 0.03], facecolor= 'lemonchiffon')
slider = Slider(ax_slider, label = 'Year', valmin = 1990, valmax = 2021, valstep = 1, valfmt = '%0.0f',  valinit = year_to_check)
ax_radio = plt.axes([0.755, 0.1, 0.3, 0.3], facecolor= 'powderblue')
radio = RadioButtons(ax_radio, labels =  ('Total', 'Electricity', 'Heat', 'Transport'), activecolor = 'k')
radio_dict = {'Total':'E007022',
              'Electricity':'E006607',
              'Heat':'E006608',
              'Transport':'E007028'}
def update(val):
    year_to_check = int(slider.val)
    application_to_check = radio_dict[radio.value_selected]
    slider.valtext.set_text(f"{year_to_check}")
    
    data_sub = data[data['Year'] == year_to_check]
    data_sub = data_sub[data_sub['Application'] == application_to_check]
    data_sub = data_sub.drop(['Year'], axis = 1)
    
    data_source = data_sub[data_sub['Source'].isin(source_code)]
    data_source.fillna(value = 0, inplace = True)
    data_source['Source'] = data_source['Source'].replace(code)
    data_source['Application'] = data_source['Application'].replace(code)
    total = data_source['Total renewable'].sum()
    percentages = (data_source['Total renewable'] / total * 100).round(1)

    ax.clear()
    patches, texts, autotexts = ax.pie(data_source['Total renewable'], 
                                       autopct=lambda p: f'{p:.1f}%' if p > 5 else '', 
                                       pctdistance = 1.1,
                                       startangle=140, 
                                       colors = colors)
    # custom labels with the source name  and the % from the autotext (from the pie chart)
    labels = ['{0} - {1}% '.format(i,j) for i,j in zip(data_source['Source'], percentages)]
    ax.legend(patches, labels, loc='upper left', bbox_to_anchor=(-0.3, 1.), fontsize = 12, frameon = False)
    
    ax.set_title(f'Distribution of Renewable Sources for {code[application_to_check]} in {year_to_check}')
    fig.canvas.draw_idle()

slider.on_changed(update)
radio.on_clicked(update)
plt.show()

#%%

application_to_check = 'E007028'
data_sub = data[data['Application'] == application_to_check]
data_sub = data_sub.drop(['Application', 'Relative'], axis = 1)
data_sub.dropna(inplace= True)

source_code= ['E006583', 'E006677', 'E006566', 'T001028']
data_sub = data_sub[~data_sub['Source'].isin(source_code)]
data_sub['Source'] = data_sub['Source'].replace(code)

# Pivot the data for a stacked bar plot
pivot_df = data_sub.pivot(index='Year', columns='Source', values='Total renewable').fillna(0)

# Plot the stacked bar plot
ax = pivot_df.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='tab20')

# Customize the plot
plt.title('Consumption of Renewable Energy for Transport by Year and Source')
plt.xlabel('Year')
plt.ylabel('Renewable energy consumed (TJ)')
plt.xticks(ticks=range(len(pivot_df.index)), labels=pivot_df.index.astype(int), rotation=90)
plt.legend(title='Source', loc='upper left')
plt.tight_layout()

# Show the plot
plt.show()

#%%

application_to_check = 'E006607'
data_sub = data[data['Application'] == application_to_check]
data_sub = data_sub.drop(['Application', 'Relative'], axis = 1)
data_sub.dropna(inplace= True)
source_code= ['E006583', 'E006677', 'E006566', 'T001027','T001028', 'E006588', 'E006669']
data_sub = data_sub[~data_sub['Source'].isin(source_code)]
data_sub['Source'] = data_sub['Source'].replace(code)

# Pivot the data for a stacked bar plot
pivot_df = data_sub.pivot(index='Year', columns='Source', values='Total renewable').fillna(0)

# Plot the stacked bar plot
ax = pivot_df.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='tab20')

# Customize the plot
plt.title('Consumption of Renewable Energy for Electricity by Year and Source')
plt.xlabel('Year')
plt.ylabel('Renewable energy consumed (TJ)')
plt.xticks(ticks=range(len(pivot_df.index)), labels=pivot_df.index.astype(int), rotation=90)
plt.legend(title='Source', loc='upper left')
plt.tight_layout()

# Show the plot
plt.show()

#%%

application_to_check = 'E006608'
data_sub = data[data['Application'] == application_to_check]
data_sub = data_sub.drop(['Application', 'Relative'], axis = 1)
data_sub.dropna(inplace= True)
source_code= ['E006583', 'E006677', 'E006566', 'T001027', 'T001028', 'E006588', 'E006669', 'E006591', 'E006664', 'E006594']
data_sub = data_sub[~data_sub['Source'].isin(source_code)]
data_sub['Source'] = data_sub['Source'].replace(code)

# Pivot the data for a stacked bar plot
pivot_df = data_sub.pivot(index='Year', columns='Source', values='Total renewable').fillna(0)

# Plot the stacked bar plot
ax = pivot_df.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='tab20')

# Customize the plot
plt.title('Consumption of Renewable Energy for Heat by Year and Source')
plt.xlabel('Year')
plt.ylabel('Renewable energy consumed (TJ)')
plt.xticks(ticks=range(len(pivot_df.index)), labels=pivot_df.index.astype(int), rotation=90)
plt.legend(title='Source', loc='upper left', fontsize = 8)
plt.tight_layout()

# Show the plot
plt.show()

#%%
# Wind energy
source_to_check = ['E006637', 'E006638']
data_sub = data[data['Source'].isin(source_to_check)]
data_sub = data_sub.drop(['Relative'], axis = 1)
data_sub.dropna(inplace= True)

data_total = data_sub[data_sub['Application'] == 'E007022']
data_total.drop(['Application'], axis = 1, inplace= True)
data_total['Source'] = data_total['Source'].replace(code)

pivot_df = data_total.pivot(index = 'Year', columns = 'Source', values = 'Total renewable')
fig, ax = plt.subplots()
# Plot the stacked bar plot
ax = pivot_df.plot(kind='bar', figsize=(10, 6), colormap='Set2')

ax.axvline(x=2016-1990, color='red', linestyle='--', linewidth=2)  # Adjust x to align with year index

# Add an arrow pointing to the line
ax.annotate(
    'Implementation of simplified tendering for \n off-shore wind farms by the Dutch govt.',
    xy=(2016-1990, 40000),  # Arrow tip position
    xytext=(2000-1990, 50000),  # Text position
    arrowprops=dict(facecolor='black', arrowstyle='->'),
    fontsize=10,
    color='black'
)

# Customize the plot
plt.title('Consumption of Renewable Wind Energy by Year and Location')
plt.xlabel('Year')
plt.ylabel('Renewable energy consumed (TJ)')
plt.xticks(ticks=range(len(pivot_df.index)), labels=pivot_df.index.astype(int), rotation=90)
plt.legend(title='Source', loc='upper left')
plt.tight_layout()

# Show the plot
plt.show()

#%%
# geothermal energy

source_to_check = ['E006595', 'E006596']
data_sub = data[data['Source'].isin(source_to_check)]
data_sub = data_sub.drop(['Relative'], axis = 1)
data_sub.dropna(inplace= True)

data_total = data_sub[data_sub['Application'] == 'E007022']
data_total.drop(['Application'], axis = 1, inplace= True)
data_total['Source'] = data_total['Source'].replace(code)

pivot_df = data_total.pivot(index = 'Year', columns = 'Source', values = 'Total renewable')
fig, ax = plt.subplots()
# Plot the stacked bar plot
ax = pivot_df.plot(kind='bar', figsize=(10, 6), colormap='Set2')


# Customize the plot
plt.title('Consumption of Renewable Geothermal Energy by Year and Location')
plt.xlabel('Year')
plt.ylabel('Renewable energy consumed (TJ)')
plt.xticks(ticks=range(len(pivot_df.index)), labels=pivot_df.index.astype(int), rotation=90)
plt.legend(title='Source', loc='upper left')
plt.tight_layout()

# Show the plot
plt.show()

#%%
application_to_check = ['E006607', 'E006608', 'E007028']
data_sub = data[(data['Source'] == 'T001027') & (data['Application'].isin(application_to_check))]
data_sub = data_sub.drop(['Relative'], axis = 1).reset_index(drop = True)

data_renewable = data[(data['Source'] == 'T001028') & (data['Application'].isin(application_to_check))]
data_renewable = data_renewable.drop(['Relative'], axis = 1).reset_index(drop = True)

data_nonrenewable = data_renewable.copy()
data_nonrenewable['Total renewable'] = data_sub['Total renewable'] - data_renewable['Total renewable']


# Replace 'Source' and 'Application' values in data_renewable
data_renewable['Source'] = data_renewable['Source'].replace(code)
data_renewable['Application'] = data_renewable['Application'].replace(code)

# Replace 'Source' and 'Application' values in data_nonrenewable
data_nonrenewable['Source'] = data_nonrenewable['Source'].replace(code)
data_nonrenewable['Application'] = data_nonrenewable['Application'].replace(code)


pivot_renewable = data_renewable.pivot(index='Year', columns='Application', values='Total renewable')
pivot_nonrenewable = data_nonrenewable.pivot(index='Year', columns='Application', values='Total renewable')

# Ensure both DataFrames are aligned on the same index and columns
pivot_renewable, pivot_nonrenewable = pivot_renewable.align(pivot_nonrenewable, join='inner', axis=0)
pivot_renewable = pivot_renewable[pivot_renewable.index > 2003]
pivot_nonrenewable = pivot_nonrenewable[pivot_nonrenewable.index > 2003]
# Bar positions and width
bar_width = 0.4
x = np.arange(len(pivot_renewable.index))  # Positions for the groups

fig, ax = plt.subplots(figsize=(12, 8))

# Define custom color lists
renewable_colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f']
nonrenewable_colors = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e', '#e6ab02']

# Plot stacked renewable bars at -bar_width/2
bottom_renewable = np.zeros(len(pivot_renewable))
for i, column in enumerate(pivot_renewable.columns):
    # print(pivot_renewable[column], bottom_renewable)
    ax.bar(
        x - bar_width / 2,
        pivot_renewable[column],
        width=bar_width,
        label=f'Renewable: {column}',
        bottom=bottom_renewable,
        color=renewable_colors[i % len(renewable_colors)]  # Cycle through renewable colors
    )
    bottom_renewable += pivot_renewable[column]



# Plot stacked non-renewable bars at +bar_width/2
bottom_nonrenewable = np.zeros(len(pivot_nonrenewable))
for i, column in enumerate(pivot_nonrenewable.columns[:2]):
    # print(pivot_nonrenewable[column], bottom_nonrenewable)
    ax.bar(
        x + bar_width / 2,
        pivot_nonrenewable[column],
        width=bar_width,
        label=f'Non-renewable: {column}',
        bottom=bottom_nonrenewable,
        color=nonrenewable_colors[i % len(nonrenewable_colors)],# Cycle through non-renewable colors
        edgecolor = 'k',
        hatch = '/'
    )
    bottom_nonrenewable += pivot_nonrenewable[column]



# Customize the plot
ax.set_title('Renewable and Non-Renewable Energy Consumption by Year and Application')
ax.set_xlabel('Year')
ax.set_ylabel('Energy Consumed (TJ)')
ax.set_xticks(x)
ax.set_xticklabels(pivot_renewable.index.astype(int), rotation=90)
ax.legend(loc='upper left', fontsize=10)

plt.tight_layout()
plt.show()