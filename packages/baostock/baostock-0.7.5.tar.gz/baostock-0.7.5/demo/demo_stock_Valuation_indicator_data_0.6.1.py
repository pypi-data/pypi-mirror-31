import baostock as bs
import pandas as pd

#### 登陆系统 ####
lg = bs.login(user_id="anonymous", password="123456")
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### 获取沪深A股估值指标(日频)数据 ####
# peTTM    动态市盈率    
# psTTM    市销率    
# pcfNcfTTM    市现率    
# pbMRQ    市净率    
rs = bs.query_history_k_data("sh.600000",
    "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
    start_date='2015-01-01', end_date='2017-12-31', 
    frequency="d", adjustflag="3")
print('query_history_k_data respond error_code:'+rs.error_code)
print('query_history_k_data respond  error_msg:'+rs.error_msg)

#### 打印结果集 ####
result = pd.DataFrame(columns=["date","code","close","peTTM","pbMRQ","psTTM","pcfNcfTTM"])
while (rs.error_code == '0') & rs.next():
    # 分页查询，将每页信息合并在一起
    result = result.append(rs.get_row_data(), ignore_index=True)

# columns rename
result.rename(columns={'date':'date日期','code': 'code证券代码','close': 'close收盘价','peTTM': 'peTTM动态市盈率','pbMRQ': 'pbMRQ市净率','psTTM': 'psTTM市销率','pcfNcfTTM': 'pcfNcfTTM市现率'}, inplace=True)    
 
#### 结果集输出到csv文件 ####   
result.to_csv("D:\\history_A_stock_valuation_indicator_data.csv", encoding="gbk", index=False)
print(result)

#### 登出系统 ####
bs.logout()