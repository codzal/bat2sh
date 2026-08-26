@echo off
setlocal enabledelayedexpansion
set A1=x A2=y
set B2=y B3=z
for %%k in (A1 A2 B2 B3) do (
    if defined %%k (echo common-or-first: %%k) else echo missing: %%k
)
