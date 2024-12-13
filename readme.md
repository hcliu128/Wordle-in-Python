# Wordle Server Project

This project is a simple server implementation of the popular word-guessing game, Wordle. The server allows multiple clients to connect and play the game simultaneously. Each client is tasked with guessing a randomly selected word from a predefined dictionary.

## Features

- **Multithreading**: The server can handle multiple client connections at the same time.
- **Word Validation**: Ensures that guesses are valid English words and match the length of the target word.
- **Feedback System**: Provides feedback on each guess, indicating correct letters and their positions.
- **Graceful Shutdown**: The server can be shut down gracefully using a signal handler for `Ctrl+C`.

## How to Use

### Prerequisites

- Python 3.x
- A text file named `dictionary.txt` located in the `./utils/` directory, containing a list of valid words, one per line.

### Running the Server

1. **Start the Server**: Run the server script to start listening for client connections.

   ```bash
   python server.py
   ```

2. **Start the Client**: Run the client script
    ```bash
   python client.py
   ```

3. **Play!!!**

### Game Rules
- Each guess must be a valid English word of the same length as the target word.
- Feedback is provided for each guess:
    - <GREEN>: Correct letter and position.
    - <YELLOW>: Correct letter but wrong position.
    - <BLACK>: Incorrect letter.
- The game ends when the correct word is guessed or the client sends [GameOver].

