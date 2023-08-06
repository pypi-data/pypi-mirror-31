# GAIS JSON Convertor

GAIS 格式和 JSON 格式互相轉換的 convertor.

## 資料格式說明

### GAIS format

以 `@` 開頭, `:` 結尾作為欄位名稱，`:` 以後的部分是欄位的內容，範例:

```bash
# title 為欄位名稱, : 以後的部分是欄位內容
@title:外出小心 今起3天高屏紅害
```

### JSON format

JSON 是一個輕量級、易於閱讀的資料交換格式。

## 安裝

```bash
pip3 install gais_json_convertor
```

## Usage

### GAIS to JSON

```python
from gais_json_convertor import Convertor

rec_beg = "@GAIS:"
records = [
    "@GAIS:", 
    "@title:來台南只知道牛肉湯？6大比秘境更吸引人的景點祭典", 
    "@time:2018/04/19 12:00", 
    "@url:https://bit.ly/2qJxkyQ", 
    "@body:台南，是不少人心中的美食之都，小巷子裡總是隱藏著各式各樣的美食等你去發掘", 
    "其中又以牛肉湯最為有名，吸引無數的外地人慕名而來。", 
    "但撇開台南有什麼美食好吃，說到不能錯過的景點就顯得相對較少", 
    "@loaction.lat:123", 
    "@location.lng:456"
]

try:
    data = convertor.gais2json(records, rec_beg)
    print(data)
except ValueError as err:
    print('ValueError: %s' % err)
```

Output:

```json
{
    "time": "2018/04/19 12:00",
    "url": "https://bit.ly/2qJxkyQ",
    "location": {
        "lng": 456,
        "lat": 123
    },
    "body": "台南，是不少人心中的美食之都，小巷子裡總是隱藏著各式各樣的美食等你去發掘 其中又以牛肉湯最為有名，吸引無數的外地人慕名而來。 但撇開台南有什麼美食好吃，說到不能錯過的景點就顯得相對較少",
    "title": "來台南只知道牛肉湯？6大比秘境更吸引人的景點祭典"
}
```

### convertor.gais2json(records, rec_beg)

`records` 是一個陣列，其中每一個陣列元素是一組欄位名稱和內容，如果陣列元素不包含欄位名稱，則會將此內容視為最接近的欄位的內容，如上面的範例: `records[5]` 和 `records[6]` 都會視為 `body (records[4])` 的內容。  
`rec_beg` 是 record begin pattern, 用來判斷每筆資料的開始。  
  
當欄位名稱包含 `.` 時，會視為巢狀的 JSON object, 最多只能包含兩層，例如：

```text
@data.body:...                  => {"data": {"body": "..."}}
@data.location.lat:123          => {"data": {"location": {"lat": 123}}}
@data.info.location.lat:123     => ValueError
```

## JSON to GAIS

```python
from gais_json_convertor import Convertor

records = {
    "title": "來台南只知道牛肉湯？6大比秘境更吸引人的景點祭典",
    "time": "2018/04/19 12:00",
    "url": "https://bit.ly/2qJxkyQ",
    "imgs": ["img1", "img2", "img3"],
    "info": {
        "location": {
            "lat": 123,
            "lng": 456
        },
        "phone": "12345678"
    }
}

try:
    data = convertor.json2gais(records)
    print(data)
except ValueError as err:
    print('ValueError: %s' % err)
```

Output:

```text
@GAIS:
@title:來台南只知道牛肉湯？6大比秘境更吸引人的景點祭典
@info.phone:12345678
@info.location.lng:456
@info.location.lat:123
@imgs:['img1', 'img2', 'img3']
@url:https://bit.ly/2qJxkyQ
@time:2018/04/19 12:00
```

### convertor.json2gais(records)

`records` 是一個 object 或是 array of objects, 最多可以包含兩層巢狀結構，超過兩層會直接存為 JSON string, 例如：

```json
{
    "data": {
        "info": {
            "location": {
                "lat": 123,
                "lng": 456
            }
        }
    }
}
```

會轉換為:

```text
@data.info.location:{"lat": 123, "lng": 456}
```