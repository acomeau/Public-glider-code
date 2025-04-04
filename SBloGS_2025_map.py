

from erddapy import ERDDAP
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cartopy
import cartopy.crs as ccrs
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


e_200 = ERDDAP(server="https://data.ceotr.ca/erddap",protocol="tabledap")
e_200.dataset_id = "otn200_20250224_201_realtime"
e_200.response = "csv"
# e.constraints = {
#     "time>=": "2024-04-17T00:00:00Z",
#     "time<=": "2024-11-04T23:59:59Z",}

e_200.variables = [
    "time",
    "latitude",
    "longitude",
]

df200 = e_200.to_pandas() #Load in the data to the python environment
print(df200.columns) #display the variable names since they've also got units attached
df200['pd_datetime'] = pd.to_datetime(df200['time (UTC)'])
df200['unixtime'] = df200['pd_datetime'].astype(np.int64)
df200.replace('NaN', np.nan, inplace=True)

#Polly
e_polly = ERDDAP(server="https://data.ceotr.ca/erddap",protocol="tabledap")
e_polly.dataset_id = "polly_20250324_204_realtime"
e_polly.response = "csv"
# e.constraints = {
#     "time>=": "2024-04-17T00:00:00Z",
#     "time<=": "2024-11-04T23:59:59Z",}

e_polly.variables = [
    "time",
    "latitude",
    "longitude",
]

dfpolly = e_polly.to_pandas() #Load in the data to the python environment
print(dfpolly.columns) #display the variable names since they've also got units attached
dfpolly['pd_datetime'] = pd.to_datetime(dfpolly['time (UTC)'])
dfpolly['unixtime'] = dfpolly['pd_datetime'].astype(np.int64)
dfpolly.replace('NaN', np.nan, inplace=True)

#Wave Glider data source
d_url = 'http://129.173.20.180:8086/output_realtime_missions/m203-SV3-1070%20%28C34164NS%29/Telemetry%206%20Report%20by%20WGMS%20Datetime.csv'
wg = pd.read_csv(d_url)
wg['pd_datetime'] = pd.to_datetime(wg['lastLocationFix'])
wg.set_index('pd_datetime', inplace=True)
wg.sort_index(inplace=True)
wg['pd_datetime'] = pd.to_datetime(wg['lastLocationFix'])

#Halifax line data
hfx = pd.DataFrame(np.array([[42.53, -61.39979983, 'HL7'],
       [42.85, -61.7327, 'HL6'],
       [43.17999983, -62.09819983, 'HL5'],
       [43.47999983, -62.4513, 'HL4'],
       [43.88, -62.8828, 'HL3'],
       [44.27, -63.43854512, 'HL2'],
       [44.39999983, -63.45, 'HL1']]),columns=['latitude','longitude', 'stations'])

#Figure settings
extent = [-64.27, -61.3, 42.7, 44.73]
savefigdir = '/Users/adamcomeau/Documents/PythonFigs'
figsz = (14,8)

plt.figure(1, figsize=figsz)
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(resolution='10m')
ax.add_feature(cartopy.feature.LAND)
mksize = 12


#Add the Halifax line stations
plt.plot(hfx['longitude'].astype('float'),hfx['latitude'].astype('float'),'sy',ms = mksize)
for i,z in hfx.iterrows():
    plt.annotate(z['stations'], xy = (float(z['longitude'])-0.1,float(z['latitude'])-0.1))



#OTN200
plt.plot(df200['longitude (degrees_east)'][df200['longitude (degrees_east)'] != np.nan],df200['latitude (degrees_north)'][df200['longitude (degrees_east)'] != np.nan],'-r')
id_200 = df200['pd_datetime'] == df200['pd_datetime'].max()
plt.plot(df200['longitude (degrees_east)'][id_200],df200['latitude (degrees_north)'][id_200],marker = '*',mfc = 'r', ms = mksize, mec = 'k')

#POLLY
plt.plot(dfpolly['longitude (degrees_east)'][dfpolly['longitude (degrees_east)'] != np.nan],dfpolly['latitude (degrees_north)'][dfpolly['longitude (degrees_east)'] != np.nan],'-b')
id_polly = dfpolly['pd_datetime'] == dfpolly['pd_datetime'].max()
plt.plot(dfpolly['longitude (degrees_east)'][id_polly],dfpolly['latitude (degrees_north)'][id_polly],marker = '*', ms = mksize, mfc = 'b', mec = 'k')

#WG-1070
plt.plot(wg['longitude'],wg['latitude'],mfc = 'g')
id_wg = wg['pd_datetime'] == wg['pd_datetime'].max()
plt.plot(wg['longitude'][id_wg],wg['latitude'][id_wg],marker = '*', ms = mksize, mfc = 'g', mec = 'k')

plt.legend(['HFX Line', 'OTN200','200 latest','Polly','Polly latest','WG','WG latest'])
ax.set_extent(extent)
plt.title('Last updated: {0}'.format(dfpolly['pd_datetime'].max()))



#Save the figure
ts = pd.Timestamp.today('UTC')
plt.savefig(os.path.join(savefigdir,'SBLOGS_2025_glider_map_{0}.png'.format(ts.strftime('%Y-%m-%d'))))
