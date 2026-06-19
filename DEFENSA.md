# 🛡️ Guion de defensa — A-Maze-ing

> Documento interno de preparación (NO se entrega). Contiene el guion palabra
> por palabra para explicar el proyecto y un banco de preguntas y respuestas.
> Autores: **nicorodr** y **jonadomi**.

---

## 0. Chuleta de 30 segundos (lo que NUNCA hay que olvidar)

- **Qué es:** un generador de laberintos en Python que lee un config, genera el
  laberinto (perfecto o no), dibuja un "42" dentro, lo resuelve y lo guarda en
  un fichero con codificación hexadecimal. Además lo pinta en la terminal.
- **Algoritmo:** *recursive backtracker* (DFS aleatorio con pila).
- **Codificación:** cada celda es un número 0–15; cada bit = una pared
  **cerrada**. Bit 0=N(1), 1=E(2), 2=S(4), 3=O(8). `15` = 4 paredes cerradas.
- **3 capas:** config (validación) → `mazegen` (lógica pura reutilizable) →
  programa principal + visor (entrada/salida).
- **Lo reutilizable:** el paquete `mazegen`, instalable con pip (wheel).
- **Bonus:** animación del camino solución en el visor.

---

## 1. Guion palabra por palabra (explicación principal)

> Léelo en voz alta tal cual, o adáptalo. Está pensado para durar ~3-4 minutos.

### Introducción

«Nuestro proyecto es **A-Maze-ing**, un generador de laberintos escrito en
Python. La idea es sencilla de enunciar pero tiene varias piezas: el programa
lee un fichero de configuración, genera un laberinto aleatorio —que puede ser
perfecto o no—, dibuja un "42" reconocible dentro del laberinto, calcula el
camino más corto entre la entrada y la salida, y escribe todo en un fichero de
salida. Además, ofrecemos una representación visual en la terminal.»

### La arquitectura (lo más importante)

«Hemos dividido el proyecto en **tres capas bien separadas**, y esto es una
decisión de diseño deliberada:

1. La **capa de configuración**, en `config.py`, que lee y valida el fichero de
   entrada. No sabe nada de laberintos: solo se encarga de que los datos sean
   correctos.

2. La **lógica pura**, en el paquete `mazegen`. Aquí está la clase
   `MazeGenerator`, que genera y resuelve el laberinto. Es importante que esta
   capa **no imprime, no dibuja y no toca ficheros**: solo produce la estructura
   de datos. Por eso es reutilizable e instalable con pip, como pide el subject.

3. El **programa principal**, `a_maze_ing.py`, que orquesta todo: pide la
   configuración, llama al generador y escribe el fichero. El dibujado está en
   `viewer.py`, un módulo aparte.»

### La codificación

«El corazón del proyecto es la **codificación de las paredes**. Cada celda del
laberinto es un número del 0 al 15, es decir, 4 bits. Cada bit representa una
pared **cerrada**: el bit 0 es el Norte, el 1 el Este, el 2 el Sur y el 3 el
Oeste. Por ejemplo, una celda con valor 15 —en binario 1111— tiene las cuatro
paredes cerradas; una celda con valor 10 —binario 1010— tiene cerradas el Este
y el Oeste. Empezamos con todo el laberinto a 15, es decir, todas las paredes
cerradas, y vamos "excavando" abriendo paredes.»

### La generación

«Para generar usamos el algoritmo **recursive backtracker**, que es una
búsqueda en profundidad aleatoria. Partimos de una celda al azar y, mientras
haya vecinos sin visitar, elegimos uno al azar, **abrimos la pared entre las dos
celdas** y avanzamos. Cuando llegamos a un callejón sin salida, retrocedemos
usando una pila hasta encontrar una celda con vecinos pendientes. Lo
implementamos de forma **iterativa con una pila explícita**, no con recursión,
para no chocar con el límite de recursión de Python en laberintos grandes.

Una propiedad clave: como cada celda se visita una sola vez, el resultado es un
**árbol de expansión** —un *spanning tree*—, lo que significa que hay
exactamente **un único camino** entre cualquier par de celdas. Eso es justo la
definición de laberinto perfecto. Por eso, cuando `PERFECT=True`, no tenemos que
hacer nada especial: el laberinto ya es perfecto por construcción.»

