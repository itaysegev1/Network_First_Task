# Calculator Network Service

A distributed calculator service implementing a client-server architecture with a caching proxy. The system allows clients to send mathematical expressions to be evaluated on the server, with an optional caching layer for improved performance.

## Architecture

The system consists of three main components:

1. **Server**: Evaluates mathematical expressions and returns results
2. **Proxy**: Caches results and forwards requests to the server when needed
3. **Client**: Sends expression requests and displays results

### Protocol

The system uses a custom binary protocol for communication with the following features:
- Unix timestamp (32 bits)
- Total message length (16 bits)
- Control flags for caching and computation steps
- Status codes for responses
- Cache control parameters
- Variable-length data section

## Components

### Server (`server.py`)
- Listens for incoming TCP connections
- Parses and evaluates mathematical expressions
- Returns results with optional computation steps
- Supports multithreaded request handling
- Default port: 9999

### Proxy (`proxy.py`)
- Implements caching logic for computed results
- Forwards requests to server when cache miss occurs
- Handles cache staleness and expiration
- Supports concurrent client connections
- Default port: 9998

### Client (`client.py`)
- Constructs mathematical expressions
- Sends requests to proxy/server
- Displays results and computation steps
- Supports cache control parameters

### Calculator API (`calculator.py`)
Provides the core expression evaluation functionality:
- Support for basic arithmetic operations
- Mathematical functions (sin, cos, tan, etc.)
- Named constants (pi, e, tau)
- Expression tree evaluation
- Step-by-step computation tracking

## Usage

### Starting the Server
```bash
python server.py [-H HOST] [-p PORT]
```

### Starting the Proxy
```bash
python proxy.py [-ph PROXY_HOST] [-pp PROXY_PORT] [-sh SERVER_HOST] [-sp SERVER_PORT]
```

### Running the Client
```bash
python client.py [-H HOST] [-p PORT]
```

## Features

### Expression Support
- Basic arithmetic: +, -, *, /, %, **
- Functions: sin, cos, tan, sqrt, log, max, min, pow, rand
- Constants: π, τ, e
- Nested expressions and function calls

### Caching
- Configurable cache duration
- Client-side cache control
- Staleness checking
- Cache hit/miss reporting

### Computation Steps
- Optional step-by-step calculation display
- Full expression evaluation trace
- Parenthesized sub-expression results

## Protocol Details

### Header Format
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Unix Time Stamp                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Total Length         | Res.|C|S|T|    Status Code     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Cache Control         |            Padding              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             Data                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Status Codes
- 200: Success
- 400: Client Error
- 500: Server Error

## Example Usage

```python
# Create an expression: (sin(max(2, 3 * 4)) / 12) * 13
expr = mul_b(div_b(sin_f(max_f(2, mul_b(3, 4))), 12), 13)

# Send request with caching enabled
client((host, port), expr, show_steps=True, cache_result=True, cache_control=120)
```

## Error Handling

The system implements comprehensive error handling:
- Protocol parsing errors
- Expression evaluation errors
- Network communication errors
- Cache-related errors

## Dependencies

- Python 3.6+
- Standard library modules:
  - socket
  - threading
  - argparse
  - pickle
  - math
  - random
