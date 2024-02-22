from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import os
import shutil
from nbconvert import PythonExporter
import nbformat

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
    lab_path = Variable.get('LAB_PATH')
    folder = os.path.join(lab_path, 'combie_strategy')
    if os.path.exists(folder):
        print('delete folder: ', folder)
        shutil.rmtree(folder)

def create_dest_dir(**kwargs):
    dest_dir = Variable.get('STRATEGY_PATH')
    if not os.path.exists(dest_dir):
        print(f"創建目標目錄：{dest_dir}")
        os.makedirs(dest_dir)


def convert_notebooks(**kwargs):
    source_dir = '/home/jovyan/work/notebooks'
    dest_dir = Variable.get('STRATEGY_PATH')
    exporter = PythonExporter()

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
        python_callable=create_dest_dir,
        provide_context=True,
    )

    t3 = PythonOperator(
        task_id='convert_notebooks',
        python_callable=convert_notebooks,
        provide_context=True,
    )

    t1 >> t2 >> t3
