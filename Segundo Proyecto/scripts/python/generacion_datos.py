import csv, random, uuid
from pathlib import Path
from datetime import date, datetime, time, timedelta
from faker import Faker

# Configuración Faker para datos en español y resultados reproducibles
fake = Faker("es_ES")
Faker.seed(42)
random.seed(42)

# Ubicación a guardar los archivos .csv
CARPETA_SCRIPT = Path(__file__).resolve().parent
CARPETA_CSV = CARPETA_SCRIPT / "csv"
CARPETA_CSV.mkdir(parents = True, exist_ok = True)

# Definir cantidad de registros a generar por entidad
CANTIDAD_USUARIOS = 500
CANTIDAD_RESTAURANTES = 200
CANTIDAD_CHEFS = 100
CANTIDAD_PLATILLOS = 50
CANTIDAD_TIPOS_COCINA = 15

# Rango de fechas disponibles a utilizar
FECHA_INICIO = date(2023, 1, 1)
FECHA_FIN = date(2026, 10, 10)
# Variable para llevar el control de los ID
CONTADOR_IDS = 0

# Catálogo de países
PAISES = ["Guatemala", "México", "España", "Colombia", "Argentina", "Perú", "Chile", "Costa Rica", "El Salvador", "Honduras", "Estados Unidos", "Italia", "Japón", "India", "China"]

# Catálogo de tipos de cocina
TIPOS_COCINA = [("Mexicana", "Platillos tradicionales con maíz, chiles y especias."),
    ("Italiana", "Pastas, pizzas y preparaciones mediterráneas."),
    ("Japonesa", "Sushi, ramen y preparaciones japonesas."),
    ("China", "Arroz, fideos, salteados y salsas."),
    ("India", "Preparaciones condimentadas con especias y curris."),
    ("Tailandesa", "Combinación de sabores dulces, ácidos y picantes."),
    ("Francesa", "Técnicas clásicas y preparaciones refinadas."),
    ("Española", "Tapas, arroces y recetas tradicionales españolas."),
    ("Mediterránea", "Verduras, aceite de oliva, pescados y cereales."),
    ("Árabe", "Legumbres, especias y panes tradicionales."),
    ("Peruana", "Ceviches, ajíes y recetas regionales peruanas."),
    ("Argentina", "Carnes asadas, empanadas y recetas tradicionales."),
    ("Vegetariana", "Preparaciones centradas en ingredientes vegetales."),
    ("Mariscos", "Platillos elaborados principalmente con productos del mar."),
    ("Fusión", "Combinación de técnicas de distintas cocinas.")]

