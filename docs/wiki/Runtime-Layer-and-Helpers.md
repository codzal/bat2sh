# Runtime Layer and Helpers

`--runtime-layer` inserts after the shebang:

```bash
check_errorlevel() { echo "$ERRORLEVEL"; }
mkdir -p "/tmp/bat2sh_drives/<x>" && ln -sfn "<root>" "/tmp/bat2sh_drives/<x>/."
```

* drive letters are harvested from the source (`X:\`);
* symlink targets follow the current `--path-style`;
* `--strict-bash` adds `set -euo pipefail` - note that intentionally failing
  commands will stop such scripts;
* `ERRORLEVEL=$?` after every statement is the deliberate cmd.exe model.
