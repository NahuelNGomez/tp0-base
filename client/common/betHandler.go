package common

import (
	"bufio"
	"fmt"
	"io"
	"net"
)

func sendBets(config ClientConfig, bet Bet, conn net.Conn) {
	io.WriteString(conn, fmt.Sprintf("%s,%s,%s,%s,%s,%s\x00", config.ID, bet.Name, bet.LastName, bet.Document, bet.DayOfBirth, bet.Number))
	msg, err := bufio.NewReader(conn).ReadString('\n') // Leo hasta el salto de línea

	if err == nil || msg != "1\n" {
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v", bet.Document, bet.Number)
	} else {
		log.Infof("action: apuesta_enviada | result: fail | dni: %v | numero: %v", bet.Document, bet.Number)
	}

}
