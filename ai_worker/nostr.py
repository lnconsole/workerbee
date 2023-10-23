import os
import ssl
import time
import random
import string
from nostr.relay_manager import RelayManager
from nostr.key import PrivateKey
from nostr.event import EventKind, EncryptedDirectMessage

sk = None
pk = None
relay_manager = None

def connect(nsec, relay):
    global relay_manager, sk, pk

    sk = PrivateKey.from_nsec(nsec)
    pk = sk.public_key

    relay_manager = RelayManager()
    relay_manager.add_relay(relay)
    time.sleep(1.25) # allow the connections to open

    return

def subscribe(filters):
    global relay_manager, sk

    subscription_id = gen_random_string()
    relay_manager.add_subscription_on_all_relays(subscription_id, filters)
    time.sleep(1.25) # allow the connections to open

    return

def publish_dm(pubkey, content):
    global sk, relay_manager

    dm = EncryptedDirectMessage(
        recipient_pubkey=pubkey,
        cleartext_content=content
    )
    sk.sign_event(dm)
    relay_manager.publish_event(dm)

    return

async def get_dm(sender_pk):
    global relay_manager, sk
    while True:
        event_msg = await relay_manager.message_pool.get_event()
        print("got event: ", event_msg.event)
        if event_msg.event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE and event_msg.event.public_key == sender_pk:
            dm = sk.decrypt_message(
                encoded_message=event_msg.event.content, 
                public_key_hex=sender_pk
            )
            return dm

def gen_random_string():
    return ''.join(random.choice(string.ascii_letters) for i in range(10))
