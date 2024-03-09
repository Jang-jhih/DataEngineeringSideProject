
## 資料倉儲

### run_strategy.py
DAG_ID:執行所有交易程式
功能:執行所有交易程式
schedule:星期一到五，每天 20:30 執行

### update_strategy.py
DAG_ID:上傳策略結果到discord
功能:程式更新清單發送到discord
schedule:星期一到五，每天 20:30 執行


### discord_alart.py
DAG_ID:discord_提示
功能:把OTC乖離率.RSI.ADLS
schedule:星期一到五，每天 20:30 執行

### import_var.py
DAG_ID:環境變數轉換為Airflow變數
功能:把環境變數放入airflow的variable
schedule:星期一到五，每天 20:30 執行

### init_strategy.py
DAG_ID:策略ipynb轉換py
功能:把jupyter的交易程式轉換程.py讓airflow排程執行
schedule:星期一到五，每天 20:30 執行

### test_connection.py
DAG_ID:測試hive與webhdfs連線
功能:測試hadoop是否保持正常
schedule:



### datawarehouse_clickhouse.py
DAG_ID:資料倉儲_clickhouse
功能:自動倉儲
schedule:每天 20:30 執行

### datawarehouse_hive.py
DAG_ID:資料倉儲_hive
功能:自動倉儲
schedule:每天 20:30 執行

### pickle_to_postgres_dag.py
DAG_ID:資料塞postgres
功能:把資料塞入postgres
schedule:


[docker opator有問題](docker_oprator.md)
