# 📚 Guía de estudio y defensa — A-Maze-ing

> Documento completo de repaso para entender el proyecto a fondo y
> preparar la defensa. Léelo de principio a fin antes de la peer-eval.

---

## Índice

1. [Resumen del proyecto en 30 segundos](#1-resumen-del-proyecto-en-30-segundos)
2. [Requisitos del subject (checklist)](#2-requisitos-del-subject-checklist)
3. [Arquitectura del proyecto](#3-arquitectura-del-proyecto)
4. [Conceptos de Python que debes dominar](#4-conceptos-de-python-que-debes-dominar)
5. [Bitmask: la representación de las paredes](#5-bitmask-la-representación-de-las-paredes)
6. [Algoritmos de generación: el que usamos y alternativas](#6-algoritmos-de-generación-el-que-usamos-y-alternativas)
7. [Algoritmos de búsqueda de camino](#7-algoritmos-de-búsqueda-de-camino)
8. [El patrón "42": diseño y técnica](#8-el-patrón-42-diseño-y-técnica)
9. [Modo no-perfecto y restricción 3×3](#9-modo-no-perfecto-y-restricción-3x3)
10. [Empaquetado con pip moderno](#10-empaquetado-con-pip-moderno)
11. [Walkthrough archivo por archivo](#11-walkthrough-archivo-por-archivo)
12. [Comandos y workflows](#12-comandos-y-workflows)
13. [Preguntas frecuentes en defensa](#13-preguntas-frecuentes-en-defensa)
14. [Modificaciones rápidas (lo que pueden pedir en defensa)](#14-modificaciones-rápidas-lo-que-pueden-pedir-en-defensa)
15. [Edge cases y validaciones](#15-edge-cases-y-validaciones)
16. [Glosario rápido](#16-glosario-rápido)

---

## 1. Resumen del proyecto en 30 segundos

**A-Maze-ing** es un generador de laberintos en Python que:

- **Lee** un archivo de configuración con formato `KEY=VALUE`.
- **Genera** un laberinto aleatorio (con semilla reproducible).
- **Inserta** un patrón visible "42" hecho de celdas cerradas.
- **Resuelve** el camino más corto entre entrada y salida con BFS.
- **Escribe** el laberinto en formato hexadecimal compacto.
- **Muestra** el laberinto en terminal con colores ANSI.
- **Permite** interacción: regenerar, mostrar/ocultar camino, cambiar colores.
- **Empaqueta** la lógica de generación como un módulo `mazegen` instalable con pip.

**Stack:** Python 3.10+, `typing`, `dataclasses`, `random`, `collections.deque`,
`pathlib`, `setuptools`, `pyproject.toml`. Cero dependencias externas en
runtime.

---

## 2. Requisitos del subject (checklist)

Cada vez que defiendas algo, ten esto en mente:

### Reglas generales (III.1)
- [x] Python **3.10 o superior**.
- [x] **flake8** sin errores.
- [x] **Try/except** en todas las operaciones que puedan fallar.
- [x] **Context managers** (`with`) para archivos.
- [x] **Type hints** en todas las funciones.
- [x] **mypy** sin errores con los flags del subject.
- [x] **Docstrings** estilo Google (PEP 257).

### Makefile (III.2)
- [x] `install`, `run`, `debug`, `clean`, `lint`, `lint-strict`.

### Parte obligatoria (IV)
- [x] Programa lanzado con `python3 a_maze_ing.py config.txt`.
- [x] Archivo de configuración con WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT (+ SEED opcional).
- [x] Comentarios con `#` y líneas vacías ignoradas.
- [x] Laberinto aleatorio pero reproducible (con semilla).
- [x] Coherencia: cada pared compartida entre dos celdas tiene el mismo estado.
- [x] Bordes externos siempre cerrados.
- [x] Conectividad total (excepto patrón "42").
- [x] Sin áreas abiertas mayores que 2×3 o 3×2 (es decir, ningún 3×3 abierto).
- [x] Patrón "42" visible con celdas cerradas.
- [x] Modo PERFECT=True con camino único entry→exit.
- [x] Mensaje de error si el laberinto es demasiado pequeño para el "42".
- [x] Salida en hex (bit 0=N, 1=E, 2=S, 3=W; 1=cerrada, 0=abierta).
- [x] Línea vacía + entry + exit + path (en N/E/S/W).
- [x] Todas las líneas terminan en `\n`.

### Visualización (V)
- [x] Render en terminal con ANSI.
- [x] Paredes, entrada, salida y ruta solución claramente visibles.
- [x] Interacciones: regenerar, mostrar/ocultar path, cambiar colores.

### Reusabilidad (VI)
- [x] Clase `MazeGenerator` en módulo standalone (`mazegen`).
- [x] Instalable con pip (`mazegen-1.0.0-py3-none-any.whl` en la raíz).
- [x] Documentación del módulo (`mazegen_pkg/README.md`).

### README (VII)
- [ ] Primera línea en cursiva con logins del equipo (**falta rellenar**).
- [x] Descripción.
- [x] Instrucciones.
- [x] Estructura del config.
- [x] Algoritmo elegido + justificación.
- [x] Qué es reusable y cómo.
- [ ] Roles del equipo, planning, retrospectiva, herramientas (**falta rellenar**).
- [ ] Sección "AI usage" (**falta rellenar**).

---

## 3. Arquitectura del proyecto

```
A-mazing/
├── a_maze_ing.py              ← punto de entrada (pegamento)
├── config.txt                 ← config por defecto
├── Makefile                   ← install/run/lint/clean/package
├── README.md                  ← documentación de cara al evaluador
├── .gitignore
│
├── src/                       ← lógica de la APLICACIÓN (no reusable)
│   ├── config_parser.py       ← parseo y validación del config
│   ├── output_writer.py       ← escritor del archivo hex
│   ├── display.py             ← render ANSI en terminal
│   └── menu.py                ← loop interactivo
│
├── mazegen_pkg/               ← módulo REUSABLE (se empaqueta para pip)
│   ├── pyproject.toml         ← metadata del paquete
│   ├── README.md
│   └── src/mazegen/
│       ├── __init__.py        ← expone API pública
│       ├── cell.py            ← Cell + Direction + helpers
│       ├── generator.py       ← MazeGenerator (DFS iterativo)
│       ├── solver.py          ← BFS shortest_path
│       └── pattern_42.py      ← bitmap del "42"
│
├── tests/                     ← 23 tests pytest
│   ├── test_cell.py
│   ├── test_config_parser.py
│   └── test_solver.py
│
└── mazegen-1.0.0-py3-none-any.whl   ← el paquete construido (exigido en raíz)
```

### Por qué separamos `src/` de `mazegen_pkg/`

- `mazegen_pkg/` es el **núcleo reusable**: genera y resuelve laberintos.
  Una persona puede instalarlo con `pip install mazegen` y usarlo en
  cualquier proyecto. **No sabe nada** de archivos de configuración,
  terminal, ni I/O.
- `src/` es la **aplicación A-Maze-ing**: pega `mazegen` con el archivo
  de configuración, el output hex, el render ANSI y el menú interactivo.

Esta separación es **el corazón del capítulo VI del subject** (Code
reusability). Si te preguntan "¿qué es reusable?", la respuesta es: todo
lo que está en `mazegen_pkg/`.

---

## 4. Conceptos de Python que debes dominar

### 4.1 `@dataclass` (PEP 557)

Genera automáticamente `__init__`, `__repr__`, `__eq__` para clases que
solo contienen datos.

```python
@dataclass(frozen=True)
class Config:
    width: int
    height: int
```

- `frozen=True` → **inmutable**: una vez creado, no se modifica.
  Da seguridad: ningún módulo posterior puede romper el estado.

**Pregunta típica:** *"¿Por qué `frozen=True`?"*
→ Para evitar mutación accidental del config a lo largo del programa.
Hace el flujo de datos más fácil de razonar.

### 4.2 Type hints + `from __future__ import annotations`

```python
from __future__ import annotations

def parse_config(path: str | Path) -> Config:
    ...
```

- `from __future__ import annotations` evalúa las anotaciones como **strings**
  (PEP 563). Permite sintaxis moderna (`int | None`, `list[int]`) incluso
  en versiones donde antes había que escribir `Optional[int]`, `List[int]`.
- mypy las verifica estáticamente.

### 4.3 Context managers (`with`)

```python
with open(path, "r", encoding="utf-8") as fp:
    lines = fp.readlines()
```

- Garantiza que el archivo se **cierra** incluso si hay excepción.
- **Nunca** uses `open()` sin `with` en código de producción.
- Internamente usa el protocolo `__enter__` / `__exit__`.

### 4.4 Excepciones personalizadas con encadenamiento

```python
raise ConfigError(f"file not found: {path}") from exc
```

- Crea jerarquía de errores (`ConfigError`, `OutputError`,
  `PathNotFoundError`) para que el `main()` capture lo correcto.
- `from exc` preserva la causa original en `__cause__` para debug, pero
  el usuario solo ve el mensaje limpio.

### 4.5 `IntFlag` para los bitmask

```python
class Direction(IntFlag):
    N = 1 << 0  # 1
    E = 1 << 1  # 2
    S = 1 << 2  # 4
    W = 1 << 3  # 8
```

- `IntFlag` es un `Enum` que se comporta como entero y soporta
  `|`, `&`, `~` directamente.
- Hace el código auto-documentado: `cell.has_wall(Direction.N)` se lee
  solo, vs `cell.walls & 1`.

### 4.6 `collections.deque` para BFS

```python
from collections import deque
queue = deque([start])
queue.popleft()   # O(1) — list.pop(0) sería O(n)
```

- `deque` (double-ended queue) es la cola ideal para BFS.
- `popleft()` es O(1); `list.pop(0)` es O(n).

### 4.7 Generador (`yield`) para iterar celdas

```python
def iter_cells(self) -> Iterator[tuple[int, int, Cell]]:
    for y, row in enumerate(self.grid):
        for x, cell in enumerate(row):
            yield x, y, cell
```

- No construye una lista; usa **menos memoria** y produce los items
  on-demand.
- Iterables más limpios para clientes externos.

### 4.8 `random.Random(seed)`

```python
self._rng = random.Random(seed)
self._rng.choice(neighbours)
```

- Crea una instancia de RNG **propia**, no toca el RNG global.
- Importante: si dos partes del programa comparten `random`, una rompe
  la reproducibilidad de la otra.

---

## 5. Bitmask: la representación de las paredes

### La idea
Cada celda tiene 4 paredes. Las codificamos en 4 bits:

```
   bit 3   bit 2   bit 1   bit 0
   ┌────┬────┬────┬────┐
   │ W  │ S  │ E  │ N  │
   └────┴────┴────┴────┘
```

| Valor hex | Binario | N | E | S | W |
|---|---|---|---|---|---|
| `0x0` | `0000` | ⬜ | ⬜ | ⬜ | ⬜ |
| `0x3` | `0011` | ⬛ | ⬛ | ⬜ | ⬜ |
| `0xA` | `1010` | ⬜ | ⬛ | ⬜ | ⬛ |
| `0xF` | `1111` | ⬛ | ⬛ | ⬛ | ⬛ |

(⬛ = pared cerrada, ⬜ = pared abierta)

### Operaciones bit a bit

```python
# Comprobar si pared N está cerrada
cell.walls & Direction.N        # AND con la máscara → != 0 si está

# Derribar pared N
cell.walls &= ~Direction.N       # AND con NOT máscara → pone bit a 0

# Levantar pared N
cell.walls |= Direction.N        # OR con la máscara → pone bit a 1
```

### Por qué es elegante

El subject pide guardar el laberinto como **un dígito hex por celda**
con exactamente este formato. Como nuestra representación interna ya es
ese mismo bitmask, **no hay conversión**: `format(cell.walls, "X")` es
todo lo que necesitamos para escribir el archivo de salida.

**Pregunta típica:** *"¿Por qué no usar 4 booleanos por pared?"*
→ Porque el output exige el bitmask. Tener una representación interna
distinta requeriría una conversión que es código extra sin valor.

---

## 6. Algoritmos de generación: el que usamos y alternativas

### 6.1 El que usamos: Recursive Backtracker (DFS aleatorizado)

**Idea:** un DFS donde, en cada paso, eliges un vecino no visitado al
azar y derribas la pared entre ambas celdas.

```
stack = [celda_inicial]
visited = {celda_inicial}
while stack:
    actual = stack[-1]                # peek
    vecinos = vecinos_no_visitados(actual)
    if vecinos:
        siguiente = random.choice(vecinos)
        derribar_pared(actual, siguiente)
        visited.add(siguiente)
        stack.append(siguiente)
    else:
        stack.pop()                   # backtrack
```

**Pros:**
- Produce laberintos **perfectos** (spanning tree) por construcción.
- Corredores largos y serpenteantes → "estética de laberinto clásico".
- Fácil de explicar.

**Contras:**
- En recursión naive rompe `sys.setrecursionlimit()` → **siempre iterativo**.
- Tendencia a corredores largos: no produce muchos cul-de-sacs cortos.

**Complejidad:** O(N) donde N = WIDTH × HEIGHT.

---

### 6.2 Alternativa: Prim's algorithm (versión randomizada)

**Idea:** crece el árbol añadiendo en cada paso un **borde aleatorio**
de la frontera.

```
visited = {celda_inicial}
frontier = lista_de_paredes_de_celda_inicial
while frontier:
    pared = random.choice(frontier)     # NO el primero — al azar
    a, b = celdas_separadas_por(pared)
    if (a in visited) XOR (b in visited):
        derribar(pared)
        nuevo = el que no estaba en visited
        visited.add(nuevo)
        añadir_a_frontier(paredes_de(nuevo))
    quitar_de_frontier(pared)
```

**Pros:**
- Produce laberintos con **bifurcaciones cortas** (más cul-de-sacs).
- Más uniformes visualmente que DFS.
- Es **el mismo Prim** de la teoría de grafos, adaptado a grids.

**Contras:**
- Estructura de datos más compleja (lista de fronteras).
- Si se usa una `set` para `frontier`, el `random.choice` no funciona
  directamente — hay que convertir a `list` (más lento).

**Complejidad:** O(N log N) o O(N²) según la estructura usada.

---

### 6.3 Alternativa: Kruskal's algorithm

**Idea:** todas las paredes en una lista barajada. Para cada una, si
las dos celdas que separa están en **componentes distintos** (según
**Union-Find**), derriba la pared y une los componentes.

```
walls = todas_las_paredes_interiores
random.shuffle(walls)
uf = UnionFind(width * height)
for pared in walls:
    a, b = celdas_separadas_por(pared)
    if uf.find(a) != uf.find(b):
        derribar(pared)
        uf.union(a, b)
```

**Pros:**
- Hermosamente uniforme — distribución muy homogénea de cul-de-sacs.
- Te permite aprender **Union-Find (DSU)**, estructura clásica.

**Contras:**
- Requiere implementar Union-Find (path compression + rank).
- Más memoria que DFS o Prim (lista de N paredes).

**Complejidad:** O(N α(N)) ≈ O(N) gracias a path compression de DSU.

---

### 6.4 Alternativa: Wilson's algorithm

**Idea:** mediante **random walks con loop erasure** se generan árboles
de expansión uniformemente distribuidos (cada laberinto perfecto tiene
exactamente la misma probabilidad).

**Pros:**
- Distribución verdaderamente uniforme — el más "matemáticamente
  correcto".

**Contras:**
- Lento (random walks pueden tardar mucho en algunas configuraciones).
- Complejo de implementar.

---

### 6.5 Alternativa: Aldous-Broder algorithm

**Idea:** parte de una celda, camina aleatoriamente; cada vez que entra
en una celda no visitada por primera vez, derriba la pared usada para
entrar.

**Pros:**
- Trivialmente correcto.
- Genera todos los laberintos posibles con igual probabilidad.

**Contras:**
- **Extremadamente lento** (camina muchas veces por celdas ya visitadas).
- Pésima primera impresión en defensa: nadie quiere ver "es lento pero
  bonito".

---

### 6.6 Comparativa rápida

| Algoritmo | Estética | Velocidad | Complejidad de implementar | Defensa |
|---|---|---|---|---|
| **DFS / Recursive Backtracker** | Corredores largos | Muy rápida | Fácil | ★★★ |
| Prim | Cul-de-sacs cortos | Rápida | Media | ★★ |
| Kruskal | Muy uniforme | Rápida | Media-alta (Union-Find) | ★★ |
| Wilson | Distribución uniforme | Variable | Alta | ★ |
| Aldous-Broder | Distribución uniforme | Muy lenta | Baja | ✗ |

**Pregunta típica:** *"¿Por qué DFS y no X?"*
→ "Buscaba un algoritmo que produjera laberintos perfectos de forma
**directa** (sin estructura auxiliar como Union-Find o frontera), fuera
**fácil de razonar** para defenderlo línea por línea, y resultara
**eficiente** para los tamaños del subject. DFS iterativo cumple los
tres."

---

## 7. Algoritmos de búsqueda de camino

### 7.1 El que usamos: BFS (Breadth-First Search)

**Idea:** explora por **niveles**: primero todos los vecinos directos,
luego sus vecinos, etc. La primera vez que toca el destino, lo hace
por el camino más corto.

```python
queue = deque([start])
parent = {start: start}
while queue:
    cell = queue.popleft()
    if cell == end:
        return reconstruir(parent, end)
    for vecino in alcanzables(cell):
        if vecino not in parent:
            parent[vecino] = cell
            queue.append(vecino)
```

**Por qué BFS y no DFS para resolver:** En un grafo **no ponderado**
(cada paso cuesta 1), BFS garantiza la **ruta óptima**. DFS puede
encontrar **un** camino pero no necesariamente el más corto.

**Complejidad:** O(V + E) — visita cada celda y cada pared abierta una
vez.

### 7.2 Alternativa: Dijkstra

Generalización de BFS a grafos **ponderados**. Si todas las aristas
cuestan 1, Dijkstra **degenera a BFS** (con O(log N) extra por la
priority queue → más lento). No tiene sentido aquí.

### 7.3 Alternativa: A*

BFS guiado por una heurística (ej. distancia Manhattan al objetivo).
**Más rápido** en grafos grandes con un objetivo claro. Para laberintos
de 20×15, BFS es más simple y suficientemente rápido — A* sería
**over-engineering**.

**Pregunta típica:** *"¿Por qué no usar A*?"*
→ "El grafo es no ponderado y pequeño; BFS es óptimo y más simple. A*
añadiría una heurística que no aporta valor a esta escala."

---

## 8. El patrón "42": diseño y técnica

### Diseño del bitmap

```
Pattern (9 columnas × 6 filas):

  X..X.XXXX
  X..X....X
  X..X....X
  XXXX...X.
  ...X..X..
  ...X.XXXX

  ←  4 →   ←  2 →
```

- `X` = celda **cerrada** (parte del "42")
- `.` = celda normal (la maze recorre por aquí)

### La técnica: "pre-visitar" las celdas del patrón

```python
def _carve_passages(self, start, blocked):
    visited = set(blocked)   # ← truco: las celdas del patrón ya están "visitadas"
    visited.add(start)
    stack = [start]
    while stack:
        ...
```

- Al sembrar `visited` con las celdas del patrón, el DFS **nunca
  entra** en esas celdas.
- Como nunca son visitadas, **nunca se les derriba ninguna pared**.
- Resultado: bloques cerrados con forma de "42" emergen automáticamente.

**Pregunta típica:** *"¿Cómo garantizas que el resto del laberinto
sigue conectado?"*
→ Tres niveles de garantía:
1. El patrón está **centrado** con margen de ≥2 celdas a cada borde.
2. El DFS visita **todas** las celdas no-patrón a partir de la celda
   inicial.
3. En tests verificamos por BFS que las 276 celdas no-patrón están
   conectadas (en el caso por defecto 20×15).

### Cuando el laberinto es muy pequeño

```python
if not pattern_42.fits(self.width, self.height):
    print("warning: maze is too small to display the '42' pattern",
          file=sys.stderr)
    return set()
```

Subject lo exige: si no cabe, imprimimos error en stderr y continuamos
sin el patrón.

---

## 9. Modo no-perfecto y restricción 3×3

### El problema

`PERFECT=False` → debe haber **ciclos** (más de un camino entry→exit),
PERO **no pueden existir áreas abiertas de 3×3** (corredores ≤ 2 celdas
de ancho).

### Estrategia

1. Genera primero un laberinto **perfecto** (DFS).
2. Toma todas las **paredes interiores** no fronterizas al patrón "42".
3. Baraja la lista.
4. Para cada pared, **tentativamente** la derriba.
5. Si crea un 3×3 abierto en cualquier ventana cercana → restaura.
6. Si no → la deja derribada.
7. Para cuando alcanzas un porcentaje objetivo (15%).

### El check 3×3

```python
def _is_open_3x3(self, ox, oy):
    """Las 12 paredes interiores del bloque 3x3 están todas abiertas?"""
    for j in range(3):
        for i in range(3):
            cell = self.grid[oy + j][ox + i]
            if i < 2 and cell.has_wall(Direction.E):
                return False
            if j < 2 and cell.has_wall(Direction.S):
                return False
    return True
```

Un bloque 3×3 tiene:
- 3×2 = 6 paredes verticales internas (entre columnas)
- 2×3 = 6 paredes horizontales internas (entre filas)
- Total: **12 paredes interiores**. Las 12 deben estar abiertas.

### Por qué solo verificamos ventanas que tocan la pared cambiada

Si una pared no se acaba de derribar, las ventanas 3×3 que NO la
contienen ya las habíamos validado en pasos anteriores. Solo las
**nuevas** ventanas que el cambio podría haber afectado necesitan
chequeo. Esto reduce el coste de O(W·H) por iteración a O(1).

---

## 10. Empaquetado con pip moderno

### El estándar: PEP 517/518/621

- **PEP 518**: define `pyproject.toml` y la sección `[build-system]`.
- **PEP 517**: define **cómo** se construye un paquete (build backends).
- **PEP 621**: define la **metadata** en `[project]`.

### Nuestro `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mazegen"
version = "1.0.0"
description = "Reusable maze generator."
requires-python = ">=3.10"

[tool.setuptools.packages.find]
where = ["src"]
```

- `[build-system]` indica qué hace falta para construir (setuptools).
- `[project]` es el metadata visible en PyPI / pip.
- `[tool.setuptools.packages.find]` con `where=["src"]` activa el
  **layout src/**, recomendado para evitar imports accidentales del cwd.

### Construir y distribuir

```bash
cd mazegen_pkg
python -m build         # produce dist/mazegen-1.0.0.tar.gz + .whl
```

- `.tar.gz` = source distribution (sdist).
- `.whl` = built distribution (binary, listo para instalar).
- El subject pide que el `.whl` esté **en la raíz del repo**.

### Instalación

```bash
pip install mazegen-1.0.0-py3-none-any.whl
# Ahora puedes:
python3 -c "from mazegen import MazeGenerator; print(MazeGenerator(10,10).generate)"
```

**Pregunta típica:** *"¿Qué diferencia hay entre `.tar.gz` y `.whl`?"*
→ "El `.tar.gz` es el código fuente del paquete (sdist); pip compila
los archivos al instalarlo. El `.whl` ya es binario — instalación
mucho más rápida. Nuestro paquete es puro Python, así que ambos
funcionan; el `.whl` es más estándar y más rápido."

---

## 11. Walkthrough archivo por archivo

### 11.1 `a_maze_ing.py` — entry point
- Parsea `sys.argv`, llama `parse_config()`, instancia `MazeGenerator`,
  escribe output, lanza menú.
- Captura `ConfigError`, `OutputError`, `KeyboardInterrupt`.
- **Truco del sys.path:** añade `mazegen_pkg/src` al path para que
  funcione sin instalación previa.

### 11.2 `src/config_parser.py`
- `Config` dataclass (frozen).
- `parse_config()` lee el archivo, valida cada KEY, retorna un `Config`
  fully-typed.
- 8 validaciones distintas (missing key, malformed line, duplicated
  key, non-positive dim, entry==exit, out of bounds, invalid bool,
  file not found).

### 11.3 `mazegen_pkg/src/mazegen/cell.py`
- `Direction` IntFlag (N, E, S, W como 1, 2, 4, 8).
- `Cell` dataclass con `walls: int`.
- Funciones helper: `opposite()`, `delta()`.
- Método `hex_digit()` = `format(walls, "X")`.

### 11.4 `mazegen_pkg/src/mazegen/generator.py`
- `MazeGenerator.__init__()` valida width/height.
- `generate()` orquesta: fresh grid → patrón → DFS → loops opcionales.
- `_carve_passages()` es el DFS iterativo con stack.
- `_add_loops()` derriba paredes random validando 3×3.
- `shortest_path()` wrapper que delega a `solver.shortest_path()`.

### 11.5 `mazegen_pkg/src/mazegen/solver.py`
- `shortest_path(grid, start, end)` BFS con `deque` + `parent` dict.
- `path_to_directions(path)` convierte tuplas a string "NESW".
- `PathNotFoundError` para casos sin solución.

### 11.6 `mazegen_pkg/src/mazegen/pattern_42.py`
- Constante `PATTERN_42` (tuple de strings).
- `fits(w, h)` chequea si cabe con margen.
- `pattern_cells(w, h)` retorna el set de coords del patrón centrado.

### 11.7 `src/output_writer.py`
- `write_maze(path, grid, entry, exit_)`:
  - Renderiza grid en hex.
  - Calcula path (BFS) y lo convierte a directions.
  - Escribe filas + línea vacía + entry + exit + path.
- Context manager para escritura.

### 11.8 `src/display.py`
- `ColorScheme` dataclass con 6 códigos ANSI por esquema.
- 4 esquemas: classic, forest, amber, ocean.
- `render()` construye la rejilla de píxeles (2H+1 × 2W+1) y pinta
  cada uno con ANSI.

### 11.9 `src/menu.py`
- `MenuSession` con estado mutable (show_path, color_index, generator).
- `run()` loop con `input()`, opciones 1-4.
- Limpia pantalla con `\x1b[2J\x1b[H` antes de cada render.

---

## 12. Comandos y workflows

### 12.1 Setup del proyecto

```bash
make install        # crea .venv e instala flake8, mypy, pytest, build
```

### 12.2 Ejecutar

```bash
make run                          # python3 a_maze_ing.py config.txt
python3 a_maze_ing.py config.txt  # equivalente
```

### 12.3 Debug

```bash
make debug          # arranca con pdb activo
```

Dentro de pdb:
- `n` = next line
- `s` = step into
- `c` = continue
- `b file.py:42` = breakpoint
- `p var` = print variable
- `l` = list nearby code

### 12.4 Calidad

```bash
make lint           # flake8 + mypy con flags del subject
make lint-strict    # flake8 + mypy --strict
make test           # pytest
```

### 12.5 Build del paquete

```bash
make package        # genera mazegen-1.0.0-{py3-none-any.whl,.tar.gz}
```

### 12.6 Limpieza

```bash
make clean          # quita __pycache__, .mypy_cache, dist/, etc.
make fclean         # clean + venv + wheels
make re             # fclean + install
```

### 12.7 Comandos útiles para defender

```bash
# Mostrar el output hex generado
cat maze.txt

# Verificar que la coherencia es correcta (manualmente):
python3 -c "
import sys; sys.path.insert(0, 'mazegen_pkg/src')
from mazegen import MazeGenerator, Direction
g = MazeGenerator(20, 15, seed=42); g.generate()
ok = all(
    g.grid[y][x].has_wall(Direction.E) == g.grid[y][x+1].has_wall(Direction.W)
    for y in range(g.height) for x in range(g.width-1)
)
print('coherent walls:', ok)
"

# Ver la estructura del wheel
unzip -l mazegen-1.0.0-py3-none-any.whl

# Instalar el wheel en un venv limpio (te lo pedirán en defensa)
cd /tmp && python3 -m venv test_env
./test_env/bin/pip install /sgoinfre/.../mazegen-1.0.0-py3-none-any.whl
./test_env/bin/python -c "from mazegen import MazeGenerator; print('OK')"
```

---

## 13. Preguntas frecuentes en defensa

### 13.1 Sobre el algoritmo

> **P: ¿Por qué Recursive Backtracker y no Prim/Kruskal?**
> R: Porque (1) produce laberintos perfectos directamente — el subject
> exige PERFECT=True; (2) es el más fácil de explicar línea por línea
> en defensa; (3) tiene complejidad O(N), igual de eficiente; (4) no
> requiere estructuras auxiliares complejas como Union-Find.

> **P: ¿Por qué iterativo y no recursivo?**
> R: Python tiene `sys.setrecursionlimit() ≈ 1000`. Un laberinto de
> 100×100 = 10.000 celdas rompería el stack. Con la versión iterativa
> usando un `list` como pila, el límite lo pone la RAM, no el intérprete.

> **P: ¿BFS o DFS para resolver?**
> R: BFS — garantiza la **ruta más corta** en grafos no ponderados.
> DFS encontraría **un** camino, no necesariamente el óptimo.

> **P: ¿Qué pasa si la entrada y salida son la misma celda?**
> R: El parser lo rechaza al cargar el config (`ENTRY and EXIT must be
> different cells`). Por contrato, el solver nunca recibe ese caso —
> aun así tiene un short-circuit `if start == end: return [start]`.

### 13.2 Sobre la estructura de datos

> **P: ¿Por qué `list[list[Cell]]` y no `numpy.array`?**
> R: numpy sería overkill — el tamaño es pequeño (cientos de celdas),
> los métodos vectorizados no aportan valor, y añade una dependencia.
> Listas nativas son suficientes y eliminan I/O extra.

> **P: ¿Por qué bitmask en lugar de 4 bool?**
> R: Porque el subject pide salida en hex con exactamente ese formato.
> Tener una representación interna distinta requeriría conversión.
> Además, las operaciones bitwise son O(1) y el código es compacto.

> **P: ¿Por qué `grid[y][x]` y no `grid[x][y]`?**
> R: Convención de filas-primero. El bucle exterior recorre `y` (filas),
> el interior `x` (columnas) → coincide con cómo lees el archivo de
> salida (línea = fila = y constante).

### 13.3 Sobre Python

> **P: ¿Qué hace `from __future__ import annotations`?**
> R: PEP 563 — pospone la evaluación de las anotaciones hasta tiempo
> de inspección. Permite usar sintaxis moderna (`int | None`,
> `list[X]`) y elimina el overhead de evaluar tipos en cada llamada.

> **P: ¿Qué es un dataclass `frozen`?**
> R: Una dataclass cuyos atributos no se pueden modificar después de
> creada. Es **inmutable** y por lo tanto **hashable** → se puede usar
> como key de dict o miembro de set.

> **P: ¿Por qué `random.Random(seed)` en lugar de `random.seed(seed)`?**
> R: Para no contaminar el RNG global. Si dos módulos hacen
> `random.seed()` en momentos distintos, se sobrescriben mutuamente.
> Una instancia propia es aislada.

> **P: ¿Qué hace `try/except OSError`?**
> R: Captura cualquier error de sistema operativo: archivo no
> encontrado (`FileNotFoundError` es subclase), permisos
> (`PermissionError`), disco lleno, etc. Es la captura general
> para I/O.

### 13.4 Sobre el patrón "42"

> **P: ¿Cómo aparece el "42" si el DFS conecta todas las celdas?**
> R: Antes de empezar el DFS, marcamos las celdas del patrón como
> **visitadas**. El DFS las saltará (nunca elige una visitada como
> siguiente). Como nunca las visita, nunca les derriba paredes —
> quedan como bloques cerrados.

> **P: ¿Qué pasa si el patrón aísla parte del laberinto?**
> R: No puede pasar con nuestro diseño porque (1) el patrón está
> centrado con margen ≥2 a cada borde, (2) los huecos internos del
> "4" y del "2" están conectados al exterior. Si quisiéramos
> garantizarlo formalmente, haríamos BFS post-generación.

> **P: ¿Por qué el patrón es 9×6 y no más grande?**
> R: Compromiso entre legibilidad y tamaño mínimo de laberinto.
> 9×6 es legible y cabe en mazes desde 13×10 (con margen). Más
> grande requeriría mazes mayores.

### 13.5 Sobre la salida

> **P: ¿Por qué el bit 0 es N y no S?**
> R: Lo define el subject literalmente. Si fuera al revés, los
> dígitos hex no coincidirían con la representación esperada.

> **P: ¿Y si quisiéramos cambiar la convención?**
> R: Solo habría que cambiar los valores de `Direction.N/E/S/W` en
> `cell.py`. Todo lo demás está parametrizado.

### 13.6 Sobre la reusabilidad

> **P: ¿Qué exactamente es reusable y qué no?**
> R: Reusable = todo lo que está en `mazegen_pkg/` (Cell, Direction,
> MazeGenerator, shortest_path, path_to_directions, pattern_42).
> No reusable = parser de config, output writer, display ANSI, menú
> — son específicos de esta aplicación.

> **P: ¿Cómo otro proyecto usaría tu `mazegen`?**
> R:
> ```python
> from mazegen import MazeGenerator
> gen = MazeGenerator(50, 30, seed=123)
> gen.generate()
> for row in gen.grid:
>     for cell in row:
>         ...  # usar cell.walls / cell.has_wall(...)
> ```

### 13.7 Sobre el Makefile

> **P: ¿Por qué `make install` crea un venv?**
> R: Aislamiento de dependencias — flake8 y mypy son herramientas de
> dev que no queremos instalar globalmente. El subject lo recomienda
> en III.3.

> **P: ¿Qué hacen los flags de mypy del subject?**
> R: `--disallow-untyped-defs` exige type hints en todas las funciones.
> `--check-untyped-defs` verifica también las que no tienen tipo.
> `--warn-return-any` avisa si una función retorna `Any` implícitamente.
> `--warn-unused-ignores` quita `# type: ignore` que ya no hacen falta.
> `--ignore-missing-imports` no falla si una librería de terceros no
> tiene stubs.

---

## 14. Modificaciones rápidas (lo que pueden pedir en defensa)

El subject IX dice: "a brief modification of the project may
occasionally be requested". Aquí están las modificaciones probables y
cómo abordarlas:

### 14.1 "Cambia el patrón '42' por '21'"

```python
# mazegen_pkg/src/mazegen/pattern_42.py
PATTERN_42 = (
    "XXXX.X..X",   # "2" + gap + "1"
    "...X..XX.",
    "...X...X.",
    "..X....X.",
    ".X.....X.",
    "XXXX.XXXX",
)
```

Recordar también renombrar `PATTERN_42` por consistencia.

### 14.2 "Añade una key SHOW_PATH al config (True/False)"

1. En `Config` dataclass: añadir `show_path: bool = False`.
2. En `_build_config()`: leer la key si existe, default False.
3. En `menu.run()` o en el dibujado inicial: usar `config.show_path`.

### 14.3 "Cambia el algoritmo de generación a Prim"

Reemplaza `_carve_passages` en `generator.py`. Mantén la firma e
invariantes (todas las celdas visitadas, paredes coherentes).

### 14.4 "Soporta laberintos no rectangulares (con celdas bloqueadas extra)"

Generaliza `pattern_cells` a un set arbitrario de celdas que el
generator recibe en `__init__`. Toda la lógica ya está preparada porque
el patrón "42" es exactamente esto.

### 14.5 "Imprime el laberinto sin colores (modo no-TTY)"

Añade un parámetro `use_ansi: bool` a `render()`. Si es False, usa
caracteres ASCII (`+`, `-`, `|`, `#` para wall) sin escapes ANSI.

### 14.6 "Asegúrate de que el camino más corto pasa por al menos N celdas"

Añade una validación post-generación: si `len(path) < N`, regenera con
otra semilla. Cuidado con bucles infinitos — pon un límite de intentos.

---

## 15. Edge cases y validaciones

### 15.1 Inputs raros

- **Config sin SEED** → usa seed random (`random.Random(None)`).
- **WIDTH=1 HEIGHT=1** → 1 celda; `parse_config` lo rechaza si
  ENTRY==EXIT.
- **WIDTH=1 HEIGHT=2** → 2 celdas; legal, ENTRY=0,0 EXIT=0,1.
- **PERFECT=true** (minúsculas) → aceptado (parser hace `.lower()`).
- **ENTRY = 19,14 EXIT = 0,0** → legal (entry y exit no tienen orden).

### 15.2 Errores del usuario que el programa debe sobrevivir

- Archivo de config inexistente.
- Archivo de config con permisos solo de lectura para nosotros.
- Coordenadas negativas o fuera de bounds.
- Valores no numéricos donde se esperan números.
- Tipo bool con valor distinto de True/False (`yes`, `1`, `on`, etc.).
- `OUTPUT_FILE` apunta a un directorio que no existe.
- Ctrl+C en mitad del menú interactivo.

### 15.3 Casos límite del algoritmo

- Laberinto demasiado pequeño para el patrón → warning, sigue.
- Solo 1 celda → el camino es `[start]`.
- Entry == Exit → bloqueado por parser.
- `_add_loops` con 0 candidatos → no hace nada (loop sale solo).
- `_creates_open_3x3` cerca de bordes → `max/min` cubren los límites.

---

## 16. Glosario rápido

| Término | Significado |
|---|---|
| **Laberinto perfecto** | Grafo conectado sin ciclos = spanning tree. Camino único entre 2 celdas. |
| **Spanning tree** | Árbol que conecta todos los nodos de un grafo sin formar ciclos. |
| **Bitmask** | Entero usado para guardar varios booleanos en sus bits. |
| **DFS** | Depth-First Search. Explora en profundidad antes de volver atrás. |
| **BFS** | Breadth-First Search. Explora por niveles, óptimo para shortest path no ponderado. |
| **Iterativo vs recursivo** | Mismo algoritmo; iterativo usa stack/queue explícita, recursivo usa el stack del intérprete. |
| **Backtracking** | Cuando una rama no lleva a ningún sitio, deshacer pasos hasta encontrar otra. |
| **Union-Find / DSU** | Estructura para mantener conjuntos disjuntos eficientemente (Kruskal). |
| **Context manager** | Objeto con `__enter__`/`__exit__` para usar con `with`. Garantiza cleanup. |
| **Dataclass** | Decorador que genera `__init__`/`__repr__`/`__eq__` automáticamente. |
| **Type hint** | Anotación de tipo (`x: int`); estática (no afecta runtime). |
| **PEP 257** | Estándar de docstrings. |
| **PEP 517/518/621** | Estándares de empaquetado moderno (`pyproject.toml`). |
| **`.whl`** | Wheel — built distribution; binario listo para instalar. |
| **`.tar.gz` (sdist)** | Source distribution; código fuente comprimido. |
| **ANSI escape** | Secuencia `\x1b[...m` para colorear texto en terminal. |
| **`flake8`** | Linter de estilo (PEP 8) + análisis estático básico. |
| **`mypy`** | Static type checker. Lee los type hints y verifica consistencia. |
| **`pytest`** | Framework de tests. |

---

## 🎯 Antes de la defensa, asegúrate de:

- [ ] Saber explicar cada función pública sin mirar el código.
- [ ] Poder dibujar el flujo de datos: config → MazeGenerator → solver →
      output → display.
- [ ] Tener clarísimo por qué DFS iterativo (`sys.setrecursionlimit`).
- [ ] Poder explicar el bitmask con un ejemplo concreto (`0xA = 1010`).
- [ ] Saber dibujar el patrón "42" a mano y explicar cómo se inserta.
- [ ] Tener listo el comando para instalar el `.whl` en un venv limpio.
- [ ] Haber rellenado el README con tus logins, roles y planning.
- [ ] Haber ensayado al menos 2 modificaciones rápidas (sección 14).
- [ ] Tener `make lint` y `make test` corriendo sin errores.
- [ ] Saber qué archivos son reusables y qué archivos no.

**¡Suerte en la defensa!** 🚀
