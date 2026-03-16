$ErrorActionPreference = "Stop"

if ($PSScriptRoot) {
    Set-Location -LiteralPath $PSScriptRoot
}

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

Write-Host "Running region DSL scripts only (no extract/clean/post-clean steps)."

# DSL per region (82-90 and 810-819)
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

# Merge all region summaries after DSL extraction
Run-Command "merge_region_summaries" "python" @("merge_region_summaries.py")

Write-Host "Region-only DSL pipeline completed."