# Catálogo de platillos
CATALOGO_PLATILLOS = [("Tacos al pastor", "Tortillas con carne adobada y piña."),
    ("Enchiladas", "Tortillas rellenas con salsa y acompañamientos."),
    ("Pozole", "Caldo tradicional con maíz y carne."),
    ("Chiles rellenos", "Chiles preparados con relleno y salsa."),
    ("Tamales", "Masa de maíz cocida en hojas."),
    ("Pizza margarita", "Pizza con tomate, mozzarella y albahaca."),
    ("Lasaña", "Capas de pasta con salsa y queso."),
    ("Risotto", "Arroz cremoso cocinado lentamente."),
    ("Ravioles", "Pasta rellena servida con salsa."),
    ("Espagueti a la boloñesa", "Pasta con salsa de carne y tomate."),
    ("Sushi de salmón", "Arroz y salmón preparados al estilo japonés."),
    ("Ramen", "Sopa japonesa con fideos y acompañamientos."),
    ("Tempura", "Ingredientes rebozados y fritos."),
    ("Yakitori", "Brochetas japonesas a la parrilla."),
    ("Gyozas", "Empanadillas rellenas cocidas o doradas."),
    ("Arroz frito", "Arroz salteado con verduras y otros ingredientes."),
    ("Pollo agridulce", "Pollo acompañado de salsa agridulce."),
    ("Dim sum", "Pequeñas preparaciones chinas variadas."),
    ("Pato pekinés", "Pato asado servido con acompañamientos."),
    ("Fideos chow mein", "Fideos salteados con verduras."),
    ("Pollo tikka masala", "Pollo con salsa especiada y cremosa."),
    ("Curry de verduras", "Verduras cocinadas con especias."),
    ("Samosas", "Empanadillas rellenas de verduras o carne."),
    ("Pollo tandoori", "Pollo marinado y cocinado con especias."),
    ("Pan naan", "Pan tradicional de textura suave."),
    ("Pad thai", "Fideos salteados con salsa y acompañamientos."),
    ("Tom yum", "Sopa tailandesa aromática y especiada."),
    ("Curry verde", "Curry tailandés con hierbas y especias."),
    ("Satay de pollo", "Brochetas acompañadas de salsa de cacahuate."),
    ("Arroz jazmín", "Arroz aromático de grano largo."),
    ("Quiche lorraine", "Tarta salada con huevo y otros ingredientes."),
    ("Ratatouille", "Guiso francés de verduras."),
    ("Coq au vin", "Pollo cocinado lentamente con vino."),
    ("Crème brûlée", "Postre de crema con capa caramelizada."),
    ("Croissant", "Pieza de bollería de masa laminada."),
    ("Paella", "Arroz preparado con diversos ingredientes."),
    ("Tortilla española", "Tortilla de huevo y patatas."),
    ("Gazpacho", "Sopa fría elaborada con verduras."),
    ("Patatas bravas", "Patatas servidas con salsa."),
    ("Churros", "Masa frita acompañada de azúcar."),
    ("Ceviche", "Pescado preparado con cítricos y condimentos."),
    ("Lomo saltado", "Carne salteada con verduras y patatas."),
    ("Ají de gallina", "Pollo desmenuzado con salsa cremosa."),
    ("Causa limeña", "Preparación fría de patata sazonada."),
    ("Anticuchos", "Brochetas de carne condimentada."),
    ("Asado argentino", "Carnes cocinadas a la parrilla."),
    ("Empanadas argentinas", "Masa rellena de carne u otros ingredientes."),
    ("Humita", "Preparación de maíz con condimentos."),
    ("Falafel", "Croquetas de legumbres y especias."),
    ("Hummus", "Crema de garbanzos con condimentos."),
    ("Ensalada mediterránea", "Ensalada de vegetales e ingredientes mediterráneos.")]

# Devuelve un ID para cada registro
def nuevo_id():
    global CONTADOR_IDS
    CONTADOR_IDS += 1
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"neo4j-restaurantes-{CONTADOR_IDS}"))

# Genera una fecha aleatoria (en formato YYYY-MM-DD) entre la FECHA_INICIO y FECHA_FIN
def fecha_aleatoria():
    dias_disponibles = (FECHA_FIN - FECHA_INICIO).days
    fecha = FECHA_INICIO + timedelta(days = random.randint(0, dias_disponibles))
    return fecha.isoformat()

# Genera una fecha-hora aleatoria (en formato YYYY-MM-DDTHH:MM:SS) entre la FECHA_INICIO y FECHA_FIN
def datetime_aleatorio():
    fecha = date.fromisoformat(fecha_aleatoria())
    hora = time(hour = random.randint(8, 22), minute = random.choice([0, 59]), second = 0)
    return datetime.combine(fecha, hora).isoformat(timespec="seconds")

# Seleccionar un número determinado de elementos de un catálogo sin repetir estos
def elegir_unicos(elementos, cantidad):
    return random.sample(list(elementos), min(cantidad, len(elementos)))

