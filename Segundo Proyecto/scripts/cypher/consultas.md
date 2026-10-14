**Consulta #1:**

```sql
// Buscar el usuario y sus amigos hasta tres grados de separación
MATCH (usuario:Usuario {id: '0b46c9e1-989c-5133-bc46-539135c04a44'})-[:ES_AMIGO_DE*1..3]->(amigo:Usuario)

// Descartar que los usuarios sean iguales
WHERE usuario <> amigo

// Conservar solo una aparición de cada amigo
WITH DISTINCT usuario, amigo

// Buscar las calificaciones a los restaurantes por parte de los amigos
MATCH (amigo)-[calificacion:`CALIFICÓ`]->(restaurante:Restaurante)

// Considerar calificaciones iguales o superiores a 4 estrellas y descartar restaurantes que el usuario ya visitó
WHERE calificacion.puntuacion >= 4
    AND NOT EXISTS {
        MATCH (usuario)-[:`VISITÓ`]->(restaurante)
    }

// Calcular la cantidad de amigos y el promedio de calificaciones del restaurante
WITH restaurante,
    count(DISTINCT amigo) AS cantidad_amigos,
    avg(calificacion.puntuacion) AS calificacion_promedio_restaurante

// Retornar los datos correspondientes
RETURN restaurante.id AS id_restaurante,
    restaurante.nombre AS nombre_restaurante,
    cantidad_amigos,
    round(calificacion_promedio_restaurante * 100) / 100.0 AS calificacion_promedio_restaurante

// Ordenar de forma descendente de acuerdo a la cantidad de amigos y luego por calificación promedio del restaurante
ORDER BY cantidad_amigos DESC,
    calificacion_promedio_restaurante DESC;
```

<br/>

**Consulta #2:**

```sql
// Buscar los chefs y los restaurantes donde trabajan
MATCH (chef:Chef)-[:TRABAJA_EN]->(restaurante:Restaurante)

// Buscar las calificaciones registradas para cada restaurante
MATCH (:Usuario)-[calificacion:`CALIFICÓ`]->(restaurante)

// Calcular la calificación promedio de cada restaurante
WITH chef, 
    restaurante, 
    avg(calificacion.puntuacion) AS calificacion_prom_restaurante

// Conservar solamente los restaurantes con calificación promedio superior a 4
WHERE calificacion_prom_restaurante > 4

// Agrupar los restaurantes con calificaciones superiores a 4 asociados a cada chef
WITH chef,
    collect({
        restaurante: restaurante.nombre,
        promedio: calificacion_prom_restaurante
    }) AS restaurantes_prestigio_chef

// Buscar los platillos que prepara cada chef y los restaurantes que los ofrecen
MATCH (chef)-[:PREPARA]->(platillo:Platillo)<-[:OFRECE]-(r:Restaurante)

// Calcular el número de restaurantes distintos donde se ofrecen los platillos del chef
WITH chef,
    restaurantes_prestigio_chef,
    count(DISTINCT r) AS restaurante_con_sus_platillos

// Conservar los chefs cuyos platillos están en al menos 3 restaurantes
WHERE restaurante_con_sus_platillos >= 3

// Retornar los datos correspondientes
RETURN chef.id AS id_chef,
       chef.nombre AS nombre_chef,
       restaurantes_prestigio_chef,
       size(restaurantes_prestigio_chef) AS cantidad_restaurantes_prestigio,
       restaurante_con_sus_platillos

// Ordenar según la presencia de sus platillos y sus restaurantes bien calificados.
ORDER BY restaurante_con_sus_platillos DESC,
        restaurante_con_sus_platillos DESC;
```

<br/>

**Consulta #3:**

```sql
// Buscar los restaurantes que tienen visitas registradas
MATCH (restaurante:Restaurante)<-[visita:`VISITÓ`]-()

// Calcular el promedio de visitas que se hicieron con reserva de cada restaurante
WITH restaurante,
    avg(CASE
        WHEN visita.con_reserva = true THEN 1.0
        ELSE 0.0
    END) AS tasa_reservas

// Agrupar en una lista cada restaurante con su proporción de reservas y calcular el promedio general de reservas
WITH collect({
    restaurante: restaurante,
    tasa_reservas: tasa_reservas
}) AS datos_reservas,
    avg(tasa_reservas) AS promedio_general_reservas

// Buscar las calificaciones de los restaurantes
MATCH (:Usuario)-[calificacion:`CALIFICÓ`]->(:Restaurante)

// Calcular el promedio general de las calificaciones
WITH datos_reservas,
    promedio_general_reservas,
    avg(calificacion.puntuacion) AS promedio_general_calificaciones

// Separar la lista
UNWIND datos_reservas AS dato

// Recuperar los datos de cada restaurante y conservar los promedios
WITH dato.restaurante AS restaurante,
    dato.tasa_reservas AS tasa_reservas,
    promedio_general_reservas,
    promedio_general_calificaciones

// Buscar las calificaciones del restaurante
MATCH (:Usuario)-[calificacion:`CALIFICÓ`]->(restaurante)

// Calcular la calificación promedio del restaurante
WITH restaurante,
    tasa_reservas,
    promedio_general_reservas,
    promedio_general_calificaciones,
    avg(calificacion.puntuacion) AS calificacion_promedio_restaurante

// Conservar los restaurantes con una tasa de reserva superior al promedio general, pero calificación bajo el promedio
WHERE tasa_reservas > promedio_general_reservas
    AND calificacion_promedio_restaurante < promedio_general_calificaciones

// Retornar los datos correspondientes
RETURN restaurante.id AS id_restaurante,
    restaurante.nombre AS nombre_restaurante,
    round(tasa_reservas * 10000) / 100.0 AS porcentaje_reservas_restaurante,
    round(promedio_general_reservas * 10000) / 100.0 AS promedio_general_reservas,
    round(calificacion_promedio_restaurante * 100) / 100.0 AS calificacion_promedio_restaurante,
    round(promedio_general_calificaciones * 100) / 100.0 AS promedio_general_calificaciones

// Ordenar según la diferencia en la proporción de reservas de forma descendente
ORDER BY tasa_reservas - promedio_general_reservas DESC;
```

