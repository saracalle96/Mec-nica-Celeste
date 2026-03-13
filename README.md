# Mec-nica-Celeste
Notebooks y programas del curso de mecánica celeste

## Validacion de notebooks antes de commit
Para activar el hook versionado en cualquier clon del repositorio, ejecuta:

```powershell
git config core.hooksPath .githooks
```

Luego, antes de cada commit, Git validara que los archivos `.ipynb` no esten vacios y tengan la estructura basica de un notebook Jupyter.
