import asyncio
import websockets

async def echo(websocket, path):
    # Print a message when a new connection is established
    print(f"New connection from {websocket.remote_address}")

    try:
        # Loop to handle messages received from the connection
        async for message in websocket:
            # Print the received message
            print(f"Received message: {message}")

            # Respond always with "true"
            response = "{\"verdict\": true}"

            # Send the response back to the client
            await websocket.send(response)
            print(f"Sent response: {response}")

    except websockets.exceptions.ConnectionClosed:
        # Handle connection closure
        print(f"Connection closed by {websocket.remote_address}")

# Start the WebSocket server
start_server = websockets.serve(echo, "localhost", 5052)

# Run the server in an infinite loop
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