<br/>

**Consulta #4:**

```sql
// Buscar las visitas realizadas a restaurantes
MATCH (:Usuario)-[visita:`VISITÓ`]->(restaurante:Restaurante)

// Calcular el consumo promedio real y el consumo esperado
WITH restaurante,
    avg(visita.consumo) AS consumo_promedio_real,
    (restaurante.precio_min_rango + restaurante.precio_max_rango) / 2.0 AS consumo_esperado

// Calcular la diferencia entre consumos y el valor absoluto de esta
WITH restaurante,
    consumo_promedio_real,
    consumo_esperado,
    consumo_promedio_real - consumo_esperado AS diferencia_consumos,
    abs(consumo_promedio_real - consumo_esperado) AS diferencia_abs_consumos

// Retornar los datos correspondientes
RETURN restaurante.id AS id_restaurante,
    restaurante.nombre AS nombre_restaurante,
    restaurante.precio_min_rango AS precio_minimo,
    restaurante.precio_max_rango AS precio_maximo,
    round(consumo_esperado * 100) / 100.0 AS consumo_esperado,
    round(consumo_promedio_real * 100) / 100.0 AS consumo_promedio_real,
    round(diferencia_consumos * 100) / 100.0 AS diferencia_consumos,
    round(diferencia_abs_consumos * 100) / 100.0 AS diferencia_abs_consumos

// Ordenar de forma descendente según la diferencia absoluta entre los consumos
ORDER BY diferencia_abs_consumos DESC;
```

<br/>

**Consulta #5:**

```sql
// Buscar los tipos de cocina que le gustan a los usuarios
MATCH (usuario:Usuario)-[gusta:LE_GUSTA]->(tipopreferido:TipoCocina)

// Calcular el mayor nivel de interés y guardar los tipos de cocina preferidos
WITH usuario,
    max(gusta.nivel_interes) AS max_interes,
    collect({tipo: tipopreferido, interes: gusta.nivel_interes}) AS preferencias

// Conservar los tipos de cocina que tienen el nivel de interés máximo
WITH usuario,
    max_interes,
    [preferencia IN preferencias WHERE preferencia.interes = max_interes | preferencia.tipo] AS favoritos

// Buscar las visitas del usuario y los tipos de cocina de los restaurantes
MATCH (usuario)-[visita:VISITÓ]->(:Restaurante)-[:PERTENECE_A]->(tipo:TipoCocina)

// Contar las visitas que realizó a cada tipo de cocina.
WITH usuario,
    max_interes,
    favoritos,
    tipo,
    count(visita) AS num_visitas

// Agrupar los tipos de cocina visitados junto a su cantidad de visitas
WITH usuario, 
    max_interes,
    favoritos,
    collect({tipo: tipo, visitas: num_visitas}) AS restaurante_visitas

// Encontrar la cantidad máxima de visitas entre los tipos de cocina visitados
WITH usuario,
    max_interes,
    favoritos,
    restaurante_visitas,
    reduce(maximo = 0, elemento IN restaurante_visitas |
        CASE
            WHEN elemento.visitas > maximo THEN elemento.visitas
            ELSE maximo
        END
    ) AS max_visitas

// Obtener los tipos de cocina que tienen el número máximo de visitas
WITH usuario, 
    max_interes, 
    favoritos, 
    restaurante_visitas, 
    max_visitas,
    [elemento IN restaurante_visitas WHERE elemento.visitas = max_visitas | elemento.tipo] AS tipos_mas_visitados

// Conservar usuarios que tienen visitas registradas y donde el tipo de cocina más visitado no sea el favorito
WHERE max_visitas > 0
    AND none(tipo IN tipos_mas_visitados WHERE tipo IN favoritos)

// Desagrupar la lista por cada tipo de cocina favorito del usuario
UNWIND favoritos AS favorito

// Calcular las visitas del tipo favorito
WITH usuario,
    max_interes,
    max_visitas,
    tipos_mas_visitados,
    favorito,
    coalesce(head([elemento IN restaurante_visitas WHERE elemento.tipo = favorito | elemento.visitas]), 0) AS num_visitas_favorito

// Retornar los datos correspondientes
RETURN usuario.id AS id_usuario,
       usuario.nombre AS nombre_usuario,
       favorito.nombre AS tipo_cocina_favorito,
       [tipo IN tipos_mas_visitados | tipo.nombre] AS tipos_cocina_mas_visitado,
       max_interes AS nivel_interes_favorito,
       num_visitas_favorito,
       max_visitas AS num_visitas_restaurante_mas_visitado

// Ordenar descendentemente, priorizando las mayores diferencias y luego ordenar por nombre de usuario
ORDER BY num_visitas_restaurante_mas_visitado - num_visitas_favorito DESC,
    nombre_usuario ASC;
```