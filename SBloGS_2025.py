

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
e.dataset_id = "otn200_20250224_201_realtime"
e.response = "csv"
# e.constraints = {
#     "time>=": "2025-03-17T00:00:00Z",
#     "time<=": "2025-03-17T23:59:59Z",}

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
    "sci_suna_nitrate_concentration",
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


# find the appropriate oxygen and nitrate variable name since they have special characters that break normal text laws
s_oxy = b'sci_oxy4_oxygen (\u00b5mole/liter)'  # variable names with mu in them
oxygen_variable_name = s_oxy.decode('utf-8')
s_suna = b'sci_suna_nitrate_concentration (\u03bcmol)'  # variable names with mu in them
# nitrate_variable_name = s_suna.decode('utf-8')

#interpolate depth, to all timestamps so it is avialalbe for plotting against science variables
x_t, x_clean, df['interp_depth'] = interp_y2x(df['unixtime'],df['unixtime'],df['depth (m)'],debg=0)

#ERDDAP sometimes adds units to the variable names and other times not. Likewise for the nitrate variable name. Use whichever variant works.
chl_variable_name = 'sci_bb2flsv2_chl_scaled (ug/l)'
# chl_variable_name = 'sci_bb2flsv2_chl_scaled'
bb532_variable_name = 'sci_bb2flsv2_b532_scaled (/m /sr)'
# bb532_variable_name = 'sci_bb2flsv2_b532_scaled'
bb470_variable_name = 'sci_bb2flsv2_b470_scaled (/m /sr)'
# bb470_variable_name = 'sci_bb2flsv2_b470_scaled'
nitrate_variable_name = s_suna.decode('utf-8')
# nitrate_variable_name = 'sci_suna_nitrate_concentration'

######################################################################
# Transect plot of chl, nitrate, oxygen and backscattering #
figsz = (14,8)
savefigdir = '/Users/adamcomeau/Documents/PythonFigs'

plt.figure(1, figsize=figsz)
a = plt.subplot(4,1,1)
plt.scatter(df['pd_datetime'],df['interp_depth'],6, df[chl_variable_name], alpha = 0.5)
plt.gca().invert_yaxis()
plt.colorbar().set_label('Chl-a fluor (ug/l)')
plt.ylabel('Depth (m)')
plt.clim([0.5,6.0])

plt.subplot(4,1,2, sharex = a)
plt.scatter(df['pd_datetime'],df['interp_depth'],6, df[nitrate_variable_name])
plt.gca().invert_yaxis()
plt.colorbar().set_label('Nitrate (uM)')
# plt.clim([10,18])
plt.ylabel('Depth (m)')
plt.clim([8,20])

plt.subplot(4,1,3, sharex = a)
plt.scatter(df['pd_datetime'],df['interp_depth'],6, df[oxygen_variable_name])
plt.gca().invert_yaxis()
plt.colorbar().set_label('Oxygen (uM)')
plt.ylabel('Depth (m)')
# plt.clim([300,335])

plt.subplot(4,1,4, sharex = a)
plt.scatter(df['pd_datetime'],df['interp_depth'],6, df[bb532_variable_name])
plt.gca().invert_yaxis()
plt.colorbar().set_label('Backscattering 532nm(/m /sr)')
plt.ylabel('Depth (m)')
plt.clim([0,0.001])

plt.savefig(os.path.join(savefigdir,'{0}_transect.png'.format(e.dataset_id)))
######################################################################
# Timeseries plot of the same variables as above

surf_depth = 30
idx = df['interp_depth']<surf_depth # Find an index for all values shallower than the surface depth

plt.figure(2, figsize=figsz)
a = plt.subplot(4,1,1)
plt.plot(df['pd_datetime'],df[chl_variable_name],'ob',label = 'all')
plt.plot(df['pd_datetime'][idx],df[chl_variable_name][idx],'.r',label = '<{0}m'.format(surf_depth))
plt.ylabel('chl-a fluor (ug/l)')
plt.legend()

