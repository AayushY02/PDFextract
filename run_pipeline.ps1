$ErrorActionPreference = "Stop"

function Run-Command {
    param(
        [string]$Label,
        [string]$Exe,
        [string[]]$Args
    )
    Write-Host "==> $Label"
    & $Exe @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Label (exit $LASTEXITCODE)"
    }
}

# 1) Extract
Run-Command "text_extractor" "python" @("text_extractor.py")
Run-Command "hybrid_extraction" "python" @("hybrid_extraction.py")

# 2) Clean (output1 -> output2, test -> test2)
Run-Command "text_cleaner output1->output2" "python" @("text_cleaner.py", "--input-dir", "results/output1", "--output-dir", "results/output2")
Run-Command "text_cleaner test->test2" "python" @("text_cleaner.py", "--input-dir", "results/test", "--output-dir", "results/test2")

# 3) Post-clean (output2 -> output3, test2 -> test3)
Run-Command "post_clean output2->output3" "python" @("post_clean_output3.py", "--input-dir", "results/output2", "--output-dir", "results/output3")
Run-Command "post_clean test2->test3" "python" @("post_clean_output3.py", "--input-dir", "results/test2", "--output-dir", "results/test3")

# 4) Merge
Run-Command "merge_86_texts" "python" @("merge_86_texts.py", "--input_dir", "results/test3/縲・6縲題ｿ醍柄", "--output_dir", "results/test4/縲・6縲題ｿ醍柄")
Run-Command "merge_89_texts" "python" @("merge_89_texts.py", "--input_dir", "results/test3/縲・9縲台ｹ晏ｷ・, "--output_dir", "results/test4/縲・9縲台ｹ晏ｷ・)

# 5) DSL per region
Run-Command "DSL 82 譚ｱ蛹・ "python" @("dsl_engine.py", "--script", "82_script.dsl", "--input_dir", "results/output3/縲・2縲第擲蛹・, "--outdir", "results/csv/縲・2縲第擲蛹・)
Run-Command "DSL 83 髢｢譚ｱ" "python" @("dsl_engine.py", "--script", "83_script.dsl", "--input_dir", "results/output3/縲・3縲鷹未譚ｱ", "--outdir", "results/csv/縲・3縲鷹未譚ｱ")
Run-Command "DSL 84 蛹鈴匣" "python" @("dsl_engine.py", "--script", "84_script.dsl", "--input_dir", "results/output3/縲・4縲大圏髯ｸ", "--outdir", "results/csv/縲・4縲大圏髯ｸ")
Run-Command "DSL 85 荳ｭ驛ｨ" "python" @("dsl_engine.py", "--script", "85_script.dsl", "--input_dir", "results/output3/縲・5縲台ｸｭ驛ｨ", "--outdir", "results/csv/縲・5縲台ｸｭ驛ｨ")
Run-Command "DSL 86 霑醍柄" "python" @("dsl_engine.py", "--script", "86_script.dsl", "--input_dir", "results/test4/縲・6縲題ｿ醍柄", "--outdir", "results/csv/縲・6縲題ｿ醍柄")
Run-Command "DSL 87 荳ｭ蝗ｽ" "python" @("dsl_engine.py", "--script", "87_script.dsl", "--input_dir", "results/output3/縲・7縲台ｸｭ蝗ｽ", "--outdir", "results/csv/縲・7縲台ｸｭ蝗ｽ")
Run-Command "DSL 88 蝗帛嵜" "python" @("dsl_engine.py", "--script", "88_script.dsl", "--input_dir", "results/output3/縲・8縲大屁蝗ｽ", "--outdir", "results/csv/縲・8縲大屁蝗ｽ")
Run-Command "DSL 89 荵晏ｷ・ "python" @("dsl_engine.py", "--script", "89_script.dsl", "--input_dir", "results/test4/縲・9縲台ｹ晏ｷ・, "--outdir", "results/csv/縲・9縲台ｹ晏ｷ・)
Run-Command "DSL 90 豐也ｸ・ "python" @("dsl_engine.py", "--script", "90_script.dsl", "--input_dir", "results/output3/縲・0縲第ｲ也ｸ・, "--outdir", "results/csv/縲・0縲第ｲ也ｸ・)

Run-Command "DSL 810" "python" @("dsl_engine.py", "--script", "810_script.dsl", "--input_dir", "results/test3/縲・10縲・, "--outdir", "results/csv/縲・10縲・)
Run-Command "DSL 811" "python" @("dsl_engine.py", "--script", "811_script.dsl", "--input_dir", "results/test3/縲・11縲・, "--outdir", "results/csv/縲・11縲・)
Run-Command "DSL 812" "python" @("dsl_engine.py", "--script", "812_script.dsl", "--input_dir", "results/test3/縲・12縲・, "--outdir", "results/csv/縲・12縲・)
Run-Command "DSL 813" "python" @("dsl_engine.py", "--script", "813_script.dsl", "--input_dir", "results/test3/縲・13縲・, "--outdir", "results/csv/縲・13縲・)
Run-Command "DSL 814" "python" @("dsl_engine.py", "--script", "814_script.dsl", "--input_dir", "results/test3/縲・14縲・, "--outdir", "results/csv/縲・14縲・)
Run-Command "DSL 815" "python" @("dsl_engine.py", "--script", "815_script.dsl", "--input_dir", "results/test3/縲・15縲・, "--outdir", "results/csv/縲・15縲・)
Run-Command "DSL 816" "python" @("dsl_engine.py", "--script", "816_script.dsl", "--input_dir", "results/test3/縲・16縲・, "--outdir", "results/csv/縲・16縲・)
Run-Command "DSL 817" "python" @("dsl_engine.py", "--script", "817_script.dsl", "--input_dir", "results/test3/縲・17縲・, "--outdir", "results/csv/縲・17縲・)
Run-Command "DSL 819" "python" @("dsl_engine.py", "--script", "819_script.dsl", "--input_dir", "results/test3/縲・19縲・, "--outdir", "results/csv/縲・19縲・)

Write-Host "All pipeline steps completed."
