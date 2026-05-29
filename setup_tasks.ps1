$pyPath = (Get-Command py).Source
$action1 = New-ScheduledTaskAction -Execute $pyPath -Argument "-m uvicorn main:app --host 0.0.0.0 --port 8080" -WorkingDirectory "C:\aianycam\backend"
$action2 = New-ScheduledTaskAction -Execute $pyPath -Argument "crisp_bot_v2.py" -WorkingDirectory "C:\aianycam\backend"
$trigger1 = New-ScheduledTaskTrigger -AtStartup
$trigger2 = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 5) -Once -At (Get-Date)
$settings = New-ScheduledTaskSettingsSet -RestartCount 10 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Hours 0)
Register-ScheduledTask -TaskName "AiAnyCam-Backend" -Action $action1 -Trigger $trigger1,$trigger2 -Settings $settings -RunLevel Highest -Force
Register-ScheduledTask -TaskName "AiAnyCam-CrispBot" -Action $action2 -Trigger $trigger1,$trigger2 -Settings $settings -RunLevel Highest -Force
Write-Host "Done"
