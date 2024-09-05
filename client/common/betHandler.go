package common

import (
	"bufio"
	"io"
	"net"
	"os"
)

func sendBets(config ClientConfig, conn net.Conn) {
	file, err := os.Open("agency.csv")
	if err != nil {
		log.Criticalf("action: open_file | result: fail | error: %v", err)
	}
	defer file.Close()
	reader := bufio.NewReader(file)
	for {
		stringBets := ""
		count := 0

		// Leer y preparar el paquete de apuestas
		for i := 0; i < config.MaxAmount; i++ {
			line, err := reader.ReadString('\n')
			if err != nil {
				if err == io.EOF {
					if len(line) > 0 {
						line = line[:len(line)-1]
						stringBets += config.ID + "," + line
						count++
					}
					break
				} else {
					log.Criticalf("action: read_line | result: fail | error: %v", err)
					return
				}
			}
			line = line[:len(line)-1]
			stringBets += config.ID + "," + line
			count++
			if i < config.MaxAmount-1 {
				stringBets += "\n"
			}
		}

		if count == 0 {
			break // No hay más apuestas que enviar
		}

		stringBets += "\x00"
		io.WriteString(conn, stringBets)

		msg, err := bufio.NewReader(conn).ReadString('\n') // Esperar confirmación
		if err != nil || msg != "1\n" {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				config.ID,
				err,
			)
			return
		}

		log.Infof("action: apuesta_enviada | result: success | batch: %v", count)

	}
}
