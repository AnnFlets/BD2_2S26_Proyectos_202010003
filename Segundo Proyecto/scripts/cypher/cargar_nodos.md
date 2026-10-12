**Cargar datos de Usuarios:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///usuarios.csv' AS fila
MERGE (u:Usuario {id: fila.id})
SET u.nombre = fila.nombre,
    u.email = fila.email,
    u.edad = toInteger(fila.edad),
    u.pais = fila.pais;
```

**Cargar datos de Restaurantes:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///restaurantes.csv' AS fila
MERGE (r:Restaurante {id: fila.id})
SET r.nombre = fila.nombre,
    r.anio_apertura = toInteger(fila.anio_apertura),
    r.precio_min_rango = toFloat(fila.precio_min_rango),
    r.precio_max_rango = toFloat(fila.precio_max_rango),
    r.descripcion = fila.descripcion;
```

**Cargar datos de Chefs:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///chefs.csv' AS fila
MERGE (c:Chef {id: fila.id})
SET c.nombre = fila.nombre,
    c.fecha_nacimiento = fila.fecha_nacimiento,
    c.nacionalidad = fila.nacionalidad;
```

**Cargar datos de Platillos:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///platillos.csv' AS fila
MERGE (p:Platillo {id: fila.id})
SET p.nombre = fila.nombre,
    p.precio = toFloat(fila.precio),
    p.descripcion = fila.descripcion;
```

**Cargar datos de Tipos de Cocina:**

```sql
LOAD CSV WITH HEADERS FROM 'file:///tipos_cocina.csv' AS fila
MERGE (tc:TipoCocina {id: fila.id})
SET tc.nombre = fila.nombre,
    tc.descripcion = fila.descripcion;
```


**Cantidad de Usuarios insertados:**

```sql
MATCH (u:Usuario)
RETURN count(u) AS total_usuarios;
```

**Cantidad de Restaurantes insertados:**

```sql
MATCH (r:Restaurante)
RETURN count(r) AS total_restaurantes;
```

**Cantidad de Chefs insertados:**

```sql
MATCH (c:Chef)
RETURN count(c) AS total_chefs;
```

**Cantidad de Platillos insertados:**

```sql
MATCH (p:Platillo)
RETURN count(p) AS total_platillos;
```

**Cantidad de Tipos de Cocina insertados:**

```sql
MATCH (t:TipoCocina)
RETURN count(t) AS total_tipos_cocina;
```




**Eliminar todos los nodos y relaciones asociadas a estos:**

```sql
MATCH (n)
DETACH DELETE n;
```

**Comprobar la cantidad de nodos que existen:**

```sql
MATCH (n)
RETURN count(n) AS nodos_existentes;
```