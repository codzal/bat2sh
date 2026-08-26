# examples/ - converter test cases

Each subfolder covers one theme:

* `basics/` variables, echo, arguments, substrings
* `control_flow/` if/else, loops, goto, subroutines
* `file_operations/` file ops, spaces in names, redirections
* `advanced/` builds, user interaction, Windows paths, INI parser
* `complextasks/` 40 real-world style complex scripts (stress cases)

## Run

```bash
bash generate_examples.sh      # convert everything (creates *.sh)
bash remove_generated.sh       # remove generated *.sh
```

Warning: these samples **execute real commands** (create/delete files in the
current directory). Run them in a sandbox or a dedicated folder.
Generated `*.sh` files are build products and stay out of git - except the
two helper scripts above.
