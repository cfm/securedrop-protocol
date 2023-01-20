import pki
import requests
import sys
import ecdsa
import json
import nacl.secret
from base64 import b64decode, b64encode
from hashlib import sha3_256
from os import mkdir, listdir
from ecdsa import SigningKey, VerifyingKey, ECDH
from time import time

from commons import *

def add_ephemeral_keys(journalist_key, journalist_id, journalist_uid):
	ephemeral_keys = []
	for key in range(ONETIMEKEYS):
		ephemeral_sig, ephemeral_key = pki.generate_ephemeral(journalist_key, journalist_id, journalist_uid)		
		ephemeral_keys.append({"ephemeral_key": b64encode(ephemeral_key.verifying_key.to_string()).decode("ascii"),
							   "ephemeral_sig": b64encode(ephemeral_sig).decode("ascii")})

	response = requests.post(f"http://{SERVER}/ephemeral_keys", json={"journalist_uid": journalist_uid,
																	  "ephemeral_keys": ephemeral_keys})
# Load the journalist ephemeral keys from the journalist key dirrectory.
# On an actual implementation this would more likely be a sqlite (or sqlcipher)
# database.
def load_ephemeral_keys(journalist_key, journalist_id, journalist_uid):
	ephemeral_keys = []
	key_file_list = listdir(f"{DIR}journalists/{journalist_uid}/")
	for file_name in key_file_list:
		if file_name.endswith('.key'):
			with open(f"{DIR}journalists/{journalist_uid}/{file_name}", "rb") as f:
				key = f.read()
			ephemeral_keys.append(SigningKey.from_pem(key))
	return ephemeral_keys

# Try all the ephemeral keys to build an encryption shared secret to decrypt a message.
# This is inefficient, but on an actual implementation we would discard already used keys
def decrypt_messages(ephemeral_keys, messages_list):
	plaintexts = []
	for message in messages_list:
		for ephemeral_key in ephemeral_keys:
			message_plaintext = decrypt_message_ciphertext(ephemeral_key, message["message_public_key"], message["message_ciphertext"])
			if message_plaintext:
				plaintexts.append(message_plaintext)
				break
	if len(plaintexts) > 0:
		return plaintexts
	else:
		return False

def journalist_reply(message, reply, journalist_uid):
	# This function builds the per-message keys and returns a nacl encrypting box
	message_public_key, message_challenge, box = build_message(message["source_challenge_public_key"], message["source_encryption_public_key"])

	# The actual message struct varies depending on the sending party.
	# Still it is client controlled, so in each client we shall watch out a bit.
	message_dict = {"message": reply,
					# do we want to sign messages? how do we attest source authoriship?
					"sender": journalist_uid,
					"receiver": "source_id_placeholder",
					# we could list the journalists involved in the conversation here
					# if the source choose not to pick everybody
					"group_members": [],
					"timestamp": int(time()),
					# we can add attachmenet pieces/id here
					"attachments": [],
					# and respective keys
					"attachments_keys": [],
				   }

	message_ciphertext = b64encode(box.encrypt((json.dumps(message_dict)).ljust(1024).encode('ascii'))).decode("ascii")

	# Send the message to the server API using the generic /send endpoint
	send_message(message_ciphertext, message_public_key, message_challenge)

def main():
	# Get and check the journalist number we are impersonating
	assert(len(sys.argv) == 2)
	journalist_id = int(sys.argv[1])
	assert(journalist_id >= 0 and journalist_id < JOURNALISTS)
	journalist_sig, journalist_key = pki.load_and_verify_journalist_keypair(journalist_id)
	journalist_uid = add_journalist(journalist_key, journalist_sig)

	# Generate and upload a bunch (30) of ephemeral keys
	add_ephemeral_keys(journalist_key, journalist_id, journalist_uid)

	# Check if there are messages
	messages_list = fetch_messages(journalist_key)

	# Delete those messages
	#delete_messages()

	if messages_list:
		# Load all the ephemeral keys back
		ephemeral_keys = load_ephemeral_keys(journalist_key, journalist_id, journalist_uid)

		# Try to decrypt with the loaded ephemeral keys
		plaintext_messages = decrypt_messages(ephemeral_keys, messages_list)

		# Print the plaintext messages
		print("[+] Got submissions :)")
		for plaintext_message in plaintext_messages:
			#print(plaintext_message)
			print("---BEGIN SUBMISSION---")
			print(f"\t\tMessage: {plaintext_message['message']}")
			print(f"\t\tTimestamp: {plaintext_message['timestamp']}")
			print(f"\t\tSource Public Key (encryption): {plaintext_message['source_encryption_public_key']}")
			print("---END SUBMISSION---")

			# Send a reply to each message for demo purposes
			journalist_reply(plaintext_message, "message reply :)", journalist_uid)

main()