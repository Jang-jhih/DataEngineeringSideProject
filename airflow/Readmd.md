# 資料倉儲作業流程

本檔案說明資料倉儲相關的自動化作業流程，使用Airflow進行排程，確保資料處理、更新及監控的自動化執行。

## 每日交易程式執行

### run_strategy.py
- **DAG_ID**: 執行所有交易程式
- **功能**: 執行所有交易程式，包含策略運算與執行。
- **排程時間**: 星期一至星期五，每天 20:30 自動執行。

### update_strategy.py
- **DAG_ID**: 上傳策略結果到discord
- **功能**: 將程式更新清單發送至discord，以便團隊追蹤策略表現。
- **排程時間**: 星期一至星期五，每天 20:30 自動執行。

### discord_alert.py
- **DAG_ID**: discord_提示
- **功能**: 發送OTC乖離率、RSI、ADLS等重要指標至discord。
- **排程時間**: 星期一至星期五，每天 20:30 自動執行。

### import_var.py
- **DAG_ID**: 環境變數轉換為Airflow變數
- **功能**: 將環境變數轉換並輸入至Airflow的variables中，便於作業流程使用。
- **排程時間**: 星期一至星期五，每天 20:30 自動執行。

### init_strategy.py
- **DAG_ID**: 策略ipynb轉換py
- **功能**: 將Jupyter Notebook中的交易策略程式轉換成.py檔，以便Airflow排程執行。
- **排程時間**: 星期一至星期五，每天 20:30 自動執行。

### test_connection.py
- **DAG_ID**: 測試Hive與WebHDFS連線
- **功能**: 測試與Hadoop的連線是否保持正常，確保資料處理無障礙。
- **排程時間**: 不定期執行，依實際需要手動觸發。

## 資料倉儲自動化

### datawarehouse_clickhouse.py
- **DAG_ID**: 資料倉儲_clickhouse
- **功能**: 實現資料自動倉儲至ClickHouse，支持大規模資料分析。
- **排程時間**: 每天 20:30 自動執行。

### datawarehouse_hive.py
- **DAG_ID**: 資料倉儲_hive
- **功能**: 實現資料自動倉儲至Hive，利於資料倉儲與查詢。
- **排程時間**: 每天 20:30 自動執行。

### pickle_to_postgres_dag.py
- **DAG_ID**: 資料塞postgres
- **功能**: 將資料導入至PostgreSQL，確保資料持久化存儲。
- **排程時間**: 不定期執行，依實際需要手動觸發。

## 參考文件

- [Docker Operator 問題解析](docker_operator.md)
