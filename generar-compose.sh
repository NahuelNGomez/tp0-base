#!/bin/bash

# Verifico que se pasaron dos argumentos
if [ "$#" -ne 2 ]; then
  echo "Usar: ./generar-compose.sh <archivo_salida> <cantidad_clientes>"
  exit 1
fi

# Asigno los argumentos a variables
archivo_salida=$1
cantidad_clientes=$2

# Ejecuto el script en Python para generar el archivo docker-compose
python3 generadorCompose.py $1 $2