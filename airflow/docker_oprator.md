### 使用systemd服務（有資安疑慮的作法，但是docker operator時常出現權限不足的問題）

1. **創建一個systemd單元文件**：首先，需要創建一個自定義的systemd服務文件，這個服務將在系統啟動時運行。打開終端，使用您喜歡的文本編輯器創建一個新的文件，例如使用`nano`：

    ```bash
    sudo nano /etc/systemd/system/docker-sock-perm.service
    ```

2. **添加服務配置**：在打開的編輯器中，輸入以下內容：

    ```ini
    [Unit]
    Description=Set Docker Socket Permission
    After=docker.service

    [Service]
    Type=oneshot
    ExecStart=/bin/chmod 777 /var/run/docker.sock

    [Install]
    WantedBy=multi-user.target
    ```

    這個配置指定了在`docker.service`之後運行一個命令，將`/var/run/docker.sock`的權限設置為777。

3. **啟用和啟動服務**：保存文件並退出編輯器。然後，啟用並啟動您剛剛創建的服務：

    ```bash
    sudo systemctl enable docker-sock-perm.service
    sudo systemctl start docker-sock-perm.service
    ```

4. **檢查服務狀態**：您可以檢查服務的狀態，以確保它正確運行：

    ```bash
    sudo systemctl status docker-sock-perm.service
    ```
