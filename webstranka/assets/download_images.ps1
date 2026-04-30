param(
    [string]$Url = "https://www.softprojekt.sk/web/",
    [string]$OutDir = ".\assets\downloaded"
)

if(-not (Test-Path $OutDir)){
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

Write-Host "Fetching HTML from $Url"
try{
    $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -ErrorAction Stop
}catch{
    Write-Error "Failed to fetch $Url : $_"
    exit 1
}

$html = $resp.Content

# find src="..." and src='...' occurrences
$imgPattern = @'
(?<=src=["\'])([^"\']+)
'@
$cssPattern = @'
(?<=url\(["\']?)([^"\')]+)
'@

$imgMatches = [regex]::Matches($html,$imgPattern) | ForEach-Object { $_.Groups[1].Value }
# find CSS url(...) patterns
$cssMatches = [regex]::Matches($html,$cssPattern) | ForEach-Object { $_.Groups[1].Value }

$candidates = ($imgMatches + $cssMatches) | Where-Object { $_ -match '\.(jpg|jpeg|png|gif|svg)$' -or $_ -match '\.webp$' } | Select-Object -Unique

function Resolve-Url($base, $link){
    if($link -match '^https?://') { return $link }
    if($link -match '^//') { return 'https:' + $link }
    return ([System.Uri]::new([System.Uri]::new($base), $link)).AbsoluteUri
}

$downloaded = @()
foreach($link in $candidates){
    $abs = Resolve-Url $Url $link
    try{
        $uri = [System.Uri]::new($abs)
        $fileName = [System.IO.Path]::GetFileName($uri.LocalPath)
        if([string]::IsNullOrWhiteSpace($fileName)) { $fileName = [guid]::NewGuid().ToString() + '.img' }
        $outPath = Join-Path $OutDir $fileName
        if(-not (Test-Path $outPath)){
            Write-Host "Downloading $abs -> $outPath"
            Invoke-WebRequest -Uri $abs -OutFile $outPath -UseBasicParsing -ErrorAction Stop
            Write-Host "SAVED: $outPath"
            $downloaded += $outPath
        } else {
            Write-Host "SKIP (exists): $outPath"
            $downloaded += $outPath
        }
    }catch{
        Write-Warning "Failed to download $abs : $_"
    }
}

if($downloaded.Count -eq 0){
    Write-Host "No images found or downloaded."
} else {
    Write-Host "Downloaded files:"
    $downloaded | ForEach-Object { Write-Host $_ }
}
