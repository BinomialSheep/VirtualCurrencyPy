import base58
import ecdsa
import filelock
import json

# 引数は楕円曲線の種類。secp256k1はビットコインでも使われているらしい
private_key = ecdsa.SigningKey.generate(curve = ecdsa.SECP256k1)
public_key = private_key.get_verifying_key()
private_key = private_key.to_string()
public_key = public_key.to_string()

# 16進数表記で出力
print('private key len:', len(private_key))
print('private key hex:', private_key.hex())
print('public  key len:', len(public_key))
print('public  key hex:', public_key.hex())

# Base58形式に変換して表示
private_b58 = base58.b58encode(private_key).decode('ascii')
public_b58 = base58.b58encode(public_key).decode('ascii')
print('private key base58:', private_b58)
print('public  key base58:', public_b58)

# 秘密鍵と公開鍵をテキストファイルに出力
with filelock.FileLock('key.lock', timeout = 10):
    try:
        with open('key.txt', 'r') as file:
            key_list = json.load(file)
    except:
        key_list = []

    key_list.append({
        'private': private_b58,
        'public' : public_b58
    })

    with open('key.txt', 'w') as file:
        json.dump(key_list, file, indent = 2)


