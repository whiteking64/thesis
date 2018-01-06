#データを読み込み、main_v.pyに返す関数群
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from datetime import datetime, date, timezone, timedelta
import netCDF4

#iMac用

latlon145_file_name = "../data/" + "latlon_ex.csv"
latlon900_file_name = "../data/" + "latlon_info.csv"
grid900to145_file_name = "../data/" + "grid900to145.csv"
ocean_grid_file = "../data/ocean_grid_145.csv"
ocean_grid_145 = pd.read_csv(ocean_grid_file, header=None)
ocean_idx = np.array(ocean_grid_145[ocean_grid_145==1].dropna().index)

#macbook pro用
"""
latlon145_file_name = "../../data/" + "latlon_ex.csv"
latlon900_file_name = "../../data/" + "latlon_info.csv"
grid900to145_file_name = "../../data/" + "grid900to145.csv"
ocean_grid_file = "../../data/ocean_grid_145.csv"
ocean_grid_145 = pd.read_csv(ocean_grid_file, header=None)
ocean_idx = np.array(ocean_grid_145[ocean_grid_145==1].dropna().index)
"""

########################################################################################

def get_lonlat_data():
	#["Lon", "Lat", "Label", "Name"]
	df_lonlat = pd.read_csv(latlon145_file_name)
	return df_lonlat

def get_1day_w_data(wind_file_name):
	df_wind = pd.read_csv(wind_file_name, header=None)
	wind = np.array(df_wind, dtype='float32')
	w_u = wind[:,0]
	w_v = wind[:,1]
	w_speed = np.sqrt(w_u*w_u + w_v*w_v)
	return pd.DataFrame({"w_u": w_u, "w_v": w_v, "w_speed": w_speed})

def get_1day_iw_data(ice_file_name):
	df_ice_wind = pd.read_csv(ice_file_name, header=None)
	df_ice_wind[df_ice_wind==999.] = np.nan
	array_iw = np.array(df_ice_wind, dtype='float32')/100
	iw_u, iw_v = array_iw[:,0], array_iw[:,1]
	iw_speed = np.sqrt(iw_u*iw_u+iw_v*iw_v)
	return pd.DataFrame({"iw_u": iw_u, "iw_v": iw_v, "iw_speed": iw_speed})

def get_1day_ic0_data(ic0_file_name):
	grid_data = pd.read_csv(grid900to145_file_name, header=None)
	grid145 = np.array(grid_data, dtype='int64').ravel()

	ic0_data = pd.read_csv(ic0_file_name, header=None)
	ic0 = np.array(ic0_data, dtype='float32').ravel()
	ic0_145 = ic0[grid145]
	return pd.DataFrame({"ic0_145": ic0_145})

def get_1day_sit_data(sit_file_name):
	grid_data = pd.read_csv(grid900to145_file_name, header=None)
	grid145 = np.array(grid_data, dtype='int64').ravel()

	sit_data = pd.read_csv(sit_file_name, header=None)
	sit = np.array(sit_data, dtype='float32').ravel()

	sit[sit>=10001] = np.nan

	sit_145 = sit[grid145]
	return pd.DataFrame({"sit_145": sit_145})

