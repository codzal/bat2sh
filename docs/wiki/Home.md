# bat2sh wiki

Translates Windows batch (`.bat`/`.cmd`) into bash, or into PowerShell 7
with `--target=ps1`.

**For users**

* [[Installation]]
* [[Quick Start]]
* [[CLI Reference]] - every flag with examples
* [[Supported Constructs]] - what converts into what
* [[Audit and Reports]] - `--analyze`, `--report`
* [[GUI]]
* [[Limitations]]

**For developers**

* [[Architecture]]
* [[Runtime Layer and Helpers]]
* [[PowerShell Target beta]]
* [[Language Packs]]
* [[Tests and CI]]

**Meta**

* [Contributing](https://github.com/codzal/bat2sh/blob/dev/CONTRIBUTING.md)
* [Changelog](https://github.com/codzal/bat2sh/blob/dev/CHANGELOG.md)


> Status: **beta (v0.4)**. The ps1 target parses clean on all 62 bundled
> examples; still, verify your scripts with `-c` / `--analyze` first.

> Note: this wiki is maintained in **English only**. The desktop GUI ships
> additional UI languages that may be incomplete.
