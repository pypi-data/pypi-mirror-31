python client for hornbill

test in python3.6

# use case:


## classify

```python
import hornbill4p

host = 'algorithm3'
port = 50051
client = hornbill4p.HornbillRpcClient(host, port)
res = client.classify("是个宝宝儿", ["ADTWT"])
print(res)
```
```bash
> ADTWT$1
```

## batch_classify

```python
import hornbill4p

host = 'algorithm3'
port = 50051
client = hornbill4p.HornbillRpcClient(host, port)
res = client.batch_classify(["是个宝宝儿", "是个宝宝儿"], ["ADTWT"])

for i in res:
    print(i)
```
```bash
> ADTWT$1
> ADTWT$1
```



# install 

```bash
git clone https://git.datatub.com/hornbill/hornbill4p.git
```

```bash
pip install -r requirements.txt
python setup.py install
```
 
