from pathlib import Path

"""
dbt檔案合併腳本

此腳本用於合併指定dbt專案目錄下的.sql和.yml檔案，以便於檢閱和分享。它支持指定子目錄來限制合併範圍，
例如僅合併models目錄或models和target目錄下的檔案。

參數:
- project_dir: Path對象，指向dbt專案的根目錄。
- output_file: Path對象，指定輸出檔案的完整路徑。
- exts: 元組，定義要合併的檔案類型的擴展名。
- include_dirs: 列表，可選，指定要包含的子目錄名稱。如果未提供，則合併整個專案目錄下的檔案。

使用範例:
1. 僅合併models目錄下的檔案:
combine_dbt_files(dbt_project_directory, output_file_path, extensions, include_dirs=['models'])

2. 合併models和target目錄下的檔案:
combine_dbt_files(dbt_project_directory, output_file_path, extensions, include_dirs=['models', 'target'])

3. 合併整個專案目錄下的檔案:
combine_dbt_files(dbt_project_directory, output_file_path, extensions)
"""

# 設置您的dbt專案目錄
dbt_project_directory = Path('/usr/src/dbt_project')
# 指定輸出檔案的路徑
output_file_path = dbt_project_directory / 'dbt_combined_files.txt'

# 支持的文件擴展名
extensions = ('.sql', '.yml')

def combine_dbt_files(project_dir, output_file, exts, include_dirs=None):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        if include_dirs:
            directories = [project_dir / dir_name for dir_name in include_dirs]
        else:
            directories = [project_dir]
        
        for directory in directories:
            for path in directory.rglob('*'):
                if path.suffix in exts:
                    try:
                        with open(path, 'r', encoding='utf-8') as infile:
                            outfile.write(f"--- {path} ---\n")
                            outfile.write(infile.read())
                            outfile.write("\n\n")
                    except Exception as e:
                        print(f"Error processing file {path}: {e}")

# 使用範例
# 注意: 根據您的需求調整以下函數調用
combine_dbt_files(dbt_project_directory, output_file_path, extensions, include_dirs=['models'])
