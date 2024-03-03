# 量化交易系統專案

本專案是一個針對量化交易策略開發、測試與部署的完整框架。它包含了從數據處理、策略開發到結果分析的全套工具和流程。

## AI輔助開發工具簡介

### ChatGPT
- **描述**: ChatGPT是一個由OpenAI開發的大型語言模型，能夠理解和生成自然語言文本。它可以協助開發者通過自然語言指令生成程式碼，提供程式設計問題的解答，並優化程式碼結構。

### GitHub Copilot
- **描述**: GitHub Copilot是一個由GitHub和OpenAI共同開發的AI編碼助手，能夠根據注釋或者部分程式碼自動生成整段程式碼。它支持多種編程語言和框架，能夠大大提高開發效率。

### Perplexity
- **描述**: Perplexity是一款AI問答工具，專門設計用於解答編程相關問題。它能夠理解複雜的技術問題，提供準確、簡潔的答案和程式碼範例，幫助開發者解決疑難雜症。


## 專案結構

輔助開發AI包含:chatGPT、Github copilot、Perplexity

專案包含以下幾個主要的資料夾，每個資料夾都扮演著不同的角色：

### `airflow`
- **進度**: docker operator很常遇到要重複執行sudo chmod -R 777 /var/run/docker.sock，待解決。
- **用途**: 存放整個專案會用到的排程腳本。利用Airflow進行工作流程的自動化，包括數據處理、策略回測等。
- **相關內容**:交易程式警示與清單更新及倉儲更新。



### `jupyter`
- **進度**: spark_test.ipynb測試hdfs路徑有誤。
- **用途**: 包含Finlab交易程式、Spark以及一般Jupyter程式。這是策略開發和數據分析的工作區，提供了一個互動式的環境。




### `multi_processing`
- **進度**: 待加入基因演算法，初步完成superset常用dashbord後開始進行。
- **用途**: 多線程基因演算法的實現。用於策略優化，通過多線程技術提高計算效率。




### `superset`
- **進度**: 建置完成，已與clickhouse、Hive完成連線，尚未將doshbord加入。
- **用途**: BI與資料分析工具。Superset提供數據視覺化功能，幫助用戶分析交易數據和策略表現。
- **相關內容**:相關資料監控（待詳細）



### `hadoop`
- **進度**: 建置完成。
- **用途**: 包含Hadoop、Hive、Spark的大數據處理環境。用於處理和分析大規模數據集。
- **相關內容**:依superset需求調整



### `dbt`
- **進度**: 尚未建置，正進行實驗。
- **用途**: 數據建模和轉換工具。透過dbt在`datawarehouse`中進行數據轉換，支持更複雜的數據分析和報表生成流程。
- **相關內容**:superset SQL lab所有分析都在DBT完成，這樣可讓datahub data lineage更加完善，並且完整的相關資料描述


### `datahub`
- **進度**: 等待建置Gitlab-ci，就由ci datahub ingest dbt lineage，並且建置其他data lineage。
- **用途**：統一的數據接入層，用於集成和管理來自不同數據源的數據。提供靈活的數據集成功能，支持數據的標準化、清洗和轉換，確保數據質量和一致性。
- **相關內容**:完全使用gitlab-ci ingest


### `volume`
- **進度**: 建置完成，已經持續運作
- **用途**: 數據存儲解決方案，包含Postgres、ClickHouse、Redis。這些工具分別用於關係數據存儲、高速列式存儲和快速鍵值存儲。

### `CICD`
- **進度**: 尚未建置，正進行實驗。
- **用途**: 除了當前datahub需求以外，後續GCP自動交易程式需要透過CI進行部屬。



## datawarehouse

本專案中，`hadoop-spark`資料夾內的Hive和`volume`資料夾內的ClickHouse作為數據倉庫使用，Hive支持大規模數據的存儲和分析，ClickHouse作為BI倉儲。

- **Hive**: 提供SQL接口進行數據查詢，適用於批量數據處理和深度分析(hive://hive@hive-server:10000/default)。
- **ClickHouse**: 高性能列式存儲，適合快速數據讀取和實時分析。