### El modo no perfecto (braiding)

«Cuando `PERFECT=False`, añadimos bucles con una técnica llamada *braiding*:
recorremos los callejones sin salida —celdas con tres paredes cerradas— y
abrimos una pared extra hacia un vecino. Eso conecta dos pasillos que antes
estaban separados y crea un bucle, de modo que ya hay varios caminos posibles.
Cada apertura la validamos: si fuese a crear un área abierta de 3×3, que el
subject prohíbe, la **revertimos**.»

### El patrón "42"

«El "42" lo dibujamos con celdas completamente cerradas. Lo definimos como un
mapa de bits de 7×5, lo centramos en el laberinto y **reservamos esas celdas
antes de generar**, marcándolas como ya visitadas. Así el algoritmo nunca las
excava y se quedan con valor 15, es decir, como bloques sólidos. El braiding
también tiene prohibido abrir paredes hacia ellas. Si el laberinto es demasiado
pequeño para que quepa el "42", o si la entrada o la salida caen encima,
mostramos un mensaje de aviso y lo omitimos, tal y como permite el subject.»

### La resolución

«Para encontrar el camino más corto usamos una **búsqueda en anchura (BFS)**
desde la entrada hasta la salida. Elegimos BFS porque en un grafo sin pesos
garantiza el camino más corto, cosa que una búsqueda en profundidad no
garantizaría. El resultado lo damos como una cadena de letras N, E, S, O.»

### La salida

«El fichero de salida tiene primero el laberinto, una fila por línea, cada celda
como un dígito hexadecimal. Después de una línea en blanco escribimos las
coordenadas de entrada, las de salida y el camino más corto. Incluimos el script
`output_validator.py` que viene con el subject, y nuestro fichero pasa su
validación de coherencia de paredes.»

### El visor y el bonus

«La representación visual está en la terminal, en `viewer.py`. Tiene un menú
numerado con todas las interacciones que pide el subject: regenerar, mostrar u
ocultar el camino y cambiar el color de las paredes; además añadimos cambiar el
color del "42", mostrar la semilla para reproducir el laberinto, y como **bonus**
una **animación** que dibuja el camino solución paso a paso desde la entrada
hasta la salida. La animación vive solo en el visor para no ensuciar el paquete
reutilizable.»

### El cierre

«Por último, hemos empaquetado la lógica como un módulo `mazegen` instalable con
pip —generamos el wheel con `make package`—, tenemos un Makefile con todas las
reglas, y el código pasa `flake8` y `mypy` incluso en modo `--strict`.»

---

## 2. Orden de la demo (qué teclear, en orden)

```sh
# 1. Montar el entorno (una vez)
make install

# 2. Enseñar el config por defecto
cat config.txt

# 3. make run -> genera maze.txt Y abre el visor interactivo
make run
#    En el menú: 1 regenera, 2 camino, 3 color paredes, 4 color 42,
#                5 ANIMACIÓN, 6 muestra el seed, 7 salir

# 4. (tras salir) enseñar el fichero generado y validarlo
cat maze.txt
.venv/bin/python output_validator.py maze.txt   # no imprime nada = OK

# 5. Demostrar reproducibilidad: copiar el seed de la opción 6 al config
#    (SEED=...) y volver a make run -> mismo laberinto

# 6. Demostrar PERFECT=False: poner PERFECT=False y make run -> bucles

# 7. Calidad de código
make lint
make lint-strict

# 8. Reconstruir el paquete desde cero (lo piden en evaluación)
make package
ls mazegen-*.whl mazegen-*.tar.gz

# 9. Demostrar que el paquete es reutilizable
.venv/bin/python -c "from mazegen import MazeGenerator; \
g=MazeGenerator(10,10,True,(0,0),(9,9),seed=1); g.generate(); print(g.solve())"

# 10. (opcional) el comando obligatorio puro, solo escribe el fichero
python3 a_maze_ing.py config.txt
```

---

## 3. Banco de preguntas y respuestas

### Sobre el algoritmo

**P: ¿Por qué recursive backtracker y no Prim o Kruskal?**
R: Los tres generan laberintos perfectos válidos. Elegimos el backtracker porque
es el más sencillo de razonar, siempre queda totalmente conectado, es rápido
—O(ancho × alto)— y tiende a generar pasillos largos y sinuosos. Además, la
propiedad de laberinto perfecto sale gratis, lo que simplificó construir encima
el solver, el "42" y el braiding.

