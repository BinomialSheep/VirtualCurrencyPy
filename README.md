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

支払元（入力）と支払先（出力）の秘密鍵と公開鍵を生成する。

`python key.py`
`python key.py`

電子署名を行い、トランザクションを作成する。引数は key.txt からコピペする。

`python sign.py in-private in-public out-public`

電子署名を検証する（公開鍵で署名を復号し、トランザクションハッシュと突合する）

`python verify.py`
