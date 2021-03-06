
from mpl_toolkits.basemap import Basemap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import glob
from datetime import datetime, date, timezone, timedelta
import os.path
import os
import seaborn as sns

import calc_data
import visualize
from main_v import mkdir, main_data

latlon145_file_name = calc_data.latlon145_file_name
latlon900_file_name = calc_data.latlon900_file_name
grid900to145_file_name = calc_data.grid900to145_file_name
ocean_grid_file = calc_data.ocean_grid_file
ocean_grid_145 = calc_data.ocean_grid_145
ocean_idx = calc_data.ocean_idx

latlon_ex = calc_data.get_lonlat_data()
basic_region = ["bearing_sea", "chukchi_sea", "beaufort_sea", "canada_islands", "hudson_bay", "buffin_bay", "labrador_sea", "greenland_sea", 
	"norwegian_sea", "barents_sea", "kara_sea", "laptev_sea", "east_siberian_sea", "north_polar"]

#基本的な変数の定義
start_list = []
n = 20000000
y_list = [3,4,5,6,7,8,9,10,13,14,15,16]
for i in y_list:
	m = n + i*10000
	for j in range(12):
		start_list.append(m + (j+1)*100 + 1)
start_ex_list = [20170101, 20170201, 20170301, 20170401, 20170501, 20170601,20170701,20170801]
start_list = np.sort(np.array(list(set(start_list)|set(start_ex_list)))).tolist()
M = len(start_list)



###################################################################################################################

def test_scatter():
	mkdir("../result_h/test/test_scatter/")
	for i, start in enumerate(start_list):
		print("******************  {}/{}  *******************".format(i+1, M))

		data_ex_dir = "../data/csv_Helmert_ex/Helmert_ex_" + str(start)[:-2] + ".csv"
		data = pd.read_csv(data_ex_dir)

		#data_01 = []
		try:
			#data_01 = data[((data.area_label==16)) & (data.R2<0.25)].dropna()
			data_01 = data[((data.area_label==4)) & ((data.A<0.003)|(data.ic0_30<97))].dropna()
			#data_01 = data[((data.area_label==8)|(data.area_label==10)) & (data.coastal_region_1==False) & (data.ic0_30<99)].dropna()
			#data_01 = data[((data.area_label==1)|(data.area_label==5)|(data.area_label==7)|(data.area_label==8)) & (data.coastal_region_1==False) & (data.ic0_30<99)].dropna()
			#data_01 = data.query('area_label in [1,4,5,7,10,11]')[(data.coastal_region_1==False) & (data.ic0_30<99)].dropna()
			#data_01 = data[(data.area_label.isin([1,4,5,7,10,11])) & (data.coastal_region_1==False) & (data.ic0_30<99)].dropna()
			
		except:
			data_01 = pd.DataFrame([])
		#print(data_01.head())
		if len(data_01) >= 4:
			sns.jointplot(x="ic0_30", y="A", data=data_01, kind="reg")

			save_name = "../result_h/test/test_scatter/" + "A_ic0_" + str(start)[:-2] + ".png"
			plt.savefig(save_name, dpi=600)
			plt.close()
		"""
		visualize.visual_non_line(
			data,
			mode=["scatter", ["sit_30", "A"]],
			save_name=save_dir + str(start)[:6] + ".png",
			show=False
			)
		"""
		print("\n")


