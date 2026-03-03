$ErrorActionPreference = "Stop"

function Run-Command {
    param(
        [string]$Label,
        [string]$Exe,
        [string[]]$CommandArgs
    )
    Write-Host "==> $Label"
    & $Exe @CommandArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Label (exit $LASTEXITCODE)"
    }
}

function Get-RegionPrefix {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Code
    )
    return ([string]([char]0x3010) + $Code + [char]0x3011)
}

function Find-RegionDir {
    param(
        [string]$BaseDir,
        [string]$Prefix,
        [switch]$Required
    )

    if (-not (Test-Path -LiteralPath $BaseDir)) {
        if ($Required) {
            throw "Base directory not found: $BaseDir"
        }
        return $null
    }

    $match = Get-ChildItem -LiteralPath $BaseDir -Directory |
        Where-Object { $_.Name -like "$Prefix*" } |
        Sort-Object Name |
        Select-Object -First 1

    if (-not $match -and $Required) {
        throw "Region folder not found in $BaseDir for prefix: $Prefix"
    }

    return $match
}

function Run-Dsl {
    param(
        [string]$Script,
        [string]$InputBase,
        [string]$Prefix,
        [string]$CsvBase = "results/csv",
        [switch]$RequiredInput
    )

    if (-not (Test-Path -LiteralPath $Script)) {
        throw "Missing DSL script: $Script"
    }

    $inputDirObj = Find-RegionDir -BaseDir $InputBase -Prefix $Prefix -Required:$RequiredInput
    if (-not $inputDirObj) {
        Write-Host "Skipping $Script (no matching input under $InputBase for $Prefix)"
        return
    }

    if (-not (Test-Path -LiteralPath $CsvBase)) {
        New-Item -ItemType Directory -Path $CsvBase -Force | Out-Null
    }

    $outDir = Join-Path $CsvBase $inputDirObj.Name
    Run-Command "DSL $Prefix" "python" @(
        "dsl_engine.py",
        "--script", $Script,
        "--input_dir", $inputDirObj.FullName,
        "--outdir", $outDir
    )
}

# 1) Extract
Run-Command "text_extractor" "python" @("text_extractor.py")
Run-Command "hybrid_extraction" "python" @("hybrid_extraction.py")

# 2) Clean (output1 -> output2, test1 -> test2)
Run-Command "text_cleaner output1->output2" "python" @(
    "text_cleaner.py",
    "--input-dir", "results/output1",
    "--output-dir", "results/output2"
)
Run-Command "text_cleaner test1->test2" "python" @(
    "text_cleaner.py",
    "--input-dir", "results/test1",
    "--output-dir", "results/test2"
)

# 3) Post-clean (output2 -> output3, test2 -> test3)
Run-Command "post_clean output2->output3" "python" @(
    "post_clean_output3.py",
    "--input-dir", "results/output2",
    "--output-dir", "results/output3"
)
Run-Command "post_clean test2->test3" "python" @(
    "post_clean_output3.py",
    "--input-dir", "results/test2",
    "--output-dir", "results/test3"
)

# 4) Merge region-specific text sets
$test3Base = "results/test3"
$test4Base = "results/test4"
if (-not (Test-Path -LiteralPath $test4Base)) {
    New-Item -ItemType Directory -Path $test4Base -Force | Out-Null
}

$prefix86 = Get-RegionPrefix "86"
$region86 = Find-RegionDir -BaseDir $test3Base -Prefix $prefix86
if ($region86) {
    $out86 = Join-Path $test4Base $region86.Name
    Run-Command "merge_86_texts" "python" @(
        "merge_86_texts.py",
        "--input_dir", $region86.FullName,
        "--output_dir", $out86
    )
} else {
    Write-Host "Skipping merge_86_texts (no $prefix86 folder in $test3Base)"
}

$prefix89 = Get-RegionPrefix "89"
$region89 = Find-RegionDir -BaseDir $test3Base -Prefix $prefix89
if ($region89) {
    $out89 = Join-Path $test4Base $region89.Name
    Run-Command "merge_89_texts" "python" @(
        "merge_89_texts.py",
        "--input_dir", $region89.FullName,
        "--output_dir", $out89
    )
} else {
    Write-Host "Skipping merge_89_texts (no $prefix89 folder in $test3Base)"
}

# 5) DSL per region (82-90 and 810-819)
Run-Dsl -Script "82_script.dsl" -InputBase "results/output3" -Prefix (Get-RegionPrefix "82") -RequiredInput
Run-Dsl -Script "83_script.dsl" -InputBase "results/output3" -Prefix (Get-RegionPrefix "83") -RequiredInput
Run-Dsl -Script "84_script.dsl" -InputBase "results/output3" -Prefix (Get-RegionPrefix "84") -RequiredInput
Run-Dsl -Script "85_script.dsl" -InputBase "results/test3" -Prefix (Get-RegionPrefix "85") -RequiredInput
Run-Dsl -Script "86_script.dsl" -InputBase "results/test4" -Prefix (Get-RegionPrefix "86") -RequiredInput
Run-Dsl -Script "87_script.dsl" -InputBase "results/output3" -Prefix (Get-RegionPrefix "87") -RequiredInput
Run-Dsl -Script "88_script.dsl" -InputBase "results/output3" -Prefix (Get-RegionPrefix "88") -RequiredInput
Run-Dsl -Script "89_script.dsl" -InputBase "results/test4" -Prefix (Get-RegionPrefix "89") -RequiredInput
Run-Dsl -Script "90_script.dsl" -InputBase "results/output3" -Prefix (Get-RegionPrefix "90") -RequiredInput

Run-Dsl -Script "810_script.dsl" -InputBase "results/test3" -Prefix (Get-RegionPrefix "810") -RequiredInput
Run-Dsl -Script "811_script.dsl" -InputBase "results/test3" -Prefix (Get-RegionPrefix "811") -RequiredInput
Run-Dsl -Script "812_script.dsl" -InputBase "results/test3" -Prefix (Get-RegionPrefix "812") -RequiredInput
Run-Dsl -Script "813_script.dsl" -InputBase "results/test3" -Prefix (Get-RegionPrefix "813") -RequiredInput
Run-Dsl -Script "814_script.dsl" -InputBase "results/test3" -Prefix (Get-RegionPrefix "814") -RequiredInput
Run-Dsl -Script "815_script.dsl" -InputBase "results/test3" -Prefix (Get-RegionPrefix "815") -RequiredInput
Run-Dsl -Script "816_script.dsl" -InputBase "results/test3" -Prefix (Get-RegionPrefix "816") -RequiredInput
Run-Dsl -Script "817_script.dsl" -InputBase "results/test3" -Prefix (Get-RegionPrefix "817") -RequiredInput
Run-Dsl -Script "818_script.dsl" -InputBase "results/test3" -Prefix (Get-RegionPrefix "818") -RequiredInput
Run-Dsl -Script "819_script.dsl" -InputBase "results/test3" -Prefix (Get-RegionPrefix "819") -RequiredInput

Write-Host "All pipeline steps completed."
