# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from signal import SIGINT, SIGTERM
import asyncio
from dotenv import load_dotenv
import logging
import sys
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
import os
import platform

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Set websockets logger to WARNING to reduce noise
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

# Load and validate API key
load_dotenv('.env')
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

if not DEEPGRAM_API_KEY:
    logger.error("DEEPGRAM_API_KEY not found in environment variables")
    sys.exit(1)

# We will collect the is_final=true messages here
is_finals = []

async def main():
    try:
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram = DeepgramClient(DEEPGRAM_API_KEY, config)
        
        dg_connection = deepgram.listen.asyncwebsocket.v("1")

        async def on_message(self, result, **kwargs):
            try:
                if hasattr(result, 'channel') and hasattr(result.channel, 'alternatives'):
                    sentence = result.channel.alternatives[0].transcript
                    if sentence.strip():
                        if result.is_final:
                            logger.info(f"\n=== Final ===\n{sentence}")
                        else:
                            logger.info(f"\n=== Interim ===\n{sentence}")
            except Exception as e:
                logger.error(f"Error in message handler: {e}")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True
        )

        logger.info("Connecting to Deepgram...")
        await dg_connection.start(options)
        
        logger.info("Initializing microphone...")
        microphone = Microphone(dg_connection.send)
        microphone.start()
        logger.info("Microphone started successfully")

        # Simple way to keep the connection alive
        try:
            while True:
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            microphone.finish()
            await dg_connection.finish()

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass