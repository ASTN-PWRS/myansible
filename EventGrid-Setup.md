# Event Grid（Blob DL → Logic Apps / Function / Webhook）設定手順

## 1. Storage Account を開く
Azure Portal → **Storage accounts** → 対象のストレージを選択

---

## 2. Events（イベント）を開く
左メニュー → **Events**  
→ **+ Event Subscription** をクリック

---

## 3. Event Subscription の設定

### ● Name
zip-download-alert

### ● Event Schema

Event Grid Schema（デフォルト）

### ● Event Types（イベントタイプ）
ダウンロード（GET）イベントを拾うため：Microsoft.Storage.BlobRead


## 4. フィルタ設定（ZIP & 特定コンテナに限定）
.zip

### ● Prefix filter（コンテナ名指定）
例：
mycontainer/

### ● Suffix filter（ZIP のみ）


---

## 5. Endpoint Type（通知先）を選択


### ● Webhook
- 自前 API に POST



## 6. Endpoint（Webhook URL）を指定
あなたの API の受信 URL を入力。

例：




## 7. Create（作成）
これで Event Grid が動作開始。


---

## 7. Webhook の Validation（重要）
Event Grid は Webhook 登録時に **Validation Event** を送信する。

### Webhook 側で必要な処理
1. Event Grid からの `validationCode` を受信  
2. そのままレスポンスとして返す  
   （JSON で返す必要あり）

### 例（レスポンス）
```json
{
  "validationResponse": "<validationCode>"
}

Webhook に届く Event Grid の例（BlobRead）
{
  "topic": "/subscriptions/xxxx/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/mystorage",
  "subject": "/blobServices/default/containers/mycontainer/blobs/sample.zip",
  "eventType": "Microsoft.Storage.BlobRead",
  "eventTime": "2026-06-09T10:00:00Z",
  "id": "xxxx",
  "data": {
    "api": "GetBlob",
    "clientRequestId": "xxxx",
    "requestId": "xxxx",
    "url": "https://mystorage.blob.core.windows.net/mycontainer/sample.zip",
    "sequencer": "00000000000000000000000000000000000000000000000000000000",
    "storageDiagnostics": {
      "batchId": "xxxx"
    }
  },
  "dataVersion": "",
  "metadataVersion": "1"
}
