from collections import defaultdict
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, BatchType
from faker import Faker
from uuid import uuid4
from datetime import datetime, timedelta
import random


# ============================================================
# CONFIGURACIÓN
# NUM_RESERVAS = 100_000
# NUM_PASAJEROS = 10_000
# NUM_VUELOS = 2_000
# ============================================================

NUM_RESERVAS = 100_000
NUM_PASAJEROS = 10_000
NUM_VUELOS = 2_000

# 100,000 / 2,000 = 50 reservas por vuelo
RESERVAS_POR_VUELO = NUM_RESERVAS // NUM_VUELOS

SEED = 42

fake = Faker("es_ES")
random.seed(SEED)
Faker.seed(SEED)


# ============================================================
# CONEXIÓN A CASSANDRA
# ============================================================

cluster = Cluster(
    ["127.0.0.1"],
    port=9042
)

session = cluster.connect("reservas_aereas")

print("Conectado a Cassandra.")


try:

    # ========================================================
    # STATEMENTS PREPARADOS
    # ========================================================

    insert_historial = session.prepare("""
        INSERT INTO historial_pasajero (
            id_pasajero,
            fecha_salida,
            id_reserva,
            id_vuelo,
            codigo_vuelo,
            aeropuerto_origen,
            aeropuerto_destino,
            fecha_llegada,
            estado_vuelo,
            fecha_reserva,
            estado_reserva,
            estado_pago
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)


    insert_manifiesto = session.prepare("""
        INSERT INTO manifiesto_vuelo (
            id_vuelo,
            numero_asiento,
            id_pasajero,
            nombre_pasajero,
            clase,
            estado_reserva,
            estado_pago
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """)


    update_counter = session.prepare("""
        UPDATE disponibilidad_asientos_por_vuelo
        SET disponibles = disponibles + ?,
            ocupados = ocupados + ?
        WHERE id_vuelo = ?
          AND clase = ?
    """)


    # ========================================================
    # PASAJEROS
    # ========================================================

    pasajeros = [
        {
            "id": uuid4(),
            "nombre": fake.name()
        }
        for _ in range(NUM_PASAJEROS)
    ]


    # ========================================================
    # AEROPUERTOS
    # ========================================================

    aeropuertos = [
        "GUA",
        "MIA",
        "JFK",
        "LAX",
        "MEX",
        "MAD",
    ]


    # ========================================================
    # ASIENTOS
    #
    # 45 económicos
    # 10 ejecutivos
    # 5 primera clase
    #
    # Se utilizan números de fila con dos dígitos
    # para que el orden ASC de Cassandra sea correcto.
    # ========================================================

    asientos = []

    # 45 económicos:
    # 01A - 08F, utilizando solamente los primeros 45
    for fila in range(1, 9):
        for letra in "ABCDEF":

            if len(
                [a for a in asientos if a["clase"] == "economica"]
            ) < 45:

                asientos.append({
                    "numero": f"{fila:02d}{letra}",
                    "clase": "economica"
                })


    # 10 ejecutivos:
    # 09A - 10D
    for fila in range(9, 11):
        for letra in "ABCDEF":

            if len(
                [a for a in asientos if a["clase"] == "ejecutiva"]
            ) < 10:

                asientos.append({
                    "numero": f"{fila:02d}{letra}",
                    "clase": "ejecutiva"
                })


    # 5 primera clase:
    # 11A - 11E
    for letra in "ABCDE":

        asientos.append({
            "numero": f"11{letra}",
            "clase": "primera"
        })


    assert len(asientos) == 60


    # ========================================================
    # VUELOS
    # ========================================================

    vuelos = []

    fecha_base = datetime(
        2026,
        9,
        1,
        8,
        0,
        0
    )


    for i in range(NUM_VUELOS):

        id_vuelo = uuid4()

        origen, destino = random.sample(
            aeropuertos,
            2
        )

        fecha_salida = fecha_base + timedelta(
            days=i // 10,
            hours=i % 10
        )

        fecha_llegada = fecha_salida + timedelta(
            hours=3
        )

        vuelos.append({
            "id": id_vuelo,
            "codigo": f"AV{i + 1:04d}",
            "origen": origen,
            "destino": destino,
            "salida": fecha_salida,
            "llegada": fecha_llegada,
        })


    # ========================================================
    # ESTRUCTURAS TEMPORALES PARA LA CARGA
    # ========================================================

    # Q2:
    # todas las reservas agrupadas por pasajero
    reservas_por_pasajero = defaultdict(list)

    # Q3:
    # reservas vigentes agrupadas por vuelo
    manifiesto_por_vuelo = defaultdict(list)

    # Q1:
    # conteo de ocupados por vuelo y clase
    ocupados_por_vuelo = defaultdict(
        lambda: {
            "economica": 0,
            "ejecutiva": 0,
            "primera": 0
        }
    )


    # ========================================================
    # GENERACIÓN DE RESERVAS
    # ========================================================

    total = 0

    for vuelo in vuelos:

        # Cada vuelo tendrá 50 pasajeros diferentes.
        pasajeros_del_vuelo = random.sample(
            pasajeros,
            RESERVAS_POR_VUELO
        )

        # Cada reserva recibe un asiento diferente.
        asientos_del_vuelo = random.sample(
            asientos,
            RESERVAS_POR_VUELO
        )


        for pasajero, asiento in zip(
            pasajeros_del_vuelo,
            asientos_del_vuelo
        ):

            id_reserva = uuid4()


            # ------------------------------------------------
            # Estado de reserva
            # ------------------------------------------------

            estado_reserva = random.choices(
                [
                    "confirmada",
                    "pendiente",
                    "cancelada"
                ],
                weights=[
                    70,
                    20,
                    10
                ],
                k=1
            )[0]


            # ------------------------------------------------
            # Estado de pago
            # ------------------------------------------------

            estado_pago = {
                "confirmada": "pagado",
                "pendiente": "pendiente",
                "cancelada": "reembolsado"
            }[estado_reserva]


            # ------------------------------------------------
            # Fecha de reserva
            # ------------------------------------------------

            fecha_reserva = (
                vuelo["salida"]
                - timedelta(
                    days=random.randint(1, 60)
                )
            )


            # ------------------------------------------------
            # Q2: historial del pasajero
            #
            # Se guardan TODAS las reservas,
            # incluidas las canceladas.
            # ------------------------------------------------

            reservas_por_pasajero[
                pasajero["id"]
            ].append(
                (
                    pasajero["id"],
                    vuelo["salida"],
                    id_reserva,
                    vuelo["id"],
                    vuelo["codigo"],
                    vuelo["origen"],
                    vuelo["destino"],
                    vuelo["llegada"],
                    "programado",
                    fecha_reserva,
                    estado_reserva,
                    estado_pago
                )
            )


            # ------------------------------------------------
            # Q3: manifiesto
            #
            # Solo CONFIRMADA y PENDIENTE.
            # CANCELADA no aparece.
            # ------------------------------------------------

            if estado_reserva in (
                "confirmada",
                "pendiente"
            ):

                manifiesto_por_vuelo[
                    vuelo["id"]
                ].append(
                    (
                        vuelo["id"],
                        asiento["numero"],
                        pasajero["id"],
                        pasajero["nombre"],
                        asiento["clase"],
                        estado_reserva,
                        estado_pago
                    )
                )


                # Q1:
                # CONFIRMADA y PENDIENTE ocupan un asiento.
                ocupados_por_vuelo[
                    vuelo["id"]
                ][
                    asiento["clase"]
                ] += 1


            total += 1


        # Mostrar avance cada 100 vuelos
        if (vuelos.index(vuelo) + 1) % 100 == 0:

            print(
                f"Generadas {total:,} reservas..."
            )


    print()
    print("Datos generados.")
    print(f"Reservas: {total:,}")
    print(f"Pasajeros: {NUM_PASAJEROS:,}")
    print(f"Vuelos: {NUM_VUELOS:,}")


    # ========================================================
    # CARGA Q2
    #
    # Un batch por pasajero.
    # Todos los INSERT pertenecen a la misma partición.
    # ========================================================

    print()
    print("Cargando historial de pasajeros...")


    pasajeros_procesados = 0

    for id_pasajero, reservas in reservas_por_pasajero.items():

        batch = BatchStatement(
            batch_type=BatchType.UNLOGGED
        )

        for reserva in reservas:

            batch.add(
                insert_historial,
                reserva
            )

        session.execute(batch)

        pasajeros_procesados += 1

        if pasajeros_procesados % 1000 == 0:

            print(
                f"Pasajeros procesados: "
                f"{pasajeros_procesados:,}"
            )


    # ========================================================
    # CARGA Q3
    #
    # Un batch por vuelo.
    # Todos los INSERT pertenecen a la misma partición.
    # ========================================================

    print()
    print("Cargando manifiestos de vuelos...")


    vuelos_procesados = 0

    for id_vuelo, registros in manifiesto_por_vuelo.items():

        batch = BatchStatement(
            batch_type=BatchType.UNLOGGED
        )

        for registro in registros:

            batch.add(
                insert_manifiesto,
                registro
            )

        session.execute(batch)

        vuelos_procesados += 1

        if vuelos_procesados % 100 == 0:

            print(
                f"Vuelos procesados: "
                f"{vuelos_procesados:,}"
            )


    # ========================================================
    # CARGA Q1
    #
    # Los tres counters de cada vuelo pertenecen
    # a la misma partición.
    # ========================================================

    print()
    print("Actualizando counters de disponibilidad...")


    for vuelo in vuelos:

        id_vuelo = vuelo["id"]

        batch = BatchStatement(
            batch_type=BatchType.UNLOGGED
        )


        capacidades = {
            "economica": 45,
            "ejecutiva": 10,
            "primera": 5
        }


        for clase, capacidad in capacidades.items():

            ocupados = ocupados_por_vuelo[
                id_vuelo
            ][clase]

            disponibles = capacidad - ocupados


            batch.add(
                update_counter,
                (
                    disponibles,
                    ocupados,
                    id_vuelo,
                    clase
                )
            )


        session.execute(batch)


    # ========================================================
    # FINAL
    # ========================================================

    print()
    print("======================================")
    print("Carga completada correctamente.")
    print("======================================")
    print(f"Reservas procesadas : {total:,}")
    print(f"Pasajeros generados  : {NUM_PASAJEROS:,}")
    print(f"Vuelos generados     : {NUM_VUELOS:,}")
    print("======================================")


finally:

    cluster.shutdown()