**P: ¿Por qué iterativo con pila y no recursivo?**
R: Por el límite de recursión de Python, que por defecto ronda las 1000
llamadas. Un laberinto de 100×100 tiene 10.000 celdas y la recursión
desbordaría. Con una pila explícita no hay ese problema.

**P: ¿Cómo garantizáis que el laberinto perfecto es realmente perfecto?**
R: Porque el DFS visita cada celda exactamente una vez y solo avanza a vecinos
sin visitar; nunca cierra un ciclo. Eso es un árbol de expansión: celdas−1
aristas y un único camino entre cualquier par de celdas.

**P: ¿Cómo hacéis que NO sea perfecto?**
R: Con *braiding*: tras generar el árbol, abrimos una pared extra en cada
callejón sin salida, creando bucles.

### Sobre las restricciones

**P: ¿Cómo evitáis áreas abiertas de 3×3?**
R: Tras cada apertura extra del braiding comprobamos si esa celda forma parte de
un bloque 3×3 totalmente abierto; si es así, deshacemos la apertura. En el modo
perfecto no puede pasar: un área abierta es un ciclo, y un árbol no tiene ciclos.

### Sobre el "42"

**P: ¿Por qué reserváis el "42" ANTES de generar?**
R: Para que el algoritmo lo rodee y esas celdas queden cerradas y coherentes. Si
excaváramos primero y cerráramos después, dejaríamos datos incoherentes y celdas
inalcanzables.

**P: ¿El "42" no rompe la conectividad?**
R: No. Sus celdas son islas cerradas a propósito, y el subject permite esa
excepción. El resto de celdas libres siguen todas conectadas; lo verificamos con
un BFS que las alcanza todas. Dejamos un margen de una celda alrededor.

**P: ¿De dónde sale el tamaño 7×5 y el mínimo 9×7?**
R: El tamaño del "42" lo elegimos nosotros (el subject no lo fija); 7×5 es lo
mínimo para que sea legible. El mínimo 9×7 es ese 7×5 más un margen de una celda
por lado. Si no cabe, lo omitimos con un mensaje.

### Sobre la codificación y la salida

**P: Explica la codificación de una celda.**
R: Número de 0 a 15, 4 bits. Cada bit a 1 = pared cerrada: bit 0 Norte, 1 Este,
2 Sur, 3 Oeste. `A` = 10 = 1010 = Este y Oeste cerrados.

**P: ¿Cómo garantizáis que dos celdas vecinas coinciden en su pared compartida?**
R: Al abrir una pared limpiamos el bit en **las dos** celdas a la vez (el bit de
una y el opuesto del vecino). El `output_validator.py` del subject lo confirma.

**P: La entrada es `x,y` pero el grid es `[fila][columna]`. ¿Cómo lo manejáis?**
R: En el config las coordenadas son (x, y) = (columna, fila); internamente el
grid es `grid[fila][columna]`, así que invertimos: fila = y, columna = x.

### Sobre el solver

**P: ¿Por qué BFS y no DFS o A*?**
R: BFS garantiza el camino más corto en un grafo sin pesos. DFS daría *un*
camino, no el más corto. A* sería sobreingeniería sin una heurística útil aquí.

### Sobre la configuración

**P: ¿Por qué pydantic?**
R: Por la validación declarativa: tipos y reglas con poco código, conversión de
tipos y mensajes de error claros. Solo es dependencia de la **aplicación**, no
del módulo reutilizable.

**P: ¿pydantic está en el paquete `mazegen`?**
R: No, a propósito. `mazegen` no tiene dependencias externas; pydantic vive solo
en `config.py`. Por eso las `dependencies` del `pyproject.toml` están vacías.

### Sobre el empaquetado

**P: ¿Por qué `mazegen` es un paquete aparte?**
R: Porque el subject exige que la lógica sea un módulo independiente instalable
con pip. Mantenerlo sin entrada/salida lo hace de verdad reutilizable.

**P: Reconstruye el paquete en vivo.**
R: `make install` y `make package` (ejecuta `python -m build`), que genera el
`.whl` y el `.tar.gz` en la raíz.

