import base58
import ecdsa
import filelock
import hashlib
import json
import re
import sys

# 難易度
# 4で数秒～数十秒程度（ハッシュは16進数なので1増やすと16倍難しくなる）
DIFFICULTY = 4
# 経過表示オプション
VERBOSE = False

# コマンドライン引数処理
if len(sys.argv) == 2:
    pass
elif len(sys.argv) == 3 and sys.argv[2] == 'verbose':
    VERBOSE = True
else:
    print('usage:', sys.argv[0], 'public-key [verbose]')
    exit()

# マイニング用公開鍵を16進数表記に変換
public_key = base58.b58decode(sys.argv[1]).hex()

# 現在のブロックチェーンを取得
with filelock.FileLock('block.lock', timeout=10):
    try:
        with open('block.txt', 'r') as file:
            block_list = json.load(file)
        previous_hash = block_list[-1]['hash']
    except:
        block_list = []
        previous_hash = ''

# 現在のトランザクションを取得
with filelock.FileLock('block.lock', timeout=10):
    try:
        with open('trans.txt', 'r') as file:
            tx_list = json.load(file)
    except:
        tx_list = []

# 過去のトランザクション入出力のリストを作成
old_in = []
old_out = []
for block in block_list:
    for tx in block['tx']:
        old_in.append(tx['in'])
        old_out.append(tx['out'])

# トランザクションの検証
file_tx_list = tx_list
tx_list = []
for tx in file_tx_list:
    # 入力公開鍵と出力公開鍵からハッシュを計算
    sha = hashlib.sha256()
    sha.update(bytes.fromhex(tx['in']))
    sha.update(bytes.fromhex(tx['out']))
    hash = sha.digest()
    # 入力公開鍵から署名を検証するための鍵を作成
    key = ecdsa.VerifyingKey.from_string(bytes.fromhex(tx['in']), curve=ecdsa.SECP256k1)
    # 署名が正しいか検証
    if not key.verify(bytes.fromhex(tx['sig']), hash):
        print('invalid signature:', tx['sig'])
        continue
    # トランザクションの入力が既に使用済みか検証（あるならNG）
    if tx['in'] in old_in:
        print('tx-in has already been spent:', tx['in'])
        continue
    # トランザクションの入力が過去の入力に含まれてるか検証（ないならNG）
    if tx['in'] not in old_out:
        print('tx-out for tx-in is not found:', tx['in'])
        continue
    # トランザクションの出力が過去の入出力に含まれるか検証（あるならNG）
    if tx['out'] in old_in or tx['out'] in old_out:
        print('tx-out is reused:', tx['out'])
        continue
    # 以上問題がなければ正しいトランザクション
    tx_list.append(tx)
    old_in.append(tx['in'])
    old_out.append(tx['out'])

# マイニング用の公開鍵の検証（既存のトランザクションにあるならNG）
if public_key in old_in or public_key in old_out:
    print('public-key is reused:', public_key)
    exit()
# 検証に成功したら既存のトランザクション出力に追加しておく
old_out.append(public_key)

# 検証ここまで

# ジェネレーショントランザクションを先頭に追加
# ※マイニングの報酬の支払用
tx_list.insert(0, {
    'in' : '',
    'out': public_key,
    'sig': ''
})

# トランザクションハッシュの計算
# ブロックに含まれる全てのトランザクションの入力、出力、署名を使う
# ※ビットコインでは単純に渡す代わりにマークルツリーを用いる
sha = hashlib.sha256()
for tx in tx_list:
    sha.update(bytes.fromhex(tx['in']))
    sha.update(bytes.fromhex(tx['out']))
    sha.update(bytes.fromhex(tx['sig']))
tx_hash = sha.digest()

# ノンスの探索
for nonce in range(int(1e8)):
    # ブロックヘッダ（※）に対してブロックハッシュを計算する
    # ※本プログラムではノンス、直前のブロックハッシュ、トランザクションハッシュ
    # ビットコインではブロック作成時の時刻も含まれる
    sha = hashlib.sha256()
    sha.update(bytes(nonce))
    sha.update(bytes.fromhex(previous_hash))
    sha.update(tx_hash)
    hash = sha.digest()
    # ゼロがDIFFICULTY個並んでいたらゴールデンノンス
    if re.match(r'0{' + str(DIFFICULTY) + r'}', hash.hex()):
        break
    # 経過の出力
    if VERBOSE:
        print('nonce:{0:08d}'.format(nonce), 'hash hex:', hash.hex())
# ゴールデンノンスの表示
print('nonce:{0:08d}'.format(nonce), 'hash hex:', hash.hex())

# ブロックチェーンへのブロックの追加
block_list.append({
    'hash'          : hash.hex(),
    'nonce'         : nonce,
    'previous_hash' : previous_hash,
    'tx_hash'       : tx_hash.hex(),
    'tx'            : tx_list
})

# ブロックチェーンの書き出し
with filelock.FileLock('block.lock', timeout=10):
    with open('block.txt', 'w') as file:
        json.dump(block_list, file, indent=2)

# ブロックに登録したトランザクションをtrans.txtから削除
with filelock.FileLock('trans.lock', timeout=10):
    try:
        with open('trans.txt', 'r') as file:
            file_tx_list = json.load(file)
    except:
        file_tx_list = []
    
    tx_list = []
    for tx in file_tx_list:
        # 入力が既存の入力にあれば削除
        if (tx['in'] in old_in) : continue
        # 出力が既存の入力にあれば削除
        if (tx['out'] in old_in) : continue
        # 出力が既存の出力にあれば削除
        if (tx['out'] in old_out) : continue
        # それ以外は残す
        tx_list.append(tx)
    
    with open('trans.txt', 'w') as file:
        json.dump(tx_list, file, indent=2)

