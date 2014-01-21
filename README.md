squarepotato-metalbox
=====================

touchscreen kiosk

run python bitcoin.py to test 
simulated data over localhost:8080 with json response {"code":0,"status":"ok","price":1000, "timestamp":12345678}
```php
        echo json_encode(array(
                'code' => 0,
                'status' => 'ok',
                'price' => rand(1000, 2000),
                'timestamp' => time()
        ) );
```
