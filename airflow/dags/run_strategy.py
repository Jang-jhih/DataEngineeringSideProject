
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.models import Variable
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime
from airflow.utils.dates import days_ago
import os
from airflow.operators.dagrun_operator import TriggerDagRunOperator



# DAG 的基本參數
default_args = {
    'owner': 'airflow',
    # 'start_date': datetime(2024, 1, 16),
    'start_date': days_ago(1),
    'retries': 1,
}

# DAG 定義
dag = DAG(
    '執行所有交易程式',
    default_args=default_args,
    description='Run all Python scripts in the strategy folder in sequence',
    schedule_interval='30 20 * * *',
    tags=['strategy'],
)

# 假設您的所有 Python 腳本都位於 /opt/airflow/strategy
scripts_path = "/opt/airflow/strategy"

script_files = [                                
                'ETF.py',
                'Monthly_Revenue_Momentum.py',
                'Volume_Contracting_Price.py',
                'PB_Income_Growth.py',
                '國家認證.py',
                '穩穩抬轎.py',
                'left.py',
                '_5_Line.py',
                'High_Dividend_Yield_1.py',
                'High_Dividend_Yield_2.py',
                'Relative_Strength_Value.py',
                'Financial_Targets.py',
                '營收股價雙渦輪.py',
                'PE_Growth.py',
                'Short_Term_Trading.py',
                'Genetic_Algorithm.py',
                'Financial_Health.py',
                'boss_inv.py',
                '瘋龍流Ultra.py',
                '_Composit_Program.py',
                '除息兔.py',
                '除權息放空兔.py',
                ]
# 儲存上一個任務，用於設定依賴
previous_task = None

# 為每個 Python 腳本創建一個任務並設定依賴
for script in script_files:
    task = BashOperator(
        task_id=f'run_{script[:-3]}',  # 移除 .py 得到任務 ID
        bash_command=f'python {os.path.join(scripts_path, script)} ',
        trigger_rule=TriggerRule.ALL_DONE,
        env={
            'PYTHONPATH': Variable.get('CONDITION_PATH', '/home/jovyan/work/notebooks/workspace/condition'),
            'CONDITION_PATH': Variable.get('CONDITION_PATH', ''),
            'FINLAB_API_KEY': Variable.get('FINLAB_API_KEY', ''),
            'TEST_ENV': Variable.get('TEST_ENV', ''),
            'OPENAI_API_KEY': Variable.get('OPENAI_API_KEY', ''),
            'Stock_Market_pred': Variable.get('Stock_Market_pred', ''),
            'Warning_pred': Variable.get('Warning_pred', ''),
            'For_jacob_pred': Variable.get('For_jacob_pred', ''),
            'high_sharpe_ratio_pred': Variable.get('high_sharpe_ratio_pred', ''),
            'For_ETF_pred': Variable.get('For_ETF_pred', ''),
            'Strategy_DOC': Variable.get('Strategy_DOC', ''),
            'RSI_DOC': Variable.get('RSI_DOC', ''),
            'ADLS_DOC': Variable.get('ADLS_DOC', ''),
            'Deviation_DOC': Variable.get('Deviation_DOC', ''),
            'MACD_LongShortOrderPosition_DOC': Variable.get('MACD_LongShortOrderPosition_DOC', ''),
            'DATA_VOLUME': Variable.get('DATA_VOLUME', ''),
            'LOG_VOLUME': Variable.get('LOG_VOLUME', ''),
            'LAB_PATH': Variable.get('LAB_PATH', ''),
            'STRATEGY_PATH': Variable.get('STRATEGY_PATH', ''),
            },
        dag=dag,
    )



    # 如果有先前的任務，則設定當前任務依賴於先前的任務
    if previous_task is not None:
        previous_task >> task

    # 更新 previous_task 為當前任務
    previous_task = task

# 在所有腳本執行任務完成後，添加一個觸發器任務
trigger_update_strategy_task = TriggerDagRunOperator(
    task_id="trigger_update_strategy",
    trigger_dag_id="上傳策略結果到discord",  # 確保這裡的 DAG ID 與 update_strategy.py 中定義的 DAG ID 相匹配
    dag=dag,
)

# 確保觸發器任務只在最後一個腳本任務完成後執行
if previous_task is not None:
    previous_task >> trigger_update_strategy_task