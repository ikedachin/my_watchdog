# My Watch dog Document

以下、GPTでドキュメントを作成しました（楽ちん）

このプログラムは、指定されたフォルダ内のファイルの存在、追加、削除、更新を監視する `WatchDog` クラスを提供します。また、監視対象フォルダに変化があった場合に他のプログラムを実行するための機能も備えています。

## 目次
1. [定数の設定](#定数の設定)
2. [ロガーの設定](#ロガーの設定)
3. [WatchDog クラス](#WatchDog-クラス)
    - [コンストラクタ](#コンストラクタ)
    - [ファイルアクセスチェック](#ファイルアクセスチェック)
    - [ファイル存在確認](#ファイル存在確認)
    - [新規ファイル追加確認](#新規ファイル追加確認)
    - [ファイル削除確認](#ファイル削除確認)
    - [ファイル更新確認](#ファイル更新確認)
4. [メイン処理](#メイン処理)

## 定数の設定

```python
INTERVAL_TIME = 3 # sec
```

- `INTERVAL_TIME`: 監視のインターバル時間（秒）。

## ロガーの設定

```python
filename = os.path.basename(__file__).replace('.py', '')
logfile_date = datetime.datetime.now().strftime('%Y_%m_%d')
log_file_path = f'./watchdog_log/{logfile_date}_{filename}.log'

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
handler = logging.FileHandler(log_file_path)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.info('**************** start ***************')
```

ロガーは、プログラムの動作をログファイルに記録します。ログファイルのパスは、実行日時に基づいて動的に決定されます。

## WatchDog クラス

### コンストラクタ

```python
class WatchDog():
    def __init__(self, path, extention=None):
        # 初期設定
```

- `path`: 監視対象のフォルダパス。
- `extention`: 監視対象のファイル拡張子（省略可能）。

### ファイルアクセスチェック

```python
def access_check(self, files: list):
```

- `files`: ファイルのリスト。
- 戻り値: アクセスされていないファイルのリスト。

指定されたファイルがアクセス可能かどうかをチェックします。Windows、macOS、Linux それぞれに対応しています。

### ファイル存在確認

```python
def watch_file_existance(self):
```

- 戻り値: ファイルが存在するかどうかのフラグとファイルのリスト。

監視対象フォルダにファイルが存在するかどうかを確認します。

### 新規ファイル追加確認

```python
def watch_add_new_files(self, return_past_files=False):
```

- `return_past_files`: 過去に存在したファイルも含めるかどうか。
- 戻り値: 新規ファイルが追加されたかどうかのフラグと新規ファイルのリスト。

新規に追加されたファイルを検出します。過去に存在していたファイルも含めるかどうかを指定できます。

### ファイル削除確認

```python
def watch_removed_files(self):
```

- 戻り値: ファイルが削除されたかどうかのフラグと削除されたファイルのリスト。

監視対象フォルダからファイルが削除されたかどうかを検出します。

### ファイル更新確認

```python
def watch_update_time(self, return_past_files=False):
```

- `return_past_files`: 過去に存在したファイルも含めるかどうか。
- 戻り値: ファイルが更新されたかどうかのフラグと更新されたファイルのリスト。

ファイルが更新されたかどうかを確認します。過去に存在していたファイルも含めるかどうかを指定できます。

## メイン処理
複数のフォルダを監視する場合は別々のインスタンスを立ててフォルダを監視をします。



```python
if __name__ == "__main__":
    path1 = './watch_folder1/'
    path2 = './watch_folder2/'
    path3 = './watch_folder3/'

    watchdog1 = WatchDog(path1)
    watchdog2 = WatchDog(path2)
    watchdog3 = WatchDog(path3)

    while True:
        flag1, watching_files1 = watchdog1.watch_add_new_files(return_past_files=True)
        flag2, watching_files2 = watchdog2.watch_add_new_files(return_past_files=True)
        flag3, watching_files3 = watchdog3.watch_add_new_files(return_past_files=True)

        flag2_3 = sum([flag2, flag3])

        if flag1:
            print(f'************ start main process {os.path.basename(path1)} ************')
            command1 = 'python aaa.py'
            result_1 = subprocess.run(command1, shell=True, capture_output=True, text=True)
            error_1 = result_1.stderr
            logger.error({
                'action': command2,
                'error': error_1,
            })

        elif flag2_3:
            print(f'************ start main process {os.path.basename(path2)} / {os.path.basename(path3)} ************')
            command2 = 'python bbb.py'
            result_2 = subprocess.run(command2, shell=True, capture_output=True, text=True)
            error_2 = result_2.stderr
            logger.error({
                'action': command2,
                'error': error_2,
            })
        else:
            pass

        time.sleep(INTERVAL_TIME)
```

メイン処理は以下の手順で動作します：

1. `path1`, `path2`, `path3` で指定されたフォルダを監視する `WatchDog` インスタンスを作成します。
2. 無限ループ内で、各フォルダに新規ファイルが追加されたかどうかをチェックします。
3. `watch_add_new_files` メソッドを使用して、各フォルダの新規ファイル追加を確認します。
4. もし `path1` に新規ファイルが追加された場合、`aaa.py` を実行し、その結果をログに記録します。
5. もし `path2` または `path3` に新規ファイルが追加された場合、`bbb.py` を実行し、その結果をログに記録します。
6. 監視のインターバル時間 (`INTERVAL_TIME`) の間、処理を一時停止します。

## まとめ

このプログラムは、指定されたフォルダ内のファイルの存在、追加、削除、更新を監視し、フォルダに変化があった場合に他のプログラムを実行する機能を提供します。`WatchDog` クラスは、ファイルのアクセスチェック、存在確認、新規追加確認、削除確認、更新確認といった多機能を持ち、様々な用途で利用することができます。

このプログラムのロギング機能により、監視中のイベントを詳細に記録し、デバッグや運用時のトラブルシューティングを容易にします。また、プログラムはマルチプラットフォーム（Windows、macOS、Linux）に対応しており、幅広い環境で使用することができます。