# Crea el archivo CSV y escribe los registros en este
def escribir_csv(nombre_archivo, columnas, registros):
    ruta = CARPETA_CSV / nombre_archivo
    with ruta.open("w", newline = "", encoding = "utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames = columnas, extrasaction = "ignore")
        escritor.writeheader()
        escritor.writerows(registros)
    print(f"Se generó el archivo: {nombre_archivo} - [{len(registros)} filas]")

# Comprueba que los catálogos cumplan las cantidades solicitadas
assert len(TIPOS_COCINA) == CANTIDAD_TIPOS_COCINA
assert len(CATALOGO_PLATILLOS) >= CANTIDAD_PLATILLOS
assert len({nombre for nombre, _ in TIPOS_COCINA}) == CANTIDAD_TIPOS_COCINA
assert len({nombre for nombre, _ in CATALOGO_PLATILLOS}) == len(CATALOGO_PLATILLOS)

# === NODOS ===

# NODOS USUARIOS: Generar los registros y crear el archivo .csv
usuarios = []
correos_generados = set()
for indice in range(CANTIDAD_USUARIOS):
    correo = f"usuario{indice + 1}@ejemplo.test"
    correos_generados.add(correo)
    usuarios.append({
        "id": nuevo_id(),
        "nombre": fake.name(),
        "email": correo,
        "edad": random.randint(18, 75),
        "pais": random.choice(PAISES)
    })
escribir_csv("usuarios.csv", ["id", "nombre", "email", "edad", "pais"], usuarios)

# NODOS RESTAURANTES: Generar los registros y crear el archivo .csv
restaurantes = []
probabilidad_reserva = {}
for indice in range(CANTIDAD_RESTAURANTES):
    precio_min = round(random.uniform(40, 250), 2)
    precio_max = round(random.uniform(precio_min + 0.01, 300), 2)
    if indice % 10 == 0:
        probabilidad_reserva[indice] = 0.85
    elif indice % 10 == 1:
        probabilidad_reserva[indice] = 0.25
    else:
        probabilidad_reserva[indice] = 0.55
    restaurantes.append({
        "id": nuevo_id(),
        "nombre": f"{fake.company()} Restaurante {indice + 1}",
        "anio_apertura": random.randint(1990, 2026),
        "precio_min_rango": precio_min,
        "precio_max_rango": precio_max,
        "descripcion": fake.sentence(nb_words = 12)
    })
escribir_csv("restaurantes.csv", ["id", "nombre", "anio_apertura", "precio_min_rango", "precio_max_rango", "descripcion" ], restaurantes)

# NODOS CHEFS: Generar los registros y crear el archivo .csv
chefs = []
for _ in range(CANTIDAD_CHEFS):
    nacimiento = fake.date_of_birth(minimum_age = 25, maximum_age = 70)
    chefs.append({
        "id": nuevo_id(),
        "nombre": fake.name(),
        "fecha_nacimiento": nacimiento.isoformat(),
        "nacionalidad": random.choice(PAISES)
    })
escribir_csv("chefs.csv", ["id", "nombre", "fecha_nacimiento", "nacionalidad"], chefs)

# NODOS PLATILLOS: Generar los registros y crear el archivo .csv
platillos = []
for nombre, descripcion in CATALOGO_PLATILLOS:
    platillos.append({
        "id": nuevo_id(),
        "nombre": nombre,
        "precio": round(random.uniform(35, 350), 2),
        "descripcion": descripcion
    })
escribir_csv("platillos.csv", ["id", "nombre", "precio", "descripcion"], platillos)

# NODOS TIPOS DE COCINA: Generar los registros y crear el archivo .csv
tipos_cocina = []
for nombre, descripcion in TIPOS_COCINA:
    tipos_cocina.append({
        "id": nuevo_id(),
        "nombre": nombre,
        "descripcion": descripcion
    })
escribir_csv("tipos_cocina.csv", ["id", "nombre", "descripcion"], tipos_cocina)

# === RELACIONES ===

# RELACIÓN VISITÓ: Usuario -[VISITÓ]-> Restaurante
visitas = []
restaurantes_visitados_por_usuario = {usuario["id"]: set() for usuario in usuarios}
visitas_por_restaurante = {restaurante["id"]: [] for restaurante in restaurantes}
for usuario in usuarios:
    cantidad_visitas = random.randint(4, 15)
    restaurantes_elegidos = elegir_unicos(restaurantes, cantidad_visitas)
    # Asigna y crea una relación por cada visita del usuario al restaurante
    for restaurante in restaurantes_elegidos:
        indice_restaurante = restaurantes.index(restaurante)
        con_reserva = (random.random() < probabilidad_reserva[indice_restaurante])
        punto_medio = (restaurante["precio_min_rango"] + restaurante["precio_max_rango"]) / 2
        if random.random() < 0.12:
            factor_consumo = random.choice([0.35, 0.5, 1.6, 2.0, 2.4])
        else:
            factor_consumo = random.uniform(0.75, 1.25)
        consumo = round(max(1, punto_medio * factor_consumo), 2)
        visita = {
            "id_visita": nuevo_id(),
            "usuario_id": usuario["id"],
            "restaurante_id": restaurante["id"],
            "fecha_visita": datetime_aleatorio(),
            "consumo": consumo,
            "con_reserva": str(con_reserva).lower(),
        }
        visitas.append(visita)
        restaurantes_visitados_por_usuario[usuario["id"]].add(restaurante["id"])
        visitas_por_restaurante[restaurante["id"]].append(visita)
escribir_csv("visito.csv", ["id_visita", "usuario_id", "restaurante_id", "fecha_visita", "consumo", "con_reserva"], visitas)

# RELACIÓN CALIFICÓ: Usuario -[CALIFICÓ]-> Restaurante
calificaciones = []
for usuario in usuarios:
    visitados = list(restaurantes_visitados_por_usuario[usuario["id"]])
    cantidad_calificaciones = min(random.randint(2, 8), len(visitados))
    restaurantes_calificados = elegir_unicos(visitados, cantidad_calificaciones)
    # Asigna y crea una relación por cada calificación del usuario a un restaurante
    for restaurante_id in restaurantes_calificados:
        puntuacion = random.choices([1, 2, 3, 4, 5], weights = [5, 10, 20, 35, 30], k = 1)[0]
        calificaciones.append({
            "usuario_id": usuario["id"],
            "restaurante_id": restaurante_id,
            "puntuacion": puntuacion,
            "fecha": fecha_aleatoria(),
            "comentario": random.choice([
                "La comida estuvo excelente.",
                "Buena atención y ambiente agradable.",
                "La experiencia fue aceptable.",
                "El precio podría mejorar.",
                "Me gustaría volver.",
                "El servicio fue más lento de lo esperado.",
                "Muy buena relación entre calidad y precio.",
                "Los platillos tenían buen sabor.",
            ]),
        })
escribir_csv("califico.csv", ["usuario_id", "restaurante_id", "puntuacion", "fecha", "comentario"], calificaciones)

# RELACIÓN ES_AMIGO_DE: Usuario -[ES_AMIGO_DE]-> Usuario
amistades = []
parejas_amistad = set()
for indice in range(len(usuarios) - 1):
    usuario_a = usuarios[indice]["id"]
    usuario_b = usuarios[indice + 1]["id"]
    pareja = tuple(sorted((usuario_a, usuario_b)))
    parejas_amistad.add(pareja)
for usuario in usuarios:
    cantidad_amigos = random.randint(3, 8)
    posibles_amigos = [otro for otro in usuarios if otro["id"] != usuario["id"]]
    for amigo in elegir_unicos(posibles_amigos, cantidad_amigos):
        pareja = tuple(sorted((usuario["id"], amigo["id"])))
        parejas_amistad.add(pareja)
for usuario_a, usuario_b in sorted(parejas_amistad):
    amistades.append({
        "usuario_id": usuario_a,
        "amigo_id": usuario_b,
        "fecha_amistad": fecha_aleatoria(),
    })
escribir_csv("es_amigo_de.csv", ["usuario_id", "amigo_id", "fecha_amistad"], amistades)

# RELACIÓN PERTENECE_A: Restaurante -[PERTENECE_A]-> TipoCocina
pertenencias = []
for restaurante in restaurantes:
    cocinas_asignadas = elegir_unicos(tipos_cocina, random.randint(1, 3))
    for cocina in cocinas_asignadas:
        pertenencias.append({"restaurante_id": restaurante["id"], "tipo_cocina_id": cocina["id"]})
escribir_csv("pertenece_a.csv", ["restaurante_id", "tipo_cocina_id"], pertenencias)

# RELACIÓN OFRECE: Restaurante -[OFRECE]-> Platillo
ofertas = []
parejas_oferta = set()
restaurantes_por_platillo = {platillo["id"]: set() for platillo in platillos}
# Asigna y crea una relación por cada platillo que ofrece el restaurante
for platillo in platillos:
    restaurantes_elegidos = elegir_unicos(restaurantes, 3)
    for restaurante in restaurantes_elegidos:
        pareja = (restaurante["id"], platillo["id"])
        if pareja not in parejas_oferta:
            parejas_oferta.add(pareja)
            restaurantes_por_platillo[platillo["id"]].add(restaurante["id"])
            ofertas.append({
                "restaurante_id": restaurante["id"],
                "platillo_id": platillo["id"],
                "precio": round(platillo["precio"] * random.uniform(0.9, 1.25), 2),
                "disponible": random.choices([True, False], weights = [90, 10], k = 1)[0]
            })
# Agregar más platillos a cada restaurante, que no estén en los ya pertenecientes
for restaurante in restaurantes:
    platillos_elegidos = elegir_unicos(platillos, random.randint(4, 10))
    for platillo in platillos_elegidos:
        pareja = (restaurante["id"], platillo["id"])
        if pareja not in parejas_oferta:
            parejas_oferta.add(pareja)
            restaurantes_por_platillo[platillo["id"]].add(restaurante["id"])
            ofertas.append({
                "restaurante_id": restaurante["id"],
                "platillo_id": platillo["id"],
                "precio": round(platillo["precio"] * random.uniform(0.9, 1.25), 2),
                "disponible": random.choices([True, False], weights = [90, 10], k = 1)[0]
            })
escribir_csv("ofrece.csv", ["restaurante_id", "platillo_id", "precio", "disponible"], ofertas)

# RELACIÓN PREPARA: Chef -[PREPARA]-> Platillo
preparaciones = []
parejas_preparacion = set()
# Asigna y crea una relación por cada platillo que prepara el chef
for chef in chefs:
    platillos_asignados = elegir_unicos(platillos, random.randint(2, 6))
    for platillo in platillos_asignados:
        pareja = (chef["id"], platillo["id"])
        # Evita duplicar la relación chef-platillo.
        if pareja not in parejas_preparacion:
            parejas_preparacion.add(pareja)
            preparaciones.append({
                "chef_id": chef["id"],
                "platillo_id": platillo["id"],
                "estilo": random.choice(["Tradicional", "Contemporáneo", "Fusión", "Casero", "Gourmet"]),
                "especialidad": random.choice(["Carnes", "Pescados y mariscos", "Pastas", "Postres", "Cocina regional", "Vegetales"])
            })
escribir_csv("prepara.csv", ["chef_id", "platillo_id", "estilo", "especialidad"], preparaciones)

# RELACIÓN TRABAJA_EN: Chef -[TRABAJA_EN]-> Restaurante
empleos = []
parejas_empleo = set()
# Asigna y crea una relación por cada restaurante en el que trabaja el chef
for chef in chefs:
    restaurantes_asignados = elegir_unicos(restaurantes, random.randint(1, 4))
    for restaurante in restaurantes_asignados:
        pareja = (chef["id"], restaurante["id"])
        # Evita duplicar la relación chef-restaurante
        if pareja not in parejas_empleo:
            parejas_empleo.add(pareja)
            empleos.append({
                "chef_id": chef["id"],
                "restaurante_id": restaurante["id"],
                "fecha_inicio": fecha_aleatoria(),
                "puesto": random.choice(["Chef ejecutivo", "Sous-chef", "Chef de partida", "Chef pastelero", "Chef de cocina"])
            })
escribir_csv("trabaja_en.csv", ["chef_id", "restaurante_id", "fecha_inicio", "puesto"], empleos)

# RELACIÓN LE_GUSTA: Usuario -[LE_GUSTA]-> TipoCocina
gustos = []
for usuario in usuarios:
    cocinas_preferidas = elegir_unicos(tipos_cocina, random.randint(2, 5))
    for cocina in cocinas_preferidas:
        gustos.append({
            "usuario_id": usuario["id"],
            "tipo_cocina_id": cocina["id"],
            "nivel_interes": random.randint(1, 5),
        })
escribir_csv("le_gusta.csv", ["usuario_id", "tipo_cocina_id", "nivel_interes"], gustos)

# VALIDACIONES

# Comprobar que se generó la cantidad mínima de nodos
assert len(usuarios) >= 500
assert len(restaurantes) >= 200
assert len(chefs) >= 100
assert len(platillos) >= 50
assert len(tipos_cocina) >= 15
# Comprobar que los platillos aparecen en al menos 3 restaurantes
assert all(len(ids_restaurantes) >= 3 for ids_restaurantes in restaurantes_por_platillo.values())
# Comprobar que las calificaciones están entre 1 y 5
assert all(1 <= int(registro["puntuacion"]) <= 5 for registro in calificaciones)
# Comprobar que los correos de los usuarios no se repiten
assert len(correos_generados) == len(usuarios)
# Comprueba que no se publique ninguna relación de OFRECE
assert len(parejas_oferta) == len(ofertas)
# Comprueba que la red contiene caminos de tres aristas
assert len(usuarios) >= 4
assert tuple(sorted((usuarios[0]["id"], usuarios[1]["id"]))) in parejas_amistad
assert tuple(sorted((usuarios[1]["id"], usuarios[2]["id"]))) in parejas_amistad
assert tuple(sorted((usuarios[2]["id"], usuarios[3]["id"]))) in parejas_amistad