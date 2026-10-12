**Cargar datos de CALIFICÓ:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///califico.csv' AS fila
MATCH (u:Usuario {id: fila.usuario_id})
MATCH (r:Restaurante {id: fila.restaurante_id})
MERGE (u)-[rel:`CALIFICÓ`]->(r)
SET rel.puntuacion = toInteger(fila.puntuacion),
    rel.fecha = date(fila.fecha),
    rel.comentario = fila.comentario;
```

**Cargar datos de VISITÓ:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///visito.csv' AS fila
MATCH (u:Usuario {id: fila.usuario_id})
MATCH (r:Restaurante {id: fila.restaurante_id})
MERGE (u)-[rel:VISITÓ {id_visita: fila.id_visita}]->(r)
SET rel.fecha_visita = datetime(fila.fecha_visita),
    rel.consumo = toFloat(fila.consumo),
    rel.con_reserva = toBoolean(fila.con_reserva);
```

**Cargar datos de ES_AMIGO_DE:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///es_amigo_de.csv' AS fila
MATCH (a:Usuario {id: fila.usuario_id})
MATCH (b:Usuario {id: fila.amigo_id})
MERGE (a)-[r1:ES_AMIGO_DE]->(b)
SET r1.fecha_amistad = date(fila.fecha_amistad)
MERGE (b)-[r2:ES_AMIGO_DE]->(a)
SET r2.fecha_amistad = date(fila.fecha_amistad);
```

**Cargar datos de PERTENECE_A:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///pertenece_a.csv' AS fila
MATCH (r:Restaurante {id: fila.restaurante_id})
MATCH (t:TipoCocina {id: fila.tipo_cocina_id})
MERGE (r)-[:PERTENECE_A]->(t);
```

**Cargar datos de OFRECE:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///ofrece.csv' AS fila
MATCH (r:Restaurante {id: fila.restaurante_id})
MATCH (p:Platillo {id: fila.platillo_id})
MERGE (r)-[rel:OFRECE]->(p)
SET rel.precio = toFloat(fila.precio),
    rel.disponible = toBoolean(fila.disponible);
```

**Cargar datos de PREPARA:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///prepara.csv' AS fila
MATCH (c:Chef {id: fila.chef_id})
MATCH (p:Platillo {id: fila.platillo_id})
MERGE (c)-[rel:PREPARA]->(p)
SET rel.estilo = fila.estilo,
    rel.especialidad = fila.especialidad;
```

**Cargar datos de TRABAJA_EN:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///trabaja_en.csv' AS fila
MATCH (c:Chef {id: fila.chef_id})
MATCH (r:Restaurante {id: fila.restaurante_id})
MERGE (c)-[rel:TRABAJA_EN]->(r)
SET rel.fecha_inicio = date(fila.fecha_inicio),
    rel.puesto = fila.puesto;
```

**Cargar datos de LE_GUSTA:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///le_gusta.csv' AS fila
MATCH (u:Usuario {id: fila.usuario_id})
MATCH (t:TipoCocina {id: fila.tipo_cocina_id})
MERGE (u)-[rel:LE_GUSTA]->(t)
SET rel.nivel_interes = toInteger(fila.nivel_interes);
```



**Cantidad de relaciones por tipo:**

```sql
MATCH ()-[rel]->()
RETURN type(rel) AS tipo_relacion,
       count(rel) AS cantidad
ORDER BY cantidad DESC;
```

**Eliminar todos los nodos y relaciones asociadas a estos:**

```sql
MATCH (n)
DETACH DELETE n;
```

**Comprobar la cantidad de relaciones que existen:**

```sql
MATCH ()-[r]->()
RETURN count(r) AS relaciones_existentes;
```