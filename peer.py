import base58
import ecdsa
import filelock
import hashlib
import json
import os
import re
import shutil # Shell Utilities ファイルのコピーなど
import subprocess # 別のプログラムを呼び出す
import urllib.request # Webサーバと通信

# 難易度
DIFFICULTY = 4

# トランザクションを格納したtrans.txtをpeer_trans.txtにコピー
try:
    shutil.copy('trans.txt', 'peer_trans.txt')
except:
    pass

# 通信先をpeer.txtから入力
# peer.txtは他ユーザと共有のファイル
dir = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(dir, 'peer.txt'), 'r') as file:
        peer_list = json.load(file)
except:
    peer_list = []

# ブロックチェーンをblock.txtから入力
with filelock.FileLock('block.lock', timeout=10):
    try:
        with open('block.txt', 'r') as file:
            block_list = json.load(file)
    except:
        block_list = []

# 通信先から最長のブロックチェーンを取得
for peer in peer_list:
    url = 'http://' + peer + '/block.txt'
    try:
        with urllib.request.urlopen(url) as file:
            peer_block_list = json.load(file)
    except:
        peer_block_list = []
    if len(block_list) < len(peer_block_list):
        for block in peer_block_list:
            sha = hashlib.sha256()
            sha.update(bytes(block['nonce']))
            sha.update(bytes.fromhex(block['previous_hash']))
            sha.update(bytes.fromhex(block['tx_hash']))
            hash = sha.digest()
            # 違法なブロックハッシュがあったらそのブロックチェーンは不採用
            if not re.match(r'0{' + str(DIFFICULTY) + r'}', hash.hex()):
                break
            # 実際はブロックチェーンの正当性のために他の検証も必要
        else: # for文がbreakされた時だけ実行する構文
            print('download:', url, 'length', 
                len(block_list), '->', len(peer_block_list))
            block_list = peer_block_list

# ブロックチェーンをblock.txtに出力
with filelock.FileLock('block.lock', timeout=10):
    with open('block.txt', 'w') as file:
        json.dump(block_list, file, indent=2)

# 通信先からトランザクションを取得
tx_list = []
for peer in peer_list:
    url = 'http://' + peer + 'peer_trans.txt'
    try:
        with urllib.request.urlopen(url) as file:
            peer_tx_list = json.load(file)
        # 簡単のため、重複したトランザクションも除外していない
        tx_list += peer_tx_list
        print('download:', url, 'count:', len(peer_tx_list))
    except:
        pass
# トランザクションをtrans.txtに出力
with filelock.FileLock('trans.lock', timeout=10):
    try:
        with open('trans.txt', 'r') as file:
            tx_list += json.load(file)
    except:
        pass

    with open('trans.txt', 'w') as file:
        json.dump(tx_list, file, indent=2)

# マイニング用の鍵ペアを作成
private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
public_key = private_key.get_verifying_key()
# Base58形式に変換
private_key = base58.b58encode(private_key.to_string()).decode('ascii')
public_key = base58.b58encode(public_key.to_string()).decode('ascii')
# 鍵ペアをkey.txtに出力
with filelock.FileLock('key.lock', timeout=10):
    try:
        with open('key.txt', 'r') as file:
            key_list = json.load(file)
    except:
        key_list = []

    key_list.append({
        'private': private_key,
        'public' : public_key
    })

    with open('key.txt', 'w') as file:
        json.dump(key_list, file, indent=2)

# 鍵ペアをコンソール表示
print('mine: private key:', private_key)
print('mine: public  key:', public_key)

# マイニングのプログラム(mine.py)を実行
subprocess.run(['python', os.path.join(dir, 'mine.py'), public_key])
