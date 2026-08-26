@echo off
setlocal enabledelayedexpansion
for %%w in (alpha beta alpha gamma beta alpha) do (
    if not defined uniq_%%w (
        set uniq_%%w=1
        echo unique so far: %%w
    )
)
