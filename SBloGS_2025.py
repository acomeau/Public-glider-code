

from erddapy import ERDDAP
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

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
e.dataset_id = "otn200_20250224_201_realtime"
e.response = "csv"
# e.constraints = {
#     "time>=": "2024-04-17T00:00:00Z",
#     "time<=": "2024-11-04T23:59:59Z",}

e.variables = [
    "depth",
    "time",
    "latitude",
    "longitude",
    "sci_bb2flsv2_b470_scaled",
    "sci_bb2flsv2_b532_scaled",
    "sci_bb2flsv2_chl_scaled",
    "sci_ocr504i_irrad3",
    "sci_oxy4_oxygen",
    "sci_suna_nitrate_concentration"
]

df = e.to_pandas() #Load in the data to the python environment
print(df.columns) #display the variable names since they've also got units attached
df['pd_datetime'] = pd.to_datetime(df['time (UTC)'])
df['unixtime'] = df['pd_datetime'].astype(np.int64)
df.replace('NaN', np.nan, inplace=True)

# find the appropriate oxygen and nitrate variable name since they have special characters that break normal text laws
s_oxy = b'sci_oxy4_oxygen (\u00b5mole/liter)'  # variable names with mu in them
oxygen_variable_name = s_oxy.decode('utf-8')
s_suna = b'sci_suna_nitrate_concentration (\u03bcmol)'  # variable names with mu in them
nitrate_variable_name = s_suna.decode('utf-8')

#interpolate depth, to all timestamps so it is avialalbe for plotting against science variables
x_t, x_clean, df['interp_depth'] = interp_y2x(df['unixtime'],df['unixtime'],df['depth (m)'],debg=0)

######################################################################

plt.figure(1)
a = plt.subplot(4,1,1)
plt.scatter(df['pd_datetime'],df['interp_depth'],6, df['sci_bb2flsv2_chl_scaled (ug/l)'])
plt.gca().invert_yaxis()
plt.colorbar().set_label('Chl-a fluor (ug/l)')
plt.ylabel('Depth (m)')

plt.subplot(4,1,2, sharex = a)
plt.scatter(df['pd_datetime'],df['interp_depth'],6, df[nitrate_variable_name])
plt.gca().invert_yaxis()
plt.colorbar().set_label('Nitrate (uM)')
plt.ylabel('Depth (m)')

plt.subplot(4,1,3, sharex = a)
plt.scatter(df['pd_datetime'],df['interp_depth'],6, df[oxygen_variable_name])
plt.gca().invert_yaxis()
plt.colorbar().set_label('Oxygen (uM)')
plt.ylabel('Depth (m)')

plt.subplot(4,1,4, sharex = a)
plt.scatter(df['pd_datetime'],df['interp_depth'],6, df['sci_bb2flsv2_b532_scaled (/m /sr)'])
plt.gca().invert_yaxis()
plt.colorbar().set_label('Backscattering (/m /sr)')
plt.ylabel('Depth (m)')

######################################################################
plt.figure(2)
a = plt.subplot(4,1,1)
plt.plot(df['pd_datetime'],df['sci_bb2flsv2_chl_scaled (ug/l)'],'.')
plt.ylabel('chl-a fluor (ug/l)')

plt.subplot(4,1,2, sharex = a)
plt.plot(df['pd_datetime'],df[nitrate_variable_name],'.')
plt.ylabel('Nitrate (uM)')

plt.subplot(4,1,3, sharex = a)
plt.plot(df['pd_datetime'],df[oxygen_variable_name],'.')
plt.ylabel('Oxygen (uM)')

plt.subplot(4,1,4, sharex = a)
plt.plot(df['pd_datetime'], df['sci_bb2flsv2_b532_scaled (/m /sr)'],'.')
plt.ylabel('Backscattering (/m /sr)')