#木村さんの平均海流とあっているかのプロット．散布図．
def test_ocean_plot():
	dirs = "../result_h/test/test_iw/"
	mkdir(dirs)

	start_list_plus_1month = start_list + [20170901]
	for i, start in enumerate(start_list):
		print("*******************  {}/{}  *******************".format(i+1, M))
		month_end = start_list_plus_1month[i+1]
		month_end = date(month_end//10000, (month_end%10000)//100, (month_end%10000)%100) - timedelta(days=1)
		end = start + month_end.day - 1
		
		try:
			#csv_Helmert_90の当該月のcsvを読み込む
			#hermert_file_name_90 = "../data/csv_Helmert_both_90/Helmert_both_90_" + str(start)[:6] + ".csv"
			#helmert_90_data = pd.read_csv(hermert_file_name_90)
			#csv_Helmert_30の当該月のcsvを読み込む
			hermert_file_name_30 = "../data/csv_Helmert_30/Helmert_30_" + str(start)[:6] + ".csv"
			helmert_30_data = pd.read_csv(hermert_file_name_30)
			#木村のcsvの読み込み(90)
			#coeff_file_name_90 = "../data/csv_A_90/ssc_amsr_ads" + str(start)[2:6] + "_90_fin.csv"
			#coeff_90_data = calc_data.get_1month_coeff_data(coeff_file_name_90)
			#木村のcsvの読み込み(30)
			coeff_file_name_30 = "../data/csv_A_30/ssc_amsr_ads" + str(start)[2:6] + "_30_fin.csv"
			coeff_30_data = calc_data.get_1month_coeff_data(coeff_file_name_30)
		except:
			continue
		#ocean_90_h_u = helmert_90_data["ocean_u_90"].values
		#ocean_90_h_v = helmert_90_data["ocean_v_90"].values
		#ocean_90_h_speed = np.sqrt(ocean_90_h_u**2 + ocean_90_h_v**2)
		ocean_30_h_u = helmert_30_data["ocean_u"].values
		ocean_30_h_v = helmert_30_data["ocean_v"].values
		ocean_30_h_speed = np.sqrt(ocean_30_h_u**2 + ocean_30_h_v**2)
		#ocean_90_c_u = coeff_90_data["mean_ocean_u"].values
		#ocean_90_c_v = coeff_90_data["mean_ocean_v"].values
		#ocean_90_c_speed = np.sqrt(ocean_90_c_u**2 + ocean_90_c_v**2)
		ocean_30_c_u = coeff_30_data["mean_ocean_u"].values
		ocean_30_c_v = coeff_30_data["mean_ocean_v"].values
		ocean_30_c_speed = np.sqrt(ocean_30_c_u**2 + ocean_30_c_v**2)

		"""
		fig, axes = plt.subplots(1, 2)
		ratio_90 = ocean_90_c_speed/ocean_90_h_speed
		ratio_30 = ocean_30_c_speed/ocean_30_h_speed
		axes[0].hist(ratio_30[ocean_idx][~np.isnan(ratio_30[ocean_idx])], range=(0,3), bins=150)
		axes[1].hist(ratio_90[ocean_idx][~np.isnan(ratio_90[ocean_idx])], range=(0,3), bins=150)
		"""
		ratio_w = ocean_30_c_u/ocean_30_h_u

		N_c_h = helmert_30_data["mean_iw_v"].values
		N_c_c = coeff_30_data["mean_ice_v"].values
		N_c_diff = N_c_h - N_c_c
		#plt.hist(N_c_diff[~np.isnan(N_c_diff)], range=(-5,5), bins=11, alpha=0.5)
		#tmp = N_c_diff[~np.isnan(N_c_diff)]
		#print(len(np.where(tmp>0)[0]))

		m = Basemap(lon_0=180, boundinglat=50, resolution='l', projection='npstere')
		m.drawcoastlines(color = '0.15')
		m.fillcontinents(color='#555555')
		lon = np.array(latlon_ex.Lon)
		lat = np.array(latlon_ex.Lat)
		x, y = m(lon, lat)
		x1 = np.reshape(x, (145,145), order='F')
		y1 = np.reshape(y, (145,145), order='F')
		dx1 = (x1[1,0]-x1[0,0])/2
		dy1 = (y1[0,1]-y1[0,0])/2
		x2 = np.linspace(x1[0,0], x1[144,0], 145)
		y2 = np.linspace(y1[0,0], y1[0,144], 145)
		xx, yy = np.meshgrid(x2, y2)
		xx, yy = xx.T, yy.T
		xx = np.hstack([xx, xx[:,0].reshape(145,1)])
		xx_ex = np.vstack([xx, (xx[144,:] + (xx[1,0]-xx[0,0]))])
		yy = np.vstack([yy, yy[0,:]])
		yy_ex = np.hstack([(yy[:,0].reshape(146,1) + (yy[0,0]-yy[0,1])), yy])

		data = np.ma.masked_invalid(N_c_diff)
		data1 = np.reshape(data, (145,145), order='F')
		m.pcolormesh(xx_ex-dx1, yy_ex+dy1, data1, cmap=plt.cm.jet, vmax=0.5, vmin=-0.5)
		#fig.colorbar(im, ax=ax)
		m.colorbar()

		#plt.hist(N_c_c[~np.isnan(N_c_c)], range=(20,35), bins=16)
		plt.savefig(dirs + "iw_v_" + str(start)[:6] + ".png", dpi=450)
		plt.close()





if __name__ == '__main__':
	#test_scatter()
	test_ocean_plot()









