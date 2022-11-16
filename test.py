#!/usr/bin/env python

import asyncio
import websockets
import random

async def client_program():
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        greeting = await websocket.recv()
        print(greeting)

        name = input("What is your name? ")
        await websocket.send(name)

        actions = ["crunching numbers", "database inserts", 
                   "vlookups in excel", "deleting stuff", 
                   "formatting disk", "looking for aliens", 
                   "buying and selling bitcoin", "disconnect"]

        probability_of_occurring = [0.3, 0.2, 0.2, 0.1, 0.05, 0.05, 0.05, 0.05]

        try:
            while True:
                # pick a new action and take up to 3 seconds to carefully think about it
                await asyncio.sleep(random.randint(0, 3))
                action = random.choices(actions, probability_of_occurring)[0]

                print(f"(client) The server is going to preform: {action}")
                await websocket.send(action)

                response = await websocket.recv()
                print(f"(client) Response from server: {response}")
        except websockets.exceptions.ConnectionClosedOK:
                print(f"(client) Disconnected from server")
                
                
#The client program works as follows:

#It connects to the servers websocket using the uri
#The client will wait for a message from the server and print it to the console
#You are asked to type in your name
#Your name is send to the server
#1 of 8 actions is picked at random, one of them is disconnect
#This action is send to the server
#The client will wait for a response from the server and print it to the console
#Go back to step 5 until the server disconnects