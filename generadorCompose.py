import sys

# Verifico que se pasaron dos argumentos
if len(sys.argv) != 3:
    print("Uso: generadorCompose.py <archivo_salida> <cantidad_clientes>")
    sys.exit(1)

# Asigno los argumentos a variables
archivo_salida = sys.argv[1]
cantidad_clientes = int(sys.argv[2])

# Defino template del docker-compose
docker_compose_template = """
version: '3.8'
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    volumes:
      - ./server/config.ini:/config.ini
    networks:
      - testing_net
{clients}

networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""
# Genero la configuración para los clientes
clients = ""
for i in range(1, cantidad_clientes + 1):
    clients += f"""
  client{i}:
    container_name: client{i}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={i}
      - CLI_LOG_LEVEL=DEBUG
      - NOMBRE=NOMBRE{i}
      - APELLIDO=APELLIDO{i}
      - DOCUMENTO=DOCUMENTO{i}
      - NACIMIENTO={i}{i}{i}{i}-10-10
      - NUMERO={i}{i}{i}{i}
    volumes:
      - ./client/config.yaml:/config.yaml
      - ./.data/agency-{i}.csv:/agency.csv
    networks:
      - testing_net
    depends_on:
      - server"""

# Escribo el contenido al archivo de salida
with open(archivo_salida, "w") as f:
    f.write(docker_compose_template.format(clients=clients))

print(f"Archivo '{archivo_salida}' generado con {cantidad_clientes} clientes.")