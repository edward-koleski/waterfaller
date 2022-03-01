#### Version: 2.2 ####
############################################################

#Input file
fname_in = '/Users/edkoleski/Documents/Chang_Lab/scripts/waterfaller/stable/test cases/one_chrom.csv' 
# Should be the .csv export from mass hunter - no modifications necessary.

#Output files
# A table of the paresed will be saved as a .csv file named the same as the in .csv file with ' parsed' added in same directory

fname_out = '/Users/edkoleski/Documents/Chang_Lab/scripts/waterfaller/stable/test cases/out.pdf' 
# Output figure location, should be .pdf to import into illustrater if needed. Changing the extension to .svg may simplify editing in illustrator.


############################################################

# PLOT PARAMETERS
y_reorder = [] # Note: Comma required between numbers!
# What this does: Re order columns or chose only a subset of the data to plot. If empty ( = []), use all columns in given order. 
# Index starts at 0. Example: [0 , 2, 3 , 9 , 5] will only plot the y0, y2, y3, y9, y5 columns in that order. 
# Note: Comma required between numbers!

# Title
title_text = '' # Optional - Leave empty if no title desired ('').
title_size = 20 # Font size of title text

# Scale and rename
y_scales = {} # Scale a chromatogram. Larger = zoom in. 1 is the top chromatogram. ex. {3:10, 4:2}
custom_s_names = {} # Rename a chromatogram. 1 is the top chromatogram. ex. {2:'favorite', 5:'least favorite'}

# X-Axis
t_min = 0 # Min time in units data is stored in (seconds, minutes, hours)
t_max = 10 # Max time in units data is stored in (seconds, minutes, hours)
x_min = 0 # Minimum on x-axis
x_max = 10 # Maximum on x-axis
x_tick = 1 # Incremenet for x-tick marks
x_tick_size = 16 # Font size for x-tick marks
x_label = 'Time (min)' # X-axis title. Leave blank ( = '') if no title desired.
x_label_size = 18 # Font size for X-title

# Lines
axis_linewidth = 1.5 # linewidth of the X and Y axis
chrom_linewidth = 1.5 # linewidth of the chromatograms

############################################################

