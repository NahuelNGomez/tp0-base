package common

import (
	"bufio"
	"io"
	"net"
	"os"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type Bet struct {
	Name       string
	LastName   string
	DayOfBirth string
	Document   string
	Number     string
}

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
	MaxAmount     int
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop(channel chan os.Signal) {
	select {
	case sig := <-channel:
		log.Infof("action: signal_received | signal: %v | result: graceful_shutdown_initiated", sig)
		c.conn.Close()
		log.Infof("action: cleanup_resources | result: success")
		return

		// El caso normal para enviar mensajes y recibir respuestas
	default:
		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()

		// TODO: Modify the send to avoid short-write
		file, err := os.Open("agency.csv")
		if err != nil {
			log.Criticalf("action: open_file | result: fail | error: %v", err)
		}
		defer file.Close()

		reader := bufio.NewReader(file)

		for {
			stringBets := "UP"
			count := 0

			// Leer y preparar el paquete de apuestas
			for i := 0; i < c.config.MaxAmount; i++ {
				line, err := reader.ReadString('\n')
				if err != nil {
					if err == io.EOF {
						if len(line) > 0 {
							line = line[:len(line)-1]
							stringBets += c.config.ID + "," + line
							count++
						}
						break
					} else {
						log.Criticalf("action: read_line | result: fail | error: %v", err)
						return
					}
				}
				line = line[:len(line)-1]
				stringBets += c.config.ID + "," + line
				count++
				if i < c.config.MaxAmount-1 {
					stringBets += "\n"
				}
			}

			if count == 0 {
				break // No hay más apuestas que enviar
			}

			stringBets += "\x00"
			io.WriteString(c.conn, stringBets)

			msg, err := bufio.NewReader(c.conn).ReadString('\n') // Esperar confirmación
			if err != nil || msg != "1\n" {
				log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
					c.config.ID,
					err,
				)
				return
			}

			log.Infof("action: apuesta_enviada | result: success | batch: %v", count)
		}
		io.WriteString(c.conn, "exit"+"\x00")
		c.conn.Close()
		c.createClientSocket()

		text := "DOWN" + c.config.ID + "\x00"
		io.WriteString(c.conn, text)
		msg, err := bufio.NewReader(c.conn).ReadString('\n')
		if msg == "FALTA\n" {
			log.Infof("action: receive_message | result: success | client_id: %v | message: %v", c.config.ID, msg)
			c.conn.Close()
			for {
				c.createClientSocket()
				time.Sleep(1000)
				io.WriteString(c.conn, text)
				msg, err = bufio.NewReader(c.conn).ReadString('\n')
				c.conn.Close()
				if msg != "FALTA\n" {
					break
				}
			}
		} else {
			c.conn.Close()
		}
		log.Infof("action: receive_message | result: success | client_id: %v | message: %v", c.config.ID, msg)
		log.Infof("action: receive_message | result: success | client_id: %v | err: %v", c.config.ID, err)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
