from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import os
import shutil
from nbconvert import PythonExporter
import nbformat
from airflow.operators.dagrun_operator import TriggerDagRunOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def delete_folder(**kwargs):
    '''
    刪除 combie_strategy 所需的pickle檔案，
    不然組合程式會拿到舊的檔案
    
    '''
    lab_path = Variable.get('LAB_PATH')
    folder = os.path.join(lab_path, 'combie_strategy')
    if os.path.exists(folder):
        print('delete folder: ', folder)
        shutil.rmtree(folder)

def create_dest_dirs(**kwargs):
    '''
    strategy與GA創建目標目錄，
    strategy內的程式要讓其他dag執行。
    
    '''
    dest_dir = Variable.get('STRATEGY_PATH')
    strategy_dir = os.path.join(dest_dir, 'strategy')
    ga_dir = os.path.join(dest_dir, 'GA')
    
    for dir_path in [dest_dir, strategy_dir, ga_dir]:
        if not os.path.exists(dir_path):
            print(f"創建目標目錄：{dir_path}")
            os.makedirs(dir_path)


def convert_notebooks(**kwargs):
    '''
    將策略與GA的ipynb檔案轉換為py檔案，
    並保存至指定目錄。
    
    '''
    source_dirs = ['/home/jovyan/work/notebooks', '/home/jovyan/work/GA']
    dest_dirs = [os.path.join(Variable.get('STRATEGY_PATH'), 'strategy'), 
                 os.path.join(Variable.get('STRATEGY_PATH'), 'GA')]
    exporter = PythonExporter()

    for source_dir, dest_dir in zip(source_dirs, dest_dirs):
        for filename in os.listdir(source_dir):
            if not filename.endswith(".ipynb"):
                continue
            
            full_source_path = os.path.join(source_dir, filename)
            print(f"處理文件：{full_source_path}")

            # 使用 nbformat 讀取 notebook 檔案
            with open(full_source_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)

            # 遍歷 notebook 中的所有 cell
            cells_to_keep = []
            remove_flag = False
            for cell in nb.cells:
                if cell.cell_type == 'markdown' and "參數測試" in cell.source:
                    remove_flag = True
                if not remove_flag:
                    cells_to_keep.append(cell)

            # 只保留應該保留的 cell
            nb.cells = cells_to_keep

            # 將更新後的 notebook 轉換為 Python 腳本
            output, resources = exporter.from_notebook_node(nb)
            dest_filename = filename.replace(".ipynb", ".py")
            full_dest_path = os.path.join(dest_dir, dest_filename)
            with open(full_dest_path, "w", encoding="utf-8") as f:
                f.write(output)

            print(f"已將 {filename} 轉換為 {dest_filename} 並保存至 {full_dest_path}")

def copy_yaml_files(**kwargs):
    '''
    把GA需要的yaml檔案複製到指定目錄。
    '''
    source_dir = '/home/jovyan/work/GA'
    dest_dir = os.path.join(Variable.get('STRATEGY_PATH'), 'GA')

    for filename in os.listdir(source_dir):
        if filename.endswith(".yaml"):
            full_source_path = os.path.join(source_dir, filename)
            full_dest_path = os.path.join(dest_dir, filename)
            shutil.copy2(full_source_path, full_dest_path)
            print(f"已複製 {filename} 到 {full_dest_path}")

with DAG(
    '策略ipynb轉換py',
    default_args=default_args,
    description='Convert Jupyter notebooks to Python scripts',
    schedule_interval='30 20 * * *',  # Run every day at 8:30 PM
    tags=['strategy'],
) as dag:

    t1 = PythonOperator(
        task_id='delete_folder',
        python_callable=delete_folder,
        provide_context=True,
    )

    t2 = PythonOperator(
        task_id='create_dest_dir',
        python_callable=create_dest_dirs,
        provide_context=True,
    )

    t3 = PythonOperator(
        task_id='convert_notebooks',
        python_callable=convert_notebooks,
        provide_context=True,
    )

    t4 = PythonOperator(
        task_id='copy_yaml_files',
        python_callable=copy_yaml_files,
        provide_context=True,
    )

    trigger_update_strategy_task = TriggerDagRunOperator(
        task_id="run_strategy",
        trigger_dag_id="執行所有交易程式",  # 要觸發的 DAG ID
        dag=dag,
)

    t1 >> t2 >> t3 >> t4 >> trigger_update_strategy_task
