# securedrop-poc
## Installation (Qubes)
Install dependencies and create the virtual environment.
```
sudo dnf install redis
sudo systemctl start redis
python3 -m virtualenv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

Generate the FPF root key, the intermediate key, and the journalists long term keys and sign them all hierarchically.
```
python3 pki.py
```

Run the server:
```
FLASK_DEBUG=1 flask --app server run
```

Impersonate the journalists and generate ephemeral keys for each of them. Upload all the public keys and their signature to the server.
```
for i in $(seq 0 9); do python3 journalist.py -j $i -a upload_keys; done;
```

_Following CLI refactoring instructions need a refactor as well_

### Source
#### Help

```
# python3 source.py -h
usage: source.py [-h] [-p PASSPHRASE] -a {fetch,read,reply,submit,delete} [-i ID] [-m MESSAGE] [-f FILES [FILES ...]]

options:
  -h, --help            show this help message and exit
  -p PASSPHRASE, --passphrase PASSPHRASE
                        Source passphrase if returning
  -a {fetch,read,reply,submit,delete}, --action {fetch,read,reply,submit,delete}
                        Action to perform
  -i ID, --id ID        Message id
  -m MESSAGE, --message MESSAGE
                        Plaintext message content for submissions or replies
  -f FILES [FILES ...], --files FILES [FILES ...]
                        List of local files to submit

```

#### Send a submission (without attachments)
```
# python3 source.py -a submit -m "My first contact message with a newsroom :)"
[+] New submission passphrase: 23a90f6499c5f3bc630e7103a4e63c131a8248c1ae5223541660b7bcbda8b2a9

```
#### Send a submission (with attachments)
```
# python3 source.py -a submit -m "My first contact message with a newsroom with collected evidences and a supporting video :)" -f /tmp/secret_files/file1.mkv /tmp/secret_files/file2.zip 
[+] New submission passphrase: c2cf422563cd2dc2813150faf2f40cf6c2032e3be6d57d1cd4737c70925743f6

```
#### Fetch replies

```
# python3 source.py -p 23a90f6499c5f3bc630e7103a4e63c131a8248c1ae5223541660b7bcbda8b2a9 -a fetch
[+] Found 1 message(s)
    de55e92ca3d89de37855cea52e77c182111ca3fd00cf623a11c1f41ceb2a19ca

```

#### Read a reply

```
# python3 source.py -p 23a90f6499c5f3bc630e7103a4e63c131a8248c1ae5223541660b7bcbda8b2a9 -a read -i de55e92ca3d89de37855cea52e77c182111ca3fd00cf623a11c1f41ceb2a19ca
[+] Successfully decrypted message de55e92ca3d89de37855cea52e77c182111ca3fd00cf623a11c1f41ceb2a19ca

    ID: de55e92ca3d89de37855cea52e77c182111ca3fd00cf623a11c1f41ceb2a19ca
    From: a1eb055608e169d04392607a79a3bf8ac4ccfc9e0d3f5056941f31be78a12be1
    Date: 2023-01-23 23:42:14
    Text: This is a reply to the message without attachments, it is identified only by the id

```

#### Send an additional reply

```
# python3 source.py -p 23a90f6499c5f3bc630e7103a4e63c131a8248c1ae5223541660b7bcbda8b2a9 -a reply -i de55e92ca3d89de37855cea52e77c182111ca3fd00cf623a11c1f41ceb2a19ca -m "This is a second source to journalist reply"
```

#### Delete a message

```
# python3 source.py -p 23a90f6499c5f3bc630e7103a4e63c131a8248c1ae5223541660b7bcbda8b2a9 -a delete -i de55e92ca3d89de37855cea52e77c182111ca3fd00cf623a11c1f41ceb2a19ca
[+] Message de55e92ca3d89de37855cea52e77c182111ca3fd00cf623a11c1f41ceb2a19ca deleted

```

### Journalist
#### Help
```
# python3 journalist.py -h
usage: journalist.py [-h] -j [0, 9] [-a {upload_keys,fetch,read,reply,delete}] [-i ID] [-m MESSAGE]

options:
  -h, --help            show this help message and exit
  -j [0, 9], --journalist [0, 9]
                        Journalist number
  -a {upload_keys,fetch,read,reply,delete}, --action {upload_keys,fetch,read,reply,delete}
                        Action to perform
  -i ID, --id ID        Message id
  -m MESSAGE, --message MESSAGE
                        Plaintext message content for replies

```
#### Fetch replies and submissions

```
# python3 journalist.py -j 7 -a fetch
[+] Found 2 message(s)
    0358306e106d1d9e0449e8e35a59c37c41b28a5e6630b88360738f5989da501c
    1216789eab54869259e168b02825151b665f04b0b9f01f654c913e3bbea1f627

```

#### Read a submission/reply (without attachments)

```
# python3 journalist.py -j 7 -a read -i 1216789eab54869259e168b02825151b665f04b0b9f01f654c913e3bbea1f627
[+] Successfully decrypted message 1216789eab54869259e168b02825151b665f04b0b9f01f654c913e3bbea1f627

    ID: 1216789eab54869259e168b02825151b665f04b0b9f01f654c913e3bbea1f627
    Date: 2023-01-23 23:37:15
    Text: My first contact message with a newsroom :)

