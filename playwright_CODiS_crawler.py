#python -m playwright codegen --target python -o test.py -b chromium https://codis.cwa.gov.tw/StationData

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time
import os
from tqdm import tqdm

class TqdmWrapper(tqdm):
    """提供了一個 `total_time` 格式參數"""
    
    @property
    def format_dict(self):
        # 取得父類別的format_dict
        d = super().format_dict
        
        # 計算總共花費的時間
        total_time = d["elapsed"] * (d["total"] or 0) / max(d["n"], 1)
        
        # 更新字典以包含總共花費的時間
        d.update(total_time='總計: ' + self.format_interval(total_time))

        # 返回更新後的字典
        return d

# 定義站名
station_name = "大寮 (C0V730)"
station_code = station_name.split()[-1].strip("()")  # 提取站號

# 定義日期區間
start_date = datetime(2023, 1, 1)  # 開始日期
end_date = datetime(2023, 12, 31)    # 結束日期

# 基本下載路徑
base_download_path = "C:/R/Python/Playwright/download/"

# 建立下載路徑
station_download_path = os.path.join(base_download_path, station_code)

# 如果資料夾不存在，則建立它
if not os.path.exists(station_download_path):
    os.makedirs(station_download_path)

# 在下載時使用 station_download_path 作為儲存路徑
download_path = station_download_path

# 計算日期間隔天數
days_diff = (end_date - start_date).days

# 生成等長的數字序列
number_list = list(range(days_diff + 1))
number_list

def run(playwright):
    browser = playwright.chromium.launch(headless=False)  # 啟動瀏覽器
    print('browser open')
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    page.goto("https://codis.cwa.gov.tw/StationData")
    page.wait_for_load_state("load")
    page.get_by_label("自動氣象站").check()
    #page.locator("#station_area").select_option("高雄市")
    #time.sleep(1)
    page.locator("li").filter(has_text="站名站號").get_by_role("combobox").click()
    page.locator("li").filter(has_text="站名站號").get_by_role("combobox").fill(station_name)
    page.locator(".leaflet-marker-icon > .icon_container > .marker_bgcolor > .bg_triangle").first.click()
    page.get_by_role("button", name="觀看時序圖報表").click()
    
    # 獲取當前日期
    current_date = datetime.now()

    # 獲取前一天的日期
    previous_date = current_date - timedelta(days=1)

    # 格式化日期
    year = previous_date.strftime("%Y")
    month = previous_date.strftime("%m月")
    day = previous_date.strftime("%d")

     # 選擇年份
    if previous_date.year != end_date.year:
        page.locator("div:nth-child(5) > .lightbox-tool-type-ctrl > .lightbox-tool-type-ctrl-form > label").click()
        time.sleep(1)
        page.get_by_text(str(previous_date.year), exact=True).click()  # 選擇當前年份
        time.sleep(1)
        page.get_by_text(str(end_date.year)).click()  # 選擇目標年份
        page.get_by_text("Continue").click()
        print('year select ok')
        time.sleep(1)
    # 選擇月份
    if previous_date.month != end_date.month:
        page.locator("div:nth-child(5) > .lightbox-tool-type-ctrl > .lightbox-tool-type-ctrl-form > label").click()
        print('month select start')
        page.get_by_text(f"月{previous_date.day}日").click()
        print('month select ')
        print(f"{previous_date.month}月")
        time.sleep(1)
        print('end_date select ')
        print(f"{end_date.month}月")
        page.get_by_text(f"{end_date.month}月").click()
        print('month select ok')
        time.sleep(1)
        page.get_by_text("Continue").click()
        time.sleep(1)
    # 選擇日期
    if previous_date.day != end_date.day:
        print("end_date.day select:")
        print(end_date.day)
        page.locator("div:nth-child(5) > .lightbox-tool-type-ctrl > .lightbox-tool-type-ctrl-form > label").click()
        page.get_by_text(f"{end_date.day}", exact=True).first.click()
        print('date select ok')
   
    # 處理下載
    
    for i in   TqdmWrapper(number_list, desc="                                               下載進度",ncols=200, unit='file', unit_scale=True):
        # 根據結束時間往前推算當前日期
        current_date = end_date - timedelta(days=i)

        # 構建預期的檔名（格式為：站號-年-月-日.csv）
        expected_filename = f"{station_code}-{current_date.year}-{current_date.month:02d}-{current_date.day:02d}.csv"
        expected_filepath = os.path.join(download_path, expected_filename)

        # 檢查檔案是否存在
        if os.path.exists(expected_filepath):
            print(f"\r檔案 {expected_filename} 已存在，跳過下載。", end=" ")
            page.locator("div:nth-child(5) > .lightbox-tool-type-ctrl > .lightbox-tool-type-ctrl-form > label > .datetime-tool > div").first.click()
            #time.sleep(0.5)
            continue

        # 如果檔案不存在，執行下載操作
        with page.expect_download() as download_info:
            page.locator(".lightbox-tool-type-ctrl-btn-group > div").first.click()
            download = download_info.value
            download.save_as(download_path+"/" +  download.suggested_filename)  # 儲存檔案
            #print(download.url)  # 獲取下載的url地址
            # 這一步只是下載下來，生成一個隨機uuid值儲存，程式碼執行完會自動清除
            print("\r"+"檔案不存在，以下載 : "+download.suggested_filename,end=" ")  # 獲取下載的檔名
            time.sleep(1)
            page.locator("div:nth-child(5) > .lightbox-tool-type-ctrl > .lightbox-tool-type-ctrl-form > label > .datetime-tool > div").first.click()
            time.sleep(2)
        
    context.close()
    browser.close()
    
    