plt.subplot(4,1,2, sharex = a)
plt.plot(df['pd_datetime'],df[nitrate_variable_name],'ob',label = 'all')
plt.plot(df['pd_datetime'][idx],df[nitrate_variable_name][idx],'.r',label = '<{0}m'.format(surf_depth))
plt.ylabel('Nitrate (uM)')
plt.legend()

plt.subplot(4,1,3, sharex = a)
plt.plot(df['pd_datetime'],df[oxygen_variable_name],'ob',label = 'all')
plt.plot(df['pd_datetime'][idx],df[oxygen_variable_name][idx],'.r',label = '<{0}m'.format(surf_depth))
plt.ylabel('Oxygen (uM)')
plt.legend()

plt.subplot(4,1,4, sharex = a)
plt.plot(df['pd_datetime'], df[bb532_variable_name],'.',label = 'all')
plt.plot(df['pd_datetime'][idx], df[bb532_variable_name][idx],'.',label = '<{0}m'.format(surf_depth))
plt.ylabel('Backscattering (/m /sr)')
plt.legend()

plt.savefig(os.path.join(savefigdir,'{0}_timeseries.png'.format(e.dataset_id)))

######################################################################
#
#Backscattering 2 colours plus ration graph
plt.figure(3, figsize=figsz)
b = plt.subplot(3,1,1)
plt.scatter(df['pd_datetime'],df['interp_depth'],6, df[bb470_variable_name])
plt.gca().invert_yaxis()
plt.colorbar().set_label('Backscattering 470nm (/m /sr)')
plt.ylabel('Depth (m)')
plt.clim([0,0.001])

plt.subplot(3,1,2, sharex = b)
plt.scatter(df['pd_datetime'],df['interp_depth'],6, df[bb532_variable_name])
plt.gca().invert_yaxis()
plt.colorbar().set_label('Backscattering 532nm (/m /sr)')
plt.ylabel('Depth (m)')
plt.clim([0,0.0006])

plt.subplot(3,1,3, sharex = b)
plt.scatter(df['pd_datetime'],df['interp_depth'],6, df[bb470_variable_name]/df[bb532_variable_name])
plt.gca().invert_yaxis()
plt.colorbar().set_label('Backscattering ratio 470/532')
plt.ylabel('Depth (m)')
plt.clim([0,3])

plt.savefig(os.path.join(savefigdir,'{0}_backscattering_timeseries.png'.format(e.dataset_id)))

#Backscattering ratio
plt.figure(4, figsize=figsz)
idx2 = df[bb532_variable_name]>0.0001
idx3 = (df['interp_depth']<35) & (df['hour']<10)
plt.plot(df[chl_variable_name], df[bb470_variable_name]/df[bb532_variable_name],'.')
plt.plot(df[chl_variable_name][idx2], df[bb470_variable_name][idx2]/df[bb532_variable_name][idx2],'.r')
plt.plot(df[chl_variable_name][idx3], df[bb470_variable_name][idx3]/df[bb532_variable_name][idx3],'.g')
plt.legend(['all','backscattering greater than 0.0001','shallower than 35 and 0 to 10 hour utc'])
plt.ylabel('b470/b532')
plt.xlabel('chl-fluor')

plt.savefig(os.path.join(savefigdir,'{0}_backscattering_ratio.png'.format(e.dataset_id)))


#Chlorophyll to backscattering ratio
plt.figure(5, figsize=figsz)
idx2 = df[bb532_variable_name]>0.0001
idx3 = (df['interp_depth']<35) & (df['hour']<10)
plt.plot(df[chl_variable_name], df[chl_variable_name]/df[bb532_variable_name],'.')
plt.plot(df[chl_variable_name][idx2], df[chl_variable_name][idx2]/df[bb532_variable_name][idx2],'.r')
plt.plot(df[chl_variable_name][idx3], df[chl_variable_name][idx3]/df[bb532_variable_name][idx3],'.g')
plt.legend(['all','backscattering greater than 0.0001','shallower than 35 and 0 to 10 hour utc'])
plt.ylabel('chl/b532')
plt.xlabel('chl-fluor')

plt.savefig(os.path.join(savefigdir,'{0}_chltobackscattering.png'.format(e.dataset_id)))

#temperature
ind5 = df['density (kg.m-3)'] > 1010 #filter out low water densities

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
