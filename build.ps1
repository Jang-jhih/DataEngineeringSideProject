function Build-And-Push {
  param (
    [string]$serviceName,
    [string]$imageName,
    [string]$dockerfileName
  )

  # 構建映像
  Write-Host "Building image for service: $serviceName..."
  $buildResult = docker build --no-cache -f $dockerfileName -t $imageName .
  if ($LASTEXITCODE -ne 0) { throw "Building image failed for service: $serviceName" }

  # 推送映像到 Docker Hub
  Write-Host "Pushing image: $imageName to Docker Hub..."
  $pushResult = docker push $imageName
  if ($LASTEXITCODE -ne 0) { throw "Pushing image failed: $imageName" }
}

# 登錄 Docker Hub
Write-Host "Logging in to Docker Hub..."
$loginResult = docker login
if ($LASTEXITCODE -ne 0) { throw "Docker login failed" }

# 構建並推送 airflow 映像
# Build-And-Push -serviceName "airflow" -imageName "zebraking30/finlab-airflow:latest" -dockerfileName "Dockerfile.airflow"
#jupyter
Build-And-Push -serviceName "jupyter" -imageName "zebraking30/finlab-jupyter:latest" -dockerfileName "Dockerfile.jupyter"


Write-Host "All images pushed to Docker Hub successfully!"