with sync_playwright() as playwright:
    run(playwright)



#----------------------資料整理----------------------
print(station_download_path)

import pandas as pd
import os
import glob
from prettytable import PrettyTable


def print_df_as_table(df, max_rows=5):
    """
    Print the first five rows of a Pandas DataFrame as a PrettyTable.

    Parameters:
    df (pandas.DataFrame): The DataFrame to print.
    """
    table = PrettyTable()
    table.field_names = df.columns.tolist()

    for row in df.head(max_rows).itertuples(index=False):
        table.add_row(row)

    print(table)
    
    
#匯入station_download_path資料夾下所有csv檔案，並將檔名作為一個新的欄位
os.chdir(station_download_path)
extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

# 讀取所有檔案，跳過第二行，並新增檔名作為新列
combined_csv = pd.concat([pd.read_csv(f, skiprows=[1]).assign(檔名=os.path.basename(f)) for f in all_filenames])

#提取檔名中的日期新增到新的欄位
combined_csv['日期'] = combined_csv['檔名'].str.extract('(\d{4}-\d{2}-\d{2})')

#刪除檔名欄位
combined_csv = combined_csv.drop(['檔名'], axis=1)
print_df_as_table(combined_csv)
combined_csv.to_csv( "combined_csv.csv", index=False, encoding='utf-8-sig')


print_df_as_table(combined_csv,10)



# --------------繪製風花圖 --------------
import matplotlib.pyplot as plt
import numpy as np
from windrose import WindroseAxes

# 轉換為數值
combined_csv['風向(360degree)'] = pd.to_numeric(combined_csv['風向(360degree)'], errors='coerce')
combined_csv['風速(m/s)'] = pd.to_numeric(combined_csv['風速(m/s)'], errors='coerce')

# 移除任何包含 NaN 的行
combined_csv.dropna(subset=['風向(360degree)', '風速(m/s)'], inplace=True)

# 轉換為 numpy 陣列
directions = combined_csv['風向(360degree)'].to_numpy()
speeds = combined_csv['風速(m/s)'].to_numpy()

# 繪製風花圖
ax = WindroseAxes.from_ax()
ax.bar(directions, speeds, normed=True, opening=0.8, edgecolor='white')

# 設定標籤和標題
ax.set_legend()
ax.set_title("windrose plot")
max_value = int(combined_csv['風速(m/s)'].max()) + 1
print(max_value)
# 修改Y軸以5為間隔
yticks = np.arange(0, 26, 5) # 設定Y軸間距
ax.set_yticks(yticks)
ax.set_yticklabels([f"{i}%" for i in yticks])

plt.show()

# --------------繪製風花圖子圖 --------------
import seaborn as sns
from windrose import WindroseAxes, plot_windrose

# 假設 combined_csv 是你的 DataFrame
# 轉換 '日期' 欄位為 datetime 類型並提取月份
combined_csv['日期'] = pd.to_datetime(combined_csv['日期'])
combined_csv['month'] = combined_csv['日期'].dt.month

