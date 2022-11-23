import base58
import filelock
import json

# 現在のコインの状況を出力する。
# 未支払鍵（unspent keys）：受け取りに使って支払いに使っていない鍵（所有コイン）
# 未使用鍵（unused keys)  ：受け取りにも支払いにも使っていない鍵


# 鍵ペアの一覧を取得
with filelock.FileLock('key.lock', timeout=10):
    try:
        with open('key.txt', 'r') as file:
            key_list = json.load(file)
    except:
        key_list = []

# ブロックチェーンを取得
with filelock.FileLock('block.lock', timeout=10):
    try:
        with open('block.txt', 'r') as file:
            block_list = json.load(file)
    except:
        block_list = []

# 既存のトランザクション入出力のリストを作成
old_in = []
old_out = []
for block in block_list:
    for tx in block['tx']:
        old_in.append(tx['in'])
        old_out.append(tx['out'])

# 未支払鍵と未使用鍵のリストを作成
unspent = []
unused = []
for key in key_list:
    key_hex = base58.b58decode(key['public']).hex()
    if key_hex not in old_in:
        if key_hex in old_out:
            unspent.append(key)
        else:
            unused.append(key)

# 未支払鍵の個数と一覧を出力
print(len(unspent), 'unspent keys(coins):')
for key in unspent:
    print('private:', key['private'])
    print('public :', key['public'])
print()

# 未使用鍵の個数と一覧を出力
print(len(unused), 'unused keys:')
for key in unused:
    print('private:', key['private'])
    print('public :', key['public'])