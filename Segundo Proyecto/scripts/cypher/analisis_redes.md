# Calcular rutas más cortas entre usuarios (grados de separación)

**Consulta para un grado de separación:**

```sql
// Buscar los dos usuarios y encontrar la ruta de amistad más corta entre ellos
MATCH ruta = shortestPath((a:Usuario {id: '37424608-0fd4-555d-8ba1-0b6d66366308'})-[:ES_AMIGO_DE*]-(b:Usuario {id: '21ebc54a-d6ff-539e-bb00-84a02f9c2cb8'}))

// Mostrar los usuarios, la ruta encontrada y los grados de separación
RETURN a.nombre AS usuario_origen,
       b.nombre AS usuario_destino,
       length(ruta) AS grados_separacion,
       [usuario IN nodes(ruta) | usuario.nombre] AS usuarios_en_ruta,
       ruta AS ruta_encontrada;
```

**Consulta para dos grados de separación:**

```sql
// Buscar los dos usuarios y encontrar la ruta de amistad más corta entre ellos
MATCH ruta = shortestPath((a:Usuario {id: '37424608-0fd4-555d-8ba1-0b6d66366308'})-[:ES_AMIGO_DE*]-(b:Usuario {id: '1414f8dd-4a8e-5e30-8997-2642afb35b3d'}))

// Mostrar los usuarios, la ruta encontrada y los grados de separación
RETURN a.nombre AS usuario_origen,
       b.nombre AS usuario_destino,
       length(ruta) AS grados_separacion,
       [usuario IN nodes(ruta) | usuario.nombre] AS usuarios_en_ruta,
       ruta AS ruta_encontrada;
```

**Consulta para tres grados de separación:**

```sql
// Buscar los dos usuarios y encontrar la ruta de amistad más corta entre ellos
MATCH ruta = shortestPath((a:Usuario {id: '37424608-0fd4-555d-8ba1-0b6d66366308'})-[:ES_AMIGO_DE*]-(b:Usuario {id: '28f18eed-38f1-52df-8d84-641a8537ea46'}))

// Mostrar los usuarios, la ruta encontrada y los grados de separación
RETURN a.nombre AS usuario_origen,
       b.nombre AS usuario_destino,
       length(ruta) AS grados_separacion,
       [usuario IN nodes(ruta) | usuario.nombre] AS usuarios_en_ruta,
       ruta AS ruta_encontrada;
```

**Consulta para conocer los amigos directos e indirectos de un usuario, indicando su grado de separación:**

```sql
// Buscar un usuario y sus amigos directos e indirectos hasta tres grados de separación
MATCH ruta = (origen:Usuario {id: '37424608-0fd4-555d-8ba1-0b6d66366308'})-[:ES_AMIGO_DE*1..3]-(destino:Usuario)

WITH origen, destino, min(length(ruta)) AS grados_separacion

RETURN
    origen.id AS id_usuario_origen,
    destino.id AS id_usuario_destino,
    grados_separacion

ORDER BY grados_separacion, id_usuario_destino;
```



# Identificar restaurantes altamente conectados (con más chefs y platillos destacados)

**Consulta para identificar los restaurantes con mayor grado de conectividad (tabla):**

```sql
// Buscar todos los nodos que representan restaurantes
MATCH (r:Restaurante)

// Buscar los chefs que trabajan en cada restaurante.
OPTIONAL MATCH (c:Chef)-[:TRABAJA_EN]->(r)

// Agrupar los resultados por restaurante y contar los chefs distintos
WITH r, 
    count(DISTINCT c) AS cantidad_chefs

// Buscar los platillos que ofrece cada restaurante y que estén disponibles
OPTIONAL MATCH (r)-[:OFRECE {disponible: true}]->(p:Platillo)

// Agrupar por restaurante, conservando la cantidad de chefs y contar los platillos distintos que ofrece cada restaurante
WITH r,
    cantidad_chefs,
    count(DISTINCT p) AS cantidad_platillos

// Calcular un indicador de conectividad parcial
WITH r,
    cantidad_chefs,
    cantidad_platillos,
    cantidad_chefs + cantidad_platillos AS grado_conectividad

// Devolver los datos a mostrar
RETURN
    r.id AS id_restaurante,
    r.nombre AS nombre_restaurante,
    cantidad_chefs,
    cantidad_platillos,
    grado_conectividad

// Ordenar descendentemente por grado de conectividad, luego por cantidad de chefs
ORDER BY grado_conectividad DESC,
    cantidad_chefs DESC

// Mostrar únicamente los primeros diez restaurantes
LIMIT 10;
```

**Consulta para visualizar las conexiones entre restaurantes, chefs y platillos (grafo):**

```sql
// Buscar todos los restaurantes
MATCH (r:Restaurante)

// Contar los chefs que trabajan en cada restaurante
OPTIONAL MATCH (c:Chef)-[:TRABAJA_EN]->(r)
WITH r, 
    count(DISTINCT c) AS cantidad_chefs

// Contar los platillos disponibles que ofrece cada restaurante
OPTIONAL MATCH (r)-[:OFRECE {disponible: true}]->(p:Platillo)
WITH r,
    cantidad_chefs,
    count(DISTINCT p) AS cantidad_platillos

// Calcular el indicador de conectividad parcial
WITH r,
    cantidad_chefs,
    cantidad_platillos,
    cantidad_chefs + cantidad_platillos AS grado_conectividad

// Ordenar los restaurantes y seleccionar los diez primeros
ORDER BY grado_conectividad DESC,
    cantidad_chefs DESC
LIMIT 10

// Recuperar las relaciones con los chefs que trabajan en cada restaurante
OPTIONAL MATCH (c:Chef)-[trabajo:TRABAJA_EN]->(r)

// Recuperar los platillos disponibles que ofrece cada restaurante
OPTIONAL MATCH (r)-[ofrece:OFRECE {disponible: true}]->(p:Platillo)

// Devolver los nodos y las relaciones para visualizar el grafo
RETURN r, trabajo, c, ofrece, p;
```