# 風速和風向資料
combined_csv['ws'] = combined_csv['風速(m/s)']
combined_csv['wd'] = combined_csv['風向(360degree)']

def plot_windrose_subplots(data, *, direction, var, color=None, **kwargs):
    """wrapper function to create subplots per axis"""
    ax = plt.gca()
    ax = WindroseAxes.from_ax(ax=ax)
    plot_windrose(direction_or_df=data[direction], var=data[var], ax=ax, **kwargs)

# 建立子圖網格
g = sns.FacetGrid(
    data=combined_csv,
    col="month",  # 使用提取的月份
    col_wrap=3,
    subplot_kws={"projection": "windrose"},
    sharex=False,
    sharey=False,
    despine=False,
    height=3.5,
)

# 對映資料到子圖
g.map_dataframe(
    plot_windrose_subplots,
    direction="wd",
    var="ws",
    normed=True,
    bins=(0.1, 1, 2, 3, 4, 5),
    calm_limit=0.1,
    kind="bar",
)

# 子圖調整
for ax in g.axes:
    ax.set_legend(
        title="$m \cdot s^{-1}$", 
        bbox_to_anchor=(1.1, 1),  # 將圖例放在右上角外側
        loc="upper left"          # 相對於 bbox_to_anchor 指定的點的 'upper left' 位置
    )
    ax.set_rgrids(y_ticks, y_ticks)

plt.subplots_adjust(wspace=-0.2)
plt.show()


# --------------繪製風花圖_地圖 --------------
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt  # 正確匯入 cimgt
import matplotlib.pyplot as plt
from windrose import WindroseAxes
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd
import numpy as np
import cartopy.feature as cfeature#預定義常量
# 假設 combined_csv 是你的 DataFrame
# 轉換資料類型並移除 NaN
combined_csv['風向(360degree)'] = pd.to_numeric(combined_csv['風向(360degree)'], errors='coerce')
combined_csv['風速(m/s)'] = pd.to_numeric(combined_csv['風速(m/s)'], errors='coerce')
combined_csv.dropna(subset=['風向(360degree)', '風速(m/s)'], inplace=True)

# 轉換為 numpy 陣列
directions = combined_csv['風向(360degree)'].to_numpy()
speeds = combined_csv['風速(m/s)'].to_numpy()
station_longitude = 120.3957    # 經度
station_latitude = 22.6056  # 緯度

# 指定地圖的範圍
minlon, maxlon, minlat, maxlat = (station_longitude-0.5,station_longitude+0.5, station_latitude-0.5, station_latitude+0.5)

# 選擇 Stamen 地圖圖源
stamen_terrain = cimgt.Stamen('terrain-background')

# 建立地圖
proj = ccrs.PlateCarree()
fig = plt.figure(figsize=(10, 8))
main_ax = fig.add_subplot(1, 1, 1, projection=proj)
main_ax.set_extent([minlon, maxlon, minlat, maxlat], crs=proj)
main_ax.coastlines()
main_ax.add_feature(cfeature.LAND)#新增陸地
main_ax.add_feature(cfeature.COASTLINE,lw = 0.3)#新增海岸線
main_ax.add_feature(cfeature.RIVERS,lw = 0.25)#新增河流
#ax.add_feature(cfeat.RIVERS.with_scale('50m'),lw = 0.25)  # 載入解析度為50的河流
main_ax.add_feature(cfeature.LAKES)#新增湖泊
main_ax.add_feature(cfeature.BORDERS, linestyle = '-',lw = 0.25)#不推薦，因為該預設參數會使得我國部分領土丟失
main_ax.add_feature(cfeature.OCEAN)#新增海洋



# 在地圖上新增風花圖的位置
wrax = inset_axes(
    main_ax,
    width=1,  # size in inches
    height=1,  # size in inches
    loc="center",  # center bbox at given position
    bbox_to_anchor=(station_longitude, station_latitude),  # position of the axe
    bbox_transform=main_ax.transData,  # use data coordinate (not axe coordinate)
    axes_class=WindroseAxes,  # specify the class of the axe
)

# 繪製風花圖
wrax.bar(directions, speeds, edgecolor='none', normed=True, opening=0.8, nsector=16, bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
         blowto=False)

# 設定風花圖示題
# wrax.set_title("Wind Rose")

plt.show()