def get_1day_netcdf4_data(netcdf4_file_name, start_day, end_day):
	"""
	修正必要
	start_dateからend_dateを取り出すようにはなっていない！
	"""
	#df = pd.read_csv("../data/latlon_ex.csv")
	df = get_lonlat_data()
	unreliable_index = df[df.Lat<=49].index

	nc = netCDF4.Dataset(netcdf4_file_name, "r")
	time_var = nc.variables["time"]
	dtime = netCDF4.num2date(time_var[:], time_var.units)

	#start: ファイルのはじめの日にち
	#end: 取り出したい日付
	start_date = [start_day//10000, (start_day%10000)//100, (start_day%10000)%100]
	end_date = [end_day//10000, (end_day%10000)//100, (end_day%10000)%100]
	d1 = datetime(start_date[0], start_date[1], start_date[2])
	d2 = datetime(end_date[0], end_date[1], end_date[2])
	L = (d2-d1).days+1
	day_n = L-1

	nc_lon = nc["longitude"][:]
	nc_lat = nc["latitude"][:]
	nc_u10 = nc["u10"][:]
	nc_v10 = nc["v10"][:]
	nc_t2m = nc["t2m"][:]

	idx_lon = df["Lon"].apply(lambda x: np.argmin(np.absolute(nc_lon-x)))
	idx_lat = df["Lat"].apply(lambda x: np.argmin(np.absolute(nc_lat-x)))

	result_t2m = nc_t2m[day_n, idx_lat, idx_lon]-273
	result_u10 = nc_u10[day_n, idx_lat, idx_lon]
	result_v10 = nc_v10[day_n, idx_lat, idx_lon]

	result_t2m[unreliable_index] = np.nan
	result_u10[unreliable_index] = np.nan
	result_v10[unreliable_index] = np.nan

	return result_t2m, result_u10, result_v10

def get_1month_netcdf4_data(netcdf4_file_name):
	#df = pd.read_csv("../data/latlon_ex.csv")
	df = get_lonlat_data()
	unreliable_index = df[df.Lat<=49].index

	nc = netCDF4.Dataset(netcdf4_file_name, "r")
	time_var = nc.variables["time"]
	dtime = netCDF4.num2date(time_var[:], time_var.units)

	nc_lon = nc["longitude"][:]
	nc_lat = nc["latitude"][:]
	nc_u10 = nc["u10"][:]
	nc_v10 = nc["v10"][:]
	nc_t2m = nc["t2m"][:]

	idx_lon = df["Lon"].apply(lambda x: np.argmin(np.absolute(nc_lon-x)))
	idx_lat = df["Lat"].apply(lambda x: np.argmin(np.absolute(nc_lat-x)))

	result_t2m = nc_t2m[:, idx_lat, idx_lon]-273
	result_u10 = nc_u10[:, idx_lat, idx_lon]
	result_v10 = nc_v10[:, idx_lat, idx_lon]

	result_t2m[unreliable_index] = np.nan
	result_u10[unreliable_index] = np.nan
	result_v10[unreliable_index] = np.nan

	return result_t2m, result_u10, result_v10


def get_1month_coeff_data(coeff_file_name):
	"""
	風力係数、偏角データの読み込み
	偏角（度）, 海流u, 海流v, F, 相関係数, 回帰に使ったデータ数, 海氷流速u, 海氷流速v, 地衡風u, 地衡風v
	"""
	df_coeffs = pd.read_csv(coeff_file_name, sep=',', dtype='float32')
	df_coeffs.columns = ["index", "angle", "mean_ocean_u", "mean_ocean_v", "A", "coef", "data_num", "mean_ice_u", "mean_ice_v", "mean_w_u", "mean_w_v"]
	df_coeffs = df_coeffs.drop("index", axis=1)
	df_coeffs[df_coeffs==999.] = np.nan
	return df_coeffs

def get_1month_hermert_data(hermert_file_name):
	df_hermert = pd.read_csv(hermert_file_name)
	return df_hermert

def cvt_date(dt):
	# "2013-01-01" -> "20130101"
	return str(dt)[:10].replace('-', '')

################################################################################################
#自分でデータを計算する場所

"""
風力係数などのデータ一式の取得
"""
def get_w_regression_data(wind_file_name, ice_file_name, coeff_file_name):
	"""
	1日ごとの地衡風と流氷速度と、30日分の平均海流を取ってきて、Aとthetaを計算
	"""
	w_data = get_1day_w_data(wind_file_name)
	w_u, w_v, w_speed = np.array(w_data["w_u"]), np.array(w_data["w_v"]), np.array(w_data["w_speed"])
	iw_data = get_1day_iw_data(ice_file_name)
	iw_u, iw_v, iw_speed = np.array(iw_data["iw_u"]), np.array(iw_data["iw_v"]), np.array(iw_data["iw_speed"])
	df_coeffs = get_1month_coeff_data(coeff_file_name)
	mean_ocean_u = np.array(df_coeffs["mean_ocean_u"])
	mean_ocean_v = np.array(df_coeffs["mean_ocean_v"])

	real_iw_u = iw_u - mean_ocean_u
	real_iw_v = iw_v - mean_ocean_v
	real_iw_speed = np.sqrt(real_iw_u*real_iw_u + real_iw_v*real_iw_v)
	A_by_day = real_iw_speed / w_speed
	theta_by_day = (np.arctan2(real_iw_v, real_iw_u) - np.arctan2(w_v, w_u))*180/np.pi
	idx1 = np.where(theta_by_day>=180)[0]
	theta_by_day[idx1] = theta_by_day[idx1]-360
	idx2 = np.where(theta_by_day<=-180)[0]
	theta_by_day[idx2] = theta_by_day[idx2]+360

	data = pd.DataFrame({"A_by_day": A_by_day, "theta_by_day": theta_by_day})
	return data


def get_w_hermert_data(wind_file_name, ice_file_name, coeff_file_name):
	"""
	1日ごとの地衡風と流氷速度と、30日分の平均海流を取ってきて、Aとthetaを計算
	"""
	w_data = get_1day_w_data(wind_file_name)
	w_u, w_v, w_speed = np.array(w_data["w_u"]), np.array(w_data["w_v"]), np.array(w_data["w_speed"])
	iw_data = get_1day_iw_data(ice_file_name)
	iw_u, iw_v, iw_speed = np.array(iw_data["iw_u"]), np.array(iw_data["iw_v"]), np.array(iw_data["iw_speed"])
	df_coeffs = get_1month_hermert_data(coeff_file_name)
	mean_ocean_u = np.array(df_coeffs["ocean_u"])
	mean_ocean_v = np.array(df_coeffs["ocean_v"])

	real_iw_u = iw_u - mean_ocean_u
	real_iw_v = iw_v - mean_ocean_v
	real_iw_speed = np.sqrt(real_iw_u*real_iw_u + real_iw_v*real_iw_v)
	A_by_day = real_iw_speed / w_speed
	theta_by_day = (np.arctan2(real_iw_v, real_iw_u) - np.arctan2(w_v, w_u))*180/np.pi
	idx1 = np.where(theta_by_day>=180)[0]
	theta_by_day[idx1] = theta_by_day[idx1]-360
	idx2 = np.where(theta_by_day<=-180)[0]
	theta_by_day[idx2] = theta_by_day[idx2]+360

	data = pd.DataFrame({"A_by_day": A_by_day, "theta_by_day": theta_by_day})
	return data


def get_masked_region_data(data, region):
	data = data
	if region is not None:
		region_all = list(data.Name.values.flatten())
		region_nan = list(set(region_all)-set(region))
		data_columns = set(data.columns)
		nan_columns = list(data_columns - set(["data_idx", "Label", "Name", "Lon", "Lat"]))
		data.loc[data.Name==area, nan_columns] = np.nan
	return data
