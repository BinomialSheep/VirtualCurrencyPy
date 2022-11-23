# 概要

書籍『入門 仮想通貨の作り方』の仮想通貨を作る

# 機能

- 公開鍵と秘密鍵
- 電子署名
- マイニング
- ウォレット
- P2P
- デーモン

# 必要なモジュール

- base58：ビットコインアドレスに使われるエンコード方式
- ecsa：楕円曲線 DSA
- filelock：排他ロック

```
pip install base58
pip install ecsa
pip install filelock
```

# ファイル

- key.py: 秘密鍵と公開鍵のペアを生成する
- sign.py: 電子署名を行う
- verify.py: 電子署名の検証尾を行う
- mine.py: マイニングを行う
- wallet.py: ウォレット
- peer.py: P2P 通信を行う
- mycoind.py: デーモン
- peer.txt: P2P の通信先を記載
- key.txt: 秘密鍵と公開鍵のペア（自動生成）
- trans.txt: トランザクションの記録（自動生成）
- block.txt: ブロックチェーンの記録（自動生成）
- user1: P2P 実験用フォルダ
- user2: P2P 実験用フォルダ

# 実行方法

## 1. key.txt, trans.txt, block.txt を削除する（前回の実行結果なので）

## 2. 支払元と支払先の秘密鍵と公開鍵を生成する。

`python key.py`
`python key.py`

## 3. 電子署名を行い、トランザクションを作成する。

引数は key.txt からコピペする。
例えば 1 つ目の鍵を支払元（in）、2 つ目の鍵を支払先（out）とする。

`python sign.py in-private in-public out-public`

## 4. 電子署名を検証する（公開鍵で署名を復号し、トランザクションハッシュと突合する）

`python verify.py`

## 5. マイニングを行う。

### 5.1 もう 1 つ秘密鍵と公開鍵を生成しておく

`python key.py`

### 5.2 1 回目のマイニングを行う

`python mine.py 報酬を得る公開鍵`

- 引数は 1 つ目の鍵（3 の支払元）にするとあとが分かりやすい
- 実行すると警告が出るはず
  - 3 の支払元はまだコインを持っていないのに支払のトランザクションがあるため
  - block.txt にはジェネレーショントランザクションのみ記録される
  - tran.txt には 3 のトランザクションが残る
  - このマイニングでコインを得るので次回は正しいトランザクションになる
- `python mine.py 報酬を得る公開鍵 verbose` で探索過程を表示できる。

### 5.3 3 回目のマイニングを行う

`python mine.py 報酬を得る公開鍵`

- 引数は 3 つ目の鍵（3 で支払元でも支払先でもない）にするとあとが分かりやすい
- 3 のトランザクションも block.txt に記録され、tran.txt は空になっているはず

## 6. ウォレットによる残高の確認

`python wallet`

- 未支払鍵（unspent keys）：受け取りに使って支払いに使っていない鍵
  - つまり残高
  - 2 個と表示されるはず
- 未使用鍵（unused keys) ：受け取りにも支払いにも使っていない鍵
  - 0 個と表示されるはず

## 7. 複数人で P2P 通信する動作確認

### 7.1 現在のディレクトリでコマンドプロンプトを 4 つ立ち上げる

- `cd user1`で移動した後`python -m http.server 8001`でサーバを立ち上げる
- `cd user1`で移動した後待機（ユーザ 1 の操作用）
- `cd user2`で移動した後`python -m http.server 8002`でサーバを立ち上げる
- `cd user2`で移動した後待機（ユーザ 2 の操作用）

### 7.2 ユーザ 1 でマイニング

`python ../peer.py`

### 7.3 ユーザ 1 で残高を確認

`python ../wallet.py`

未支払鍵が 1 つあることを確認する。

### 7.4 ユーザ 2 で鍵を生成

`python ../key.py`

### 7.5 ユーザ 1 からユーザ 2 に送金

`python ../sign.py 7.1の秘密鍵 7.1の公開鍵 7.4の公開鍵`

### 7.6 ユーザ 1 でマイニング

`python ../peer.py`

### 7.7 ユーザ 2 でマイニング

`python ../peer.py`

ユーザ 1 のブロックチェーン（ユーザ 2 の今のブロックチェーンより長い）を採用していることが確認できる。

### 7.8 ユーザ 2 で残高確認

`python ../wallet.py`

7.5 の送金が実行されていることが確認できる。

# Future work

本プログラムは書籍に記載された簡易的な機能の実装なので、例えば以下の機能追加が考えらえる。

- 報酬コインや送信コイン数を可変にする
  - 現在は常に 1 コイン
- 各ブロックのトランザクションハッシュをマークルツリーにする
- peer.py のブロックチェーンの正当性の検証を厳密に行う
  - 各ブロックに記録されたトランザクションハッシュと計算結果が一致するか
  - 直後のブロックの previous_hash と一致しているか
  - 各ブロックの全てのトランザクションの検証も必要
