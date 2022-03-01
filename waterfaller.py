import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter
import os
import csv
import re
from waterfaller_params import *

# adjust the global font
font = {'family' : 'sans-serif',
        'sans-serif': 'Arial',
        'weight' : 'regular',
        'size'   : 12}
mpl.rc('font', **font)

########################################################
#Version: 2.2
#Last updated: 2/16/21
#Created by: Dr. Jorge Marchand
#Updated by: Ed Koleski
########################################################
class Data:                                     # Define a class to output both df and list of sample names
    def __init__(self, df, s_names):
        self.df = df
        self.s_names = s_names

def raw2df(input_file):
    ''' Parse data from .csv agilent mass hunter output to a wide format for further plotting.'''
    
    sname_df = pd.DataFrame(columns=['sname', 'sname_idx', 'start_idx', 'end_idx'])       # Set up df to contain idx info for each sample
    
    first_sname = pd.read_csv(input_file, header=0).columns[0]                            # Special case for first sample
    sname_df.loc[0,'sname'] = first_sname
    sname_df.loc[0,'sname_idx'] = 0
    
    raw = pd.read_csv(input_file, header=1)                     # Read in the data as a df
    
    for i in raw.index:                                         # Get sample names and index in raw df for each sample name
        value = raw.iloc[i,0]
        if type(value) == str:    
            if 'ESI' in value:
                d = {'sname':value, 'sname_idx':i}
                sname_df = sname_df.append(d, ignore_index=True)
    
    for i in sname_df.index:

        if i == 0:                                             # Get the start and end idx for each sample
            sname_df.loc[i,'start_idx'] = 0                    # Special case for first sample
            
            if len(sname_df.index) == 1:                       # Special case if only one sample
                sname_df.loc[i,'end_idx'] = raw.index[-1]
            else:
                sname_df.loc[i,'end_idx'] = sname_df.loc[i+1,'sname_idx']-1

        elif i == sname_df.index[-1]:                          # Special case for last sample
            sname_df.loc[i,'start_idx'] = sname_df.loc[i,'sname_idx']+2
            sname_df.loc[i,'end_idx'] = raw.index[-1]

        else:
            sname_df.loc[i,'start_idx'] = sname_df.loc[i,'sname_idx']+2
            sname_df.loc[i,'end_idx'] = sname_df.loc[i+1,'sname_idx']-1
    
    for i in sname_df.index:                                  # iterate through samples. 
        start_idx = sname_df.loc[i,'start_idx']
        end_idx = sname_df.loc[i,'end_idx']
        
        if i == 0:                                            # make df from first sample
            df = raw[start_idx:end_idx]
        else:                                                 # merge df from other samples to existing df
            df2merge = raw[start_idx:end_idx]
            df = df.merge(df2merge, how='outer', on=['#Point'], suffixes=('','_added'))
            df = df.drop(columns=['X(Minutes)_added'])
            
        df = df.rename(columns={'Y(Counts)':sname_df.loc[i,'sname']})
        
    df = df.astype(float)                                     # Convert data type to float
    df = df.drop(columns = ['#Point'])
    df = df.rename(columns={'X(Minutes)':'time'})
    
    s_names = sname_df['sname'].to_list()
    
    exp_df = df.copy()                                        # Create copy, change column names, export to csv
    exp_df = exp_df[exp_df.columns[1:]]
    exp_df.to_csv(fname_in[:-4]+" parsed.csv")
    
    return Data(df, s_names)

def prune_data(raw2df_out, y_reorder):
    ''' Select subset of data. Reorder columns and sample name list if necessary'''
    
    df, s_names = raw2df_out.df, raw2df_out.s_names          # Get df and s_names list from Data obj
    
    df = df[(df['time']>t_min)&(df['time']<t_max)]           # Select rows between time min and max
    
    if len(y_reorder) !=0:
        y_new_order = [0]+[i+1 for i in y_reorder]               # Add 0 and add 1 to reorder int list
        df = df.iloc[:,y_new_order]                              # Select reordered columns
        s_names = [s_names[i] for i in y_reorder]                # Reorder s_names list also
    
    return Data(df, s_names)

