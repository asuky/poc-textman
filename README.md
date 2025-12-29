## Windows に mkcert 入れる
確認はホスト側でやるので、
```Powershell
PS C:\Users\asuky> winget install mkcert
'msstore' ソースでは、使用する前に次の契約を表示する必要があります。
Terms of Transaction: https://aka.ms/microsoft-store-terms-of-transaction
ソースが正常に機能するには、現在のマシンの 2 文字の地理的リージョンをバックエンド サービスに送信する必要があります (例: "US")。

すべてのソース契約条件に同意しますか?
[Y] はい  [N] いいえ: y
見つかりました mkcert [FiloSottile.mkcert] バージョン 1.4.4
このアプリケーションは所有者からライセンス供与されます。
Microsoft はサードパーティのパッケージに対して責任を負わず、ライセンスも付与しません。
ダウンロード中 https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-windows-amd64.exe
  ██████████████████████████████  4.66 MB / 4.66 MB
インストーラーハッシュが正常に検証されました
パッケージのインストールを開始しています...
パス環境変数が変更されました; 新しい値を使用するにはシェルを再起動してください。
コマンド ライン エイリアスが追加されました: "mkcert"
インストールが完了しました
```
一度 PowerShell を終了する (exit)。

```PowerShell
PS C:\Users\asuky> mkcert --install
Created a new local CA 💥
The local CA is now installed in the system trust store! ⚡️
（警告が出るので「はい」）
PS C:\Users\asuky> mkcert -CAROOT
C:\Users\asuky\AppData\Local\mkcert
```
WSL の場合は /mnt/c に C ドライブがマウントされているのでそのまま cp できる。

```bash
sudo cp /mnt/c/Users/asuky/AppData/Local/mkcert/rootCA.pem /usr/local/share/ca-certificates/mkcert-rootCA.crt
sudo update-ca-certificates
```

hosts に関しては Windows の場合は WSL と勝手に同期される（らしい、未検証）。
気になる場合は /etc/wsl.conf の generateHosts を見る。
