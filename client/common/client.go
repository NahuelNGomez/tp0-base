package common

import (
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
		sendBets(c.config, c.conn)
		io.WriteString(c.conn, "EXIT"+c.config.ID+"\x00")
		c.conn.Close()

		c.createClientSocket()
		response := askForWinners(c.config, c.conn)

		if response == "FALTA\n" {
			log.Infof("action: receive_message | result: success | client_id: %v | message: %v", c.config.ID, response)
			c.conn.Close()
			for {
				time.Sleep(1 * time.Second)
				c.createClientSocket()
				response = askForWinners(c.config, c.conn)
				c.conn.Close()
				if response != "FALTA\n" {
					break
				}
			}
		} else {
			c.conn.Close()
		}
		amountWinners := parseResponse(response)
		log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", amountWinners)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