def waterfall(data, s_names, y_scales, fname_out):
    ''' Make plots. Each chromatogram is plotted on its own ax within the matplotlib plt object.'''
   
    n_cgrms = len(data.columns) - 1 #Number of chromatograms
    
    fig, axs = plt.subplots(n_cgrms, 1, figsize=(8,6), sharex=True)     # Make figure object
    
    fig.suptitle(title_text, fontsize = title_size, fontweight = 'bold') # Add a title
    plt.subplots_adjust(wspace=0, hspace=0)         #remove spaces b/w axes
    
    for ax in axs:                                  #remove top and right axes line from all plots
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.get_yaxis().set_visible(False)
        
    for ax in axs[:-1]:                             #remove bottom axes from all plots except last one
        ax.spines['bottom'].set_visible(False)
        ax.get_xaxis().set_visible(False)
    
    x = data['time']                                #Add plot to each axes. Select appropriate y value
    for i in range(n_cgrms):   
        y = data[data.columns[i+1]]
        axs[i].plot(x, y, color='black', linewidth = chrom_linewidth)        
    
    # First set all plots to same axis range.
    # Then, if y_scales contains scale factors, scale relevant chroms.
    
    y_max = data.iloc[:,1:].max().max()         # Set the y axis limits for each chrom based on global max and min
    y_min = data.iloc[:,1:].min().min()
    y_range = y_max-y_min
    y_ax_top = y_max + .1*y_range
    y_ax_bottom = y_min - .1*y_range
    
    for i in range(n_cgrms):
        axs[i].set_ylim([y_ax_bottom, y_ax_top])
    
    if len(y_scales.keys()) != 0:                               # Scale chroms if scale factors provided
        for i in y_scales.keys():                                
            if i-1 in range(len(axs)):
                ylim = axs[i-1].get_ylim()                          # Get y-axis limits
                y_range = ylim[1] - ylim[0]                                
                y_data_min = data.iloc[:,i].min()                   # i is 1 indexed. so skip first time col. get min
                data_min_to_ax_bottom = (y_data_min-ylim[0])/y_range    # Find ratio of distance b/w data_min and y_axis bottom to y_range

                y_range = y_range/y_scales[i]                       # Increase y_range by scale factor provided
                y_ax_bottom = y_data_min - data_min_to_ax_bottom*y_range   # Set axis bottom using data_min_to_ax_bottom
                y_ax_top = y_ax_bottom+y_range                       # Set top based on bottom
                axs[i-1].set_ylim([y_ax_bottom, y_ax_top])           # Set y axis limits 
                print(f"\nChromatogram(s) {list(y_scales.keys())} scaled.")
            else:
                print(f"Error while scaling. Chromatogram number {i} is not in chromatogram index.") 
                
    elif len(y_scales.keys()) == 0:
        print("\nNo y-axis manipulation performed. Each plot set to the same y-axis values.")
    
    plt.xlim(x_min,x_max)     # Set x axis limits
    plt.xticks(np.arange(x_min, x_max+x_tick, x_tick), fontsize=x_tick_size)   # set xticks
    
    print("\nSample names found in .csv file:")                  # Print out sample names in csv
    for i in range(len(s_names)):
        if i+1 in custom_s_names.keys():
            print(f"{i+1}: {s_names[i]} // {custom_s_names[i+1]}")
        else:
            print(f"{i+1}: {s_names[i]}")

    if len(custom_s_names.keys()) != 0:                    # Customize s_names
        for i in custom_s_names.keys():
            if i-1 in range(len(s_names)):
                s_names[i-1] = custom_s_names[i]               # custom_s_names dict 1 indexed.
            else:
                print(f"\nError while renaming. Chromatogram number {i} is not in chromatogram index.")
        
    for i in range(len(axs)):                       # Add Labels for each line
        ax = axs[i]
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        ax.text(xlim[1], ylim[0]+y_range*0.85, s_names[i], ha='right')
        
    if len(x_label)!= 0:
        plt.xlabel(x_label, fontsize = x_label_size, fontweight='bold')
    
    for ax in axs:                                   # Adjust axis linewidth
        for axis in ['top','bottom','left','right']:
            ax.spines[axis].set_linewidth(axis_linewidth)
    
    fig.subplots_adjust(bottom=0)
    fig.savefig(fname_out, bbox_inches = 'tight')
    
    print(f"\nFigure saved to: {fname_out}\n")
    plt.show()

def single_chrom(data, s_names, fname_out):
    ''' Create a plot for a single chromatogram trace.'''
    
    fig, ax = plt.subplots(figsize=(8,3))     # Make figure object
    fig.suptitle(title_text, fontsize = title_size, fontweight = 'bold') # Add a title
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.get_yaxis().set_visible(False)
    
    x = data['time']                                #Add plot to each axes. Select appropriate y value 
    y = data[data.columns[1]]
    ax.plot(x, y, color='black', linewidth = chrom_linewidth)
    
    plt.xlim(x_min,x_max)     # Set x axis limits
    plt.xticks(np.arange(x_min, x_max+x_tick, x_tick), fontsize=x_tick_size)   # set xticks
    
    print("\nSample names found in .csv file:")                  # Print out sample names in csv
    for i in range(len(s_names)):
        if i+1 in custom_s_names.keys():
            print(f"{i+1}: {s_names[i]} // {custom_s_names[i+1]}")
        else:
            print(f"{i+1}: {s_names[i]}")

    if len(custom_s_names.keys()) != 0:                    # Customize s_names
        for i in custom_s_names.keys():
            if i-1 in range(len(s_names)):
                s_names[i-1] = custom_s_names[i]               # custom_s_names dict 1 indexed.
            else:
                print(f"\nError while renaming. Chromatogram number {i} is not in chromatogram index.")
    
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]
    ax.text(xlim[1], ylim[0]+y_range*0.85, s_names[0], ha='right')
    
    if len(x_label)!= 0:
        plt.xlabel(x_label, fontsize = x_label_size, fontweight='bold')
        
    for axis in ['top','bottom','left','right']:
            ax.spines[axis].set_linewidth(axis_linewidth)
            
    fig.savefig(fname_out, bbox_inches = 'tight')
    
    print(f"\nFigure saved to: {fname_out}\n")
    plt.show()
    
########################################################  
### Run script ###
data = raw2df(fname_in)
data = prune_data(data, y_reorder)

if len(data.s_names) == 1:
    single_chrom(data.df, data.s_names, fname_out)
else:
    waterfall(data.df, data.s_names, y_scales, fname_out)

########################################################