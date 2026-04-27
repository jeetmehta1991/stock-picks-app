# keepalive.ps1 - prevents Windows sleep while backtest is running
# Moves mouse 1 pixel every 4 minutes
# Run in a separate PowerShell window while backtest is running

Add-Type -AssemblyName System.Windows.Forms

Write-Host "Keep-alive started. Press Ctrl+C to stop."
Write-Host "This window must stay open while the backtest runs."

$i = 0
while ($true) {
    $pos = [System.Windows.Forms.Cursor]::Position
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(($pos.X + 1), $pos.Y)
    Start-Sleep -Seconds 1
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(($pos.X), $pos.Y)
    
    $i++
    if ($i % 15 -eq 0) {
        Write-Host "$(Get-Date -Format 'HH:mm:ss') - Keep-alive active ($($i * 4) min elapsed)"
    }
    
    Start-Sleep -Seconds 239
}
