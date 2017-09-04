# scw
A simple wrapper of 'sc query' command.

<!-- toc -->
- [scw](#scw)
  - [Overview](#overview)
  - [Demo](#demo)
    - [全サービス情報を表示](#全サービス情報を表示)
    - [キーワードに部分一致するサービスのみ表示](#キーワードに部分一致するサービスのみ表示)
    - [サービス名と表示名のみを表示するショートフォーマット](#サービス名と表示名のみを表示するショートフォーマット)
    - [Grep で引っ掛ける用の一行表示](#grep-で引っ掛ける用の一行表示)
  - [Requirement](#requirement)
  - [License](#license)
  - [Author](#author)

## Overview

Windows でサービス情報を調べたい時がありますが、 `service.msc` の画面や `sc query` コマンドはどちらも不便です。もっとサクっと手軽に表示したい……というわけで簡単なラッパースクリプトを作りました。

実装としては `sc query` と `sc qc` の標準出力結果をパースして、少し整形して表示を行うだけです。

なお、各項目の細かい意味は sc コマンドそのままなので各自で調べていただければと思います :sweat:

## Demo

コマンド実行例をいくつか紹介します。

### 全サービス情報を表示

```terminal
$ python scw.py
AdobeARMservice(Adobe Acrobat Update Service)
binary_path_name   : "C:\Program Files\Common Files\Adobe\ARM\1.0\armsvc.exe"
checkpoint         : 0x0
dependencies       :
display_name       : Adobe Acrobat Update Service
...

AeLookupSvc(Application Experience)
binary_path_name   : C:\Windows\system32\svchost.exe -k netsvcs
checkpoint         : 0x0
dependencies       :
display_name       : Application Experience
...

ALL 78 entries.
```

### キーワードに部分一致するサービスのみ表示

- 一致を照合する対象は「サービス名(SERVICE_NAME)」と「表示名(DISPLAY_NAME)」の二つ
- 大文字小文字は区別しない
- 複数キーワード指定時は AND 検索

```terminal
$ python scw.py win up
wuauserv(Windows Update)
binary_path_name   : C:\Windows\system32\svchost.exe -k netsvcs
checkpoint         : 0x0
dependencies       : rpcss
display_name       : Windows Update
error_control      : 1   NORMAL
load_order_group   :
operation_pause    : NOT_PAUSABLE
operation_shutdown : ACCEPTS_PRESHUTDOWN
operation_stop     : STOPPABLE
service_exit_code  : 0  (0x0)
service_start_name : LocalSystem
start_type         : 2   AUTO_START  (DELAYED)
state              : 4  RUNNING
tag                : 0
type               : 20  WIN32_SHARE_PROCESS
wait_hint          : 0x0
win32_exit_code    : 0  (0x0)

ALL 1 entries.
```

### サービス名と表示名のみを表示するショートフォーマット

`-s` オプション。

```
$ python scw.py win -s
* AudioEndpointBuilder(Windows Audio Endpoint Builder)
* Audiosrv(Windows Audio)
* eventlog(Windows Event Log)
...
* wuauserv(Windows Update)
ALL 11 entries.
```

### Grep で引っ掛ける用の一行表示

`-l` オプション。

```terminal
$ python scw.py win up -l
* wuauserv(Windows Update) -> binary_path_name=C:\Windows\system32\svchost.exe -k netsvcs, checkpoint=0x0, dependencies=rpcss, display_name=Windows Update, error_control=1   NORMAL, load_order_group=, operation_pause=NOT_PAUSABLE, operation_shutdown=ACCEPTS_PRESHUTDOWN, operation_stop=STOPPABLE, service_exit_code=0  (0x0), service_start_name=LocalSystem, start_type=2   AUTO_START  (DELAYED), state=4  RUNNING, tag=0, type=20  WIN32_SHARE_PROCESS, wait_hint=0x0, win32_exit_code=0  (0x0)
ALL 1 entries.
```

## Requirement

- Windows 7+
- Python 2.7

## License

[MIT License](LICENSE)

## Author

[stakiran](https://github.com/stakiran)
