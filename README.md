squarepotato-metalbox
=====================

touchscreen kiosk

run python bitcoin.py to test 
simulated data over localhost:8080 with json response {"code":0,"status":"ok","price":1000, "timestamp":12345678}
```php
        echo json_encode(array(
                'meta' => array(
                        'code' => 200,
                        'status' => "ok",
                        'method_name' => "exchange_rate"
                        ),
                'exchange_rate' => rand(1000, 2000)
                )
        );

```
