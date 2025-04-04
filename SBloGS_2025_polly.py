

from erddapy import ERDDAP
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def interp_y2x(t,x,y,debg=0):
    #This function interpolates all the y variable data to the times of the x-variable.
    #It also outputs sorted and denan'ed data.
    #
    #Input: t - a time vector of all science or flight ticks recorded
    #   x - the variable you want to interpolate onto, must be the same size as t and paded with NaN's where there is missing data
    #   y - the variable you want to interpolate (same size restrictions as x)
    #   debg - if you want to debug and check your code, set this variable to 1. You will get a nice figure. If not set to 0
    #Note: all input variables must be a np.array([],'float')
    #
    #Output: xt_out - times for the sorted and denan'ed x-variable
    #   x_out - the x-variable sorted and denan'ed
    #   y_out - the interpolated y-variable sorted and denan'ed
    #
    #Note, you don't need ys_t because y_out matches up with xs_t
    #One important thing I figured out was that you have to deNaN the data before you sort it. I haven't figured out why yet, but it doesn't work if you do the reverse.

    #Get the times of each instrument without nan's
    x_t = t[np.isnan(x)==0]
    y_t = t[np.isnan(y)==0]
    x_clean = x[np.isnan(x)==0]
    y_clean = y[np.isnan(y)==0]

    #Your interpolated y-variable onto the x-variables timestamp
    # y_out = np.interp(xt_out,yst_clean,ys_clean)
    y_out = np.interp(x_t, y_t, y_clean)

    return x_t, x_clean, y_out


e = ERDDAP(server="https://data.ceotr.ca/erddap",protocol="tabledap")
e.dataset_id = "polly_20250324_204_realtime"
e.response = "csv"
# e.constraints = {
#     "time>=": "2025-03-17T00:00:00Z",
#     "time<=": "2025-03-17T23:59:59Z",}

e.variables = [
    "depth",
    "time",
    "latitude",
    "longitude",
    "temperature",
    "salinity",
    "density"
]

df = e.to_pandas() #Load in the data to the python environment
print(df.columns) #display the variable names since they've also got units attached
df['pd_datetime'] = pd.to_datetime(df['time (UTC)'])
df['hour'] = df['pd_datetime'].dt.hour
df['unixtime'] = df['pd_datetime'].astype(np.int64)
df.replace('NaN', np.nan, inplace=True)
df.replace(-2.147483647E9, np.nan, inplace=True)

#interpolate depth, to all timestamps so it is avialalbe for plotting against science variables
x_t, x_clean, df['interp_depth'] = interp_y2x(df['unixtime'],df['unixtime'],df['depth (m)'],debg=0)

#temperature
ind5 = df['density (kg.m-3)'] > 1010 #filter out low water densities

figsz = (14,8)
savefigdir = '/Users/adamcomeau/Documents/PythonFigs'

plt.figure(6, figsize=figsz)
c = plt.subplot(2,1,1)
plt.scatter(df['pd_datetime'][ind5],df['interp_depth'][ind5],6, df['temperature (degree_C)'][ind5], alpha = 0.5)
plt.gca().invert_yaxis()
plt.colorbar().set_label('Temperature')
plt.ylabel('Depth (m)')
# plt.clim([0.5,6.0])

plt.subplot(2,1,2, sharex = c)
plt.scatter(df['pd_datetime'][ind5],df['interp_depth'][ind5],6, df['density (kg.m-3)'][ind5], alpha = 0.5)
plt.gca().invert_yaxis()
plt.colorbar().set_label('Density')
plt.ylabel('Depth (m)')
# plt.clim([1025,1026])

plt.savefig(os.path.join(savefigdir,'{0}_temperature_density_transect.png'.format(e.dataset_id)))
