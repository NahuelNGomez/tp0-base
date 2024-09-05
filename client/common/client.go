package common

import (
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
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	bet    Bet
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, newBet Bet) *Client {
	client := &Client{
		config: config,
		bet:    newBet,
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
	default:
		c.createClientSocket()
		sendBets(c.config, c.bet, c.conn)
		c.conn.Close()
	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