**P: ¿`pyproject.toml` vs `requirements.txt`?**
R: El `pyproject.toml` describe cómo se construye el **paquete** y qué necesita
(nada). El `requirements.txt` lista lo que necesita la **aplicación** (pydantic)
y lo usa `make install`. Librería reutilizable vs. entorno de la app.

### Sobre el visor y el bonus

**P: ¿Por qué terminal y no MLX?**
R: El subject permite las dos. MLX es una librería de C sin binding oficial para
Python; engancharla con ctypes sería frágil. La terminal no tiene dependencias y
es robusta.

**P: ¿Qué interacciones tiene y cuáles son obligatorias?**
R: Obligatorias: regenerar, mostrar/ocultar camino y cambiar el color de las
paredes. Añadimos: cambiar el color del "42", mostrar el seed y una animación.
Es un menú numerado del 1 al 7.

**P: ¿Cuál es vuestro bonus?**
R: La **animación del camino solución**: dibuja el camino creciendo celda a
celda desde la entrada hasta la salida, limpiando y redibujando la pantalla. La
hicimos en el visor (`viewer.py`), no en el paquete `mazegen`, para mantener la
lógica reutilizable libre de código de pantalla.

**P: ¿Por qué `make run` abre el visor pero `python3 a_maze_ing.py` no?**
R: El comando obligatorio debe escribir el **fichero** y nada más, para que una
corrección automática no se bloquee esperando entrada. `make run` ejecuta ese
comando y luego, como conveniencia, abre el visor.

**P: ¿Cómo reproduzco un laberinto concreto?**
R: La opción 6 del menú muestra la semilla del laberinto actual; poniéndola como
`SEED=...` en el config, `make run` regenera exactamente el mismo.

### Sobre la calidad y los errores

**P: ¿Cómo garantizáis que nunca casca?**
R: Capturamos los errores esperables con mensajes claros: fichero no encontrado,
config inválida (ValueError), error de escritura (OSError) e ImportError al
arrancar. Todo por stderr, con código de salida 1.

**P: No veo ningún `.flake8`. ¿Cómo excluís el `.venv` del linter?**
R: Las exclusiones están en los comandos del Makefile (`--extend-exclude` para
flake8 y `--exclude` para mypy). Sin ficheros de config ocultos; se ve qué
excluimos: solo el entorno virtual y los artefactos de build.

**P: ¿Pasa mypy en estricto?**
R: Sí, `make lint-strict` ejecuta `mypy --strict` y pasa sin errores.

### Sobre el uso de IA

**P: ¿Usasteis IA? ¿Para qué?**
R: Sí, como apoyo tipo *pair programming*: estructurar el paquete y el Makefile,
revisar flake8/mypy y razonar la lógica del braiding y la colocación del "42".
Cada parte la hemos leído, probado y ajustado nosotros, y podemos explicar todo.

---

## 4. Preguntas trampa / puntos débiles a tener preparados

- **Coordenadas (x,y) vs (fila,columna):** ten clara la conversión.
- **Por qué un perfecto no tiene áreas 2×2/3×3:** serían ciclos, y un árbol no
  tiene ciclos.
- **El "42" como excepción a "sin celdas aisladas":** está permitido.
- **`mazegen` sin dependencias:** pydantic está en la app, no en el paquete.
- **El bonus (animación) está en el visor, no en el paquete:** para no ensuciar
  la lógica reutilizable.
- **Saber reconstruir el wheel en vivo** con `make package`.
- **Roles del equipo y planificación:** repasad quién hizo qué de verdad.

---

## 5. Checklist final antes de entrar

- [ ] `make install` funciona en limpio.
- [ ] `make run` escribe `maze.txt` y abre el menú numerado.
- [ ] Las 7 opciones del menú funcionan (incl. animación y mostrar seed).
- [ ] `PERFECT=False` genera bucles y pasa el `output_validator.py`.
- [ ] `make lint` y `make lint-strict` pasan.
- [ ] `make package` reconstruye el `.whl` y el `.tar.gz`.
- [ ] El "42" se ve en el visor.
- [ ] Sabéis explicar la codificación de paredes de memoria.
- [ ] Tenéis claros los roles de cada uno.
- [ ] **El proyecto está commiteado en git** (si no, sgoinfre borra los ficheros).
