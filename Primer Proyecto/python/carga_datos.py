from collections import defaultdict
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, BatchType
from faker import Faker
from uuid import uuid4
from datetime import datetime, timedelta
from decimal import Decimal
import random

# CONFIGURACIÓN
NUM_RESERVAS = 100_000
NUM_PASAJEROS = 10_000
NUM_VUELOS = 2_000

# 100,000 / 2,000 = 50 reservas por vuelo
RESERVAS_POR_VUELO = NUM_RESERVAS // NUM_VUELOS

SEED = 42


fake = Faker("es_ES")
random.seed(SEED)
Faker.seed(SEED)


# CONEXIÓN A CASSANDRA
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

    # --------------------------------------------------------
    # Q2 - Historial del pasajero
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Q3 - Manifiesto del vuelo
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Q1 - Disponibilidad de asientos
    # --------------------------------------------------------

    update_counter = session.prepare("""
        UPDATE disponibilidad_asientos_por_vuelo
        SET disponibles = disponibles + ?,
            ocupados = ocupados + ?
        WHERE id_vuelo = ?
          AND clase = ?
    """)


    # --------------------------------------------------------
    # Q4 - Porcentaje de ocupación
    # --------------------------------------------------------

    insert_ocupacion = session.prepare("""
        INSERT INTO ocupacion_por_ruta_mes (
            aeropuerto_origen,
            aeropuerto_destino,
            mes,
            fecha_salida,
            id_vuelo,
            codigo_vuelo,
            capacidad_max,
            porcentaje_ocupacion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """)


    # --------------------------------------------------------
    # Q4 - Reservas confirmadas
    # --------------------------------------------------------

    update_reservas_confirmadas = session.prepare("""
        UPDATE reservas_confirmadas_por_vuelo
        SET reservas_confirmadas = reservas_confirmadas + ?
        WHERE id_vuelo = ?
    """)


    # --------------------------------------------------------
    # Q5 - Top de ingresos
    # --------------------------------------------------------

    insert_top_ingresos = session.prepare("""
        INSERT INTO top_ingresos_por_vuelo (
            mes,
            monto_total,
            id_vuelo,
            codigo_vuelo
        )
        VALUES (?, ?, ?, ?)
    """)


    # --------------------------------------------------------
    # Q5 - Ingresos acumulados
    #
    # Se almacena el ingreso en CENTAVOS porque Cassandra
    # COUNTER trabaja con valores enteros.
    # --------------------------------------------------------

    update_ingresos_acumulados = session.prepare("""
        UPDATE ingresos_acumulados_por_vuelo
        SET monto_total = monto_total + ?
        WHERE id_vuelo = ?
          AND mes = ?
    """)


    # ========================================================
    # PASAJEROS
    # ========================================================

    print("Generando pasajeros...")

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
        "MAD"
    ]


    # ========================================================
    # ASIENTOS
    #
    # 45 económicos
    # 10 ejecutivos
    # 5 primera clase
    #
    # TOTAL = 60
    # ========================================================

    asientos = []

    # --------------------------------------------------------
    # 45 económicos
    # --------------------------------------------------------

    for fila in range(1, 9):

        for letra in "ABCDEF":

            if len(
                [a for a in asientos if a["clase"] == "economica"]
            ) < 45:

                asientos.append({
                    "numero": f"{fila:02d}{letra}",
                    "clase": "economica"
                })


    # --------------------------------------------------------
    # 10 ejecutivos
    # --------------------------------------------------------

    for fila in range(9, 11):

        for letra in "ABCDEF":

            if len(
                [a for a in asientos if a["clase"] == "ejecutiva"]
            ) < 10:

                asientos.append({
                    "numero": f"{fila:02d}{letra}",
                    "clase": "ejecutiva"
                })


    # --------------------------------------------------------
    # 5 primera clase
    # --------------------------------------------------------

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

    # Se utiliza un solo año para que el bucket "mes"
    # no mezcle meses de años diferentes.
    fecha_base = datetime(
        2026,
        1,
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
            "llegada": fecha_llegada
        })


    # ========================================================
    # ESTRUCTURAS TEMPORALES
    # ========================================================

    # Q2
    reservas_por_pasajero = defaultdict(list)

    # Q3
    manifiesto_por_vuelo = defaultdict(list)

    # Q1
    ocupados_por_vuelo = defaultdict(
        lambda: {
            "economica": 0,
            "ejecutiva": 0,
            "primera": 0
        }
    )

    # Q4
    reservas_confirmadas_por_vuelo = defaultdict(int)

    # Q5
    ingresos_por_vuelo = defaultdict(int)


    # ========================================================
    # PRECIOS POR CLASE
    #
    # Los valores están expresados en centavos.
    #
    # Económica  = $150.00
    # Ejecutiva  = $350.00
    # Primera    = $700.00
    # ========================================================

    precios_centavos = {
        "economica": 15000,
        "ejecutiva": 35000,
        "primera": 70000
    }


    # ========================================================
    # GENERACIÓN DE RESERVAS
    # ========================================================

    total = 0

    print()
    print("Generando reservas...")


    for indice_vuelo, vuelo in enumerate(vuelos):

        # Cada vuelo tendrá 50 pasajeros diferentes
        pasajeros_del_vuelo = random.sample(
            pasajeros,
            RESERVAS_POR_VUELO
        )

        # Cada reserva recibe un asiento diferente
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
            # Q2
            # Historial del pasajero
            #
            # Se guardan todas las reservas.
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
            # Q3
            # Manifiesto
            #
            # Solo confirmadas y pendientes.
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


                # Q1
                # Confirmadas y pendientes ocupan asiento.

                ocupados_por_vuelo[
                    vuelo["id"]
                ][
                    asiento["clase"]
                ] += 1


            # ------------------------------------------------
            # Q4
            # Reservas confirmadas
            # ------------------------------------------------

            if estado_reserva == "confirmada":

                reservas_confirmadas_por_vuelo[
                    vuelo["id"]
                ] += 1


                # ------------------------------------------------
                # Q5
                # Ingreso de pagos confirmados
                # ------------------------------------------------

                ingresos_por_vuelo[
                    vuelo["id"]
                ] += precios_centavos[
                    asiento["clase"]
                ]


            total += 1


        # Mostrar avance cada 100 vuelos

        if (indice_vuelo + 1) % 100 == 0:

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
    # CARGA Q4
    # ========================================================

    print()
    print("Cargando datos de ocupación Q4...")


    for indice_vuelo, vuelo in enumerate(vuelos):

        id_vuelo = vuelo["id"]

        mes = vuelo["salida"].month

        capacidad_max = len(asientos)

        ocupados = sum(
            ocupados_por_vuelo[id_vuelo].values()
        )

        porcentaje_ocupacion = (
            Decimal(ocupados) /
            Decimal(capacidad_max)
        ) * Decimal("100")


        # ----------------------------------------------------
        # Tabla principal Q4
        # ----------------------------------------------------

        session.execute(
            insert_ocupacion,
            (
                vuelo["origen"],
                vuelo["destino"],
                mes,
                vuelo["salida"],
                id_vuelo,
                vuelo["codigo"],
                capacidad_max,
                porcentaje_ocupacion
            )
        )


        # ----------------------------------------------------
        # Tabla auxiliar Q4
        # ----------------------------------------------------

        reservas_confirmadas = (
            reservas_confirmadas_por_vuelo[
                id_vuelo
            ]
        )


        session.execute(
            update_reservas_confirmadas,
            (
                reservas_confirmadas,
                id_vuelo
            )
        )


        if (indice_vuelo + 1) % 100 == 0:

            print(
                f"Vuelos Q4 procesados: "
                f"{indice_vuelo + 1:,}"
            )


    # ========================================================
    # CARGA Q5
    # ========================================================

    print()
    print("Cargando datos de ingresos Q5...")


    for indice_vuelo, vuelo in enumerate(vuelos):

        id_vuelo = vuelo["id"]

        mes = vuelo["salida"].month

        ingreso_centavos = ingresos_por_vuelo[
            id_vuelo
        ]


        # ----------------------------------------------------
        # Tabla auxiliar Q5
        #
        # Guarda el ingreso como COUNTER en centavos.
        # ----------------------------------------------------

        session.execute(
            update_ingresos_acumulados,
            (
                ingreso_centavos,
                id_vuelo,
                mes
            )
        )


        # ----------------------------------------------------
        # Tabla principal Q5
        #
        # Convertimos centavos a dólares.
        # ----------------------------------------------------

        monto_total = (
            Decimal(ingreso_centavos)
            / Decimal("100")
        )


        session.execute(
            insert_top_ingresos,
            (
                mes,
                monto_total,
                id_vuelo,
                vuelo["codigo"]
            )
        )


        if (indice_vuelo + 1) % 100 == 0:

            print(
                f"Vuelos Q5 procesados: "
                f"{indice_vuelo + 1:,}"
            )


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
    print("Q1 - Disponibilidad  : OK")
    print("Q2 - Historial       : OK")
    print("Q3 - Manifiestos     : OK")
    print("Q4 - Ocupación       : OK")
    print("Q5 - Ingresos        : OK")
    print("======================================")


finally:

    cluster.shutdown()