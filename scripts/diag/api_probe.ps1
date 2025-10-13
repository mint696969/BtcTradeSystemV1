# path: scripts/diag/api_probe.ps1
# desc: 4取引所( bitFlyer / Binance / Bybit / OKX )の疎通＋中身チェック＋レポート
param(
  [ValidateSet('v4','v6')] [string]$IpVer = 'v4',
  [int]$TimeoutSec = 10
)

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = 'Stop'

function CurlCall($url, $ver, $timeout) {
  $v = if ($ver -eq 'v6') { '-6' } else { '-4' }

  # 本文/ヘッダを別ファイルに出し、標準出力は -w のフォーマット文字列だけにする
  $tmpBody = New-TemporaryFile
  $tmpHdr  = New-TemporaryFile
  $fmt     = '%{http_code}|||%{time_total}|||%{remote_ip}'

  # 標準出力には -w の結果だけが出るように -D <file> -o <file> を併用
  $wout = & curl.exe --ssl-no-revoke $v -s -m $timeout `
           -D $tmpHdr -o $tmpBody -w $fmt $url 2>$null

  $parts = $wout -split '\|\|\|'
  $code = if ($parts.Length -ge 1) { [int]($parts[0].Trim()) } else { 0 }
  $sec  = if ($parts.Length -ge 2) { [double]($parts[1].Trim()) } else { -1.0 }
  $rip  = if ($parts.Length -ge 3) { $parts[2].Trim() } else { '' }

  $body = Get-Content $tmpBody -Raw
  # ヘッダは今は未使用だが、必要ならここで解析可能
  # $hdr  = Get-Content $tmpHdr -Raw

  Remove-Item $tmpBody,$tmpHdr -Force
  return [pscustomobject]@{ code=$code; sec=$sec; ip=$rip; body=$body }
}

function Test-JsonPath($obj, $paths) {
  foreach($p in $paths){
    $cur = $obj
    foreach($seg in ($p -split '\.')){
      if ($seg -match '^\[(\d+)\]$'){
        $idx = [int]$Matches[1]
        if (-not ($cur -is [System.Collections.IList]) -or $cur.Count -le $idx) { return $false }
        $cur = $cur[$idx]
      } else {
        if (-not ($cur.PSObject.Properties.Name -contains $seg)) { return $false }
        $cur = $cur.$seg
      }
      if ($null -eq $cur) { return $false }
    }
  }
  return $true
}

# 収集対象（必要に応じて増減可）
$targets = @(
  # bitFlyer（BTC_JPY）
  @{ ex='bitflyer'; sym='BTC_JPY';
     time='https://api.bitflyer.com/v1/gethealth';        time_paths=@('status');
     ticker='https://api.bitflyer.com/v1/ticker?product_code=BTC_JPY';   ticker_paths=@('product_code','best_bid','best_ask','ltp');
     ob='https://api.bitflyer.com/v1/getboard?product_code=BTC_JPY';     ob_paths=@('mid_price','bids.[0].price','asks.[0].price');
     trades='https://api.bitflyer.com/v1/getexecutions?product_code=BTC_JPY&count=5'; trades_paths=@('[0].price','[0].side','[0].exec_date')
  },
  # Binance（BTCUSDT）
  @{ ex='binance'; sym='BTCUSDT';
     time='https://api.binance.com/api/v3/time';          time_paths=@('serverTime');
     ticker='https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT'; ticker_paths=@('bidPrice','askPrice');
     ob='https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=5';  ob_paths=@('bids.[0].[0]','asks.[0].[0]');
     trades='https://api.binance.com/api/v3/trades?symbol=BTCUSDT&limit=5'; trades_paths=@('[0].price','[0].qty','[0].time')
  },
  # Bybit v5（BTCUSDT, linear）
  @{ ex='bybit'; sym='BTCUSDT';
     time='https://api.bybit.com/v5/market/time';         time_paths=@('time');
     ticker='https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT'; ticker_paths=@('result.list.[0].bid1Price','result.list.[0].ask1Price');
     ob='https://api.bybit.com/v5/market/orderbook?category=linear&symbol=BTCUSDT&limit=5'; ob_paths=@('result.a.[0].[0]','result.b.[0].[0]');
     trades='https://api.bybit.com/v5/market/recent-trade?category=linear&symbol=BTCUSDT&limit=5'; trades_paths=@('result.list.[0].p','result.list.[0].T')
  },
  # OKX（BTC-USDT）
  @{ ex='okx'; sym='BTC-USDT';
     time='https://www.okx.com/api/v5/public/time';       time_paths=@('data.[0].ts');
     ticker='https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT'; ticker_paths=@('data.[0].bidPx','data.[0].askPx');
     ob='https://www.okx.com/api/v5/market/books?instId=BTC-USDT&sz=5'; ob_paths=@('data.[0].bids.[0].[0]','data.[0].asks.[0].[0]');
     trades='https://www.okx.com/api/v5/market/trades?instId=BTC-USDT&limit=5'; trades_paths=@('data.[0].px','data.[0].ts')
  }
)

# 出力
$DATA = $env:BTC_TS_DATA_DIR; if (-not $DATA) { $DATA = 'D:\BtcTS_V1\data' }
$outDir = Join-Path $DATA 'diag'
New-Item -ItemType Directory -Force $outDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$jsonPath = Join-Path $outDir "api_probe_$stamp.json"
$csvPath  = Join-Path $outDir "api_probe_$stamp.csv"

$all = @()
foreach($t in $targets){
  foreach($kind in @(
    @{k='time';    paths=$t.time_paths;    url=$t.time},
    @{k='ticker';  paths=$t.ticker_paths;  url=$t.ticker},
    @{k='orderbook';paths=$t.ob_paths;     url=$t.ob},
    @{k='trades';  paths=$t.trades_paths;  url=$t.trades}
  )){
    $res = CurlCall $kind.url $IpVer $TimeoutSec
    $ok = $false; $note = ''; $payload = $null
    if ($res.code -eq 200) {
      try {
        $payload = $res.body | ConvertFrom-Json -ErrorAction Stop
        $ok = Test-JsonPath $payload $kind.paths
        if (-not $ok) { $note = 'JSON schema miss' }
      } catch { $note = 'JSON parse error' }
    } else {
      $note = "HTTP $($res.code)"
    }
    $all += [pscustomobject]@{
      exchange=$t.ex; topic=$kind.k; symbol=$t.sym;
      ipver=$IpVer; http_code=$res.code; time_s=[math]::Round($res.sec,3); remote_ip=$res.ip;
      ok=$ok; note=$note
    }
  }
}

# CSV / JSON 保存
$all | Export-Csv -NoTypeInformation -Encoding UTF8 $csvPath
$all | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $jsonPath

# 画面サマリ
$sum = $all | Group-Object exchange | ForEach-Object {
  $ex = $_.Name
  $okN = ($_.Group | Where-Object { $_.ok }).Count
  $ngN = ($_.Group | Where-Object { -not $_.ok }).Count
  [pscustomobject]@{ exchange=$ex; ok=$okN; ng=$ngN }
}
$sum | Format-Table -AutoSize

"`nCSV:  $csvPath"
"JSON: $jsonPath"
