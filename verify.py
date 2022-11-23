import ecdsa
import filelock
import hashlib
import json

# 電子署名が正しく行われているかチェックする
# 入力者の公開鍵を使って復号した結果がトランザクションハッシュと一致すれば、
# 入力者の秘密鍵を使って署名されたと言える

# トランザクションファイルの読み込み
with filelock.FileLock('trans.lock', timeout=10):
    with open('trans.txt', 'r') as file:
        tx_list = json.load(file)

# トランザクションごとに署名を検証する
for tx in tx_list:
    print('in hex:', tx['in'])
    print('out hex:', tx['out'])
    print('sig hex:', tx['sig'])
    # バイト列に変換
    tx_in = bytes.fromhex(tx['in']) 
    tx_out = bytes.fromhex(tx['out']) 
    tx_sig = bytes.fromhex(tx['sig']) 
    # トランザクションハッシュの作成（復号結果との比較用）
    sha = hashlib.sha256()
    sha.update(tx_in)
    sha.update(tx_out)
    hash = sha.digest()
    print('hash len:', len(hash))
    print('hash hex:', hash.hex())
    # 公開鍵を使って署名を復号し、トランザクションハッシュと一致するか検証
    key = ecdsa.VerifyingKey.from_string(tx_in, curve=ecdsa.SECP256k1)
    print('verify:', key.verify(tx_sig, hash), '\n')


