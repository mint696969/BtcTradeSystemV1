# path: scripts/diag/diag_api.ps1
# desc: IPv4優先で取引所の疎通スモーク
& curl.exe --ssl-no-revoke -4 -s -o NUL -w "binance %{http_code} %{time_total}\n" https://api.binance.com/api/v3/ping
& curl.exe --ssl-no-revoke -4 -s -o NUL -w "bybit   %{http_code} %{time_total}\n" https://api.bybit.com/v5/market/time
& curl.exe --ssl-no-revoke -4 -s -o NUL -w "okx     %{http_code} %{time_total}\n" https://www.okx.com/api/v5/public/time