```

#### Read a submission/reply (with attachments)

```
# python3 journalist.py -j 7 -a read -i 0358306e106d1d9e0449e8e35a59c37c41b28a5e6630b88360738f5989da501c
[+] Successfully decrypted message 0358306e106d1d9e0449e8e35a59c37c41b28a5e6630b88360738f5989da501c

    ID: 0358306e106d1d9e0449e8e35a59c37c41b28a5e6630b88360738f5989da501c
    Date: 2023-01-23 23:38:27
    Attachment: name=file1.mkv;size=1562624;parts_count=3
    Attachment: name=file2.zip;size=93849;parts_count=1
    Text: My first contact message with a newsroom with collected evidences and a supporting video :)

```

#### Send a reply

```
# python3 journalist.py -j 7 -a reply -i 1216789eab54869259e168b02825151b665f04b0b9f01f654c913e3bbea1f627 -m "This is a reply to the message without attachments, it is identified only by the id"
```

#### Delete a message

```
python3 journalist.py -j 7 -a delete -i 1216789eab54869259e168b02825151b665f04b0b9f01f654c913e3bbea1f627
[+] Message 1216789eab54869259e168b02825151b665f04b0b9f01f654c913e3bbea1f627 deleted

```

## Parties
  * **Source**: A source is someone who wants to leak a document. A source is unknown prior its first contact. A source may want to send a text message and/or add attachments. The anonymity and safety of the source is vital. The source must use Tor Browser to preserve their anonymity and no persistance shall be required. The highest degree of deniability a source has, the better.
  * **Journalist(s)**: Journalists are those designated to receive, check and reply to submissions. Journalists are known, or at least the newsroom they work for is known and trusted. Journalists are expected to use the Securedrop Workstation with an ad-hoc client, which has dedicated encrypted storage.
  * **Newsroom**: A newsroom is the entity responsible or at least with formal ownership of a Securedrop instance. The newsroom is trusted, and is expected to publish their Securedrop instance somewhere, their tips page, their social media channel or wherever they want the necessary outreach. In the traditional model, newsroom are also technically in charge of their own server instances and of journalist enrollment.
  * **FPF**: FPF is the entity responsible for maintaining and developing Securedrop. FPF can offer additional services, such as dedicated support. FPF has already a leading role, in the context that, while the project is open source, releases and Onion Lists for Tor Browser are signed with FPF keys. However, the full stack must remain completely usable without any FPF involvement or knowledge.

## Notions
  * **Keys**: When referring to keys, either symmetric or asymmetric, depending on the context, the key storage backend (ie: the media device) may eventually vary. Especially long term keys can be stored on Hardware Security Modules or Smart Cards, and signing keys might also be a combination of multiple keys with specialy requirements (ie: 3 out of 5 signers)
  * **Server**: For this project a server might be a physical dedicated server housed in a trusted location, a physical server in an untrusted location, or a virtual server in a trusted or untrusted context. Besides the initial setup, all the connection to the server have to happen though the Tor Hidden Service Protocol. However, we can expect that a powerful attacker can find the server location and provider (through financial records, legal orders, deanonymization attacks, logs of the setup phase).

## Threat model

## Keys summary
 * **FPF**:
     * *FPF<sub>SK</sub>*: Long term FPF signing private key
     * *FPF<sub>PK</sub>*: Long term FPF signing public key
 * **Newsroom**:
     * *NR<sub>SK</sub>*: Long term Newsroom signing private key
     * *NR<sub>PK</sub>*: Long term Newsroom signing public key
 * **Journalists**:
     * *J<sub>SK</sub>*: Long term Journalist signing private key
     * *J<sub>PK</sub>*: Long term Journalist signing public key
     * *JC<sub>SK</sub>*: Long term Journalist zero-knowledge private key
     * *JC<sub>PK</sub>*: Long term Journalist zero-knowledge public key
     * *JE<sub>SK</sub>*: Ephemeral (per-message) key agreement private key
     * *JE<sub>PK</sub>*: Ephemeral (per-message) key agreement public key
 * **Sources**:
     * *PW*: Secret passphrase
     * *S<sub>SK</sub>*: Long term Source key agreement private key
     * *S<sub>PK</sub>*: Long term Source key agreement public key
     * *SC<sub>SK</sub>*: Long term Source zero-knowledge private key
     * *SC<sub>PK</sub>*: Long term Source zero-knowledge public key
 * **Messages**:
     * *ME<sub>SK</sub>*: Ephemeral per-message key agreement private key
     * *ME<sub>PK</sub>*: Ephemeral per-message key agreement public key
 * **Server**:
     * *DE<sub>PK</sub>*: Per-request, ephemeral decoy public key

## Functions
| Formula | Description |
|---|---|
| *c = E(k, m)* | Encrypt message *m* to ciphertext *c* using symmetric key *k* |
| *m = D(k, c)* | Decrypt ciphertext *c* to message *m* using symmetric key *k* |
| *h = H(m)* | Hash message *m* to hash *h* |
| *k = KDF(m)* | Derive a key *k* from message *m* |
| *SK, PK = G(s)* | Generate a private key *SK* public key *PK* pair using seed *s*; if seed is empty generation is securely random |
| *sig = Sig(SK, m)* | Create signature *sig* using *SK* as the signer key and *m* as the signed message |

## Initial Trust Chain Setup
 * **FPF**:
     * *FPF<sub>SK</sub>, FPF<sub>PK</sub> = G()* - FPF generates a random keypair (we might add HSM requirements, or certificate style PKI, ie: self signing some attributes)
 * **Newsroom**:
     * *NR<sub>SK</sub>, NR<sub>PK</sub> = G()* - Newsroom generates a random keypair with similar security of the FPF one
     * *sig<sub>NR</sub> = Sig(FPF<sub>SK</sub>, NR<sub>PK</sub>)* - Newsroom sends a CSR or the public key to FPF for signing

