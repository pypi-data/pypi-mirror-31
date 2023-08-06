dts: Generate sequence of datatimes, like seq
=============================================

## Sequece of dates

`dts` generate sequence of datetimes. 

```
$ dts 20180401 20180403
20180401
20180402
20180403
```

If you do it using `seq`, it will like below.

```bash
$ seq 1 3
1
2
3
$ seq -f '%02g' 1 3 | xargs -I {} echo "201804{}"
20180401
20180402
20180403
```

## Install

```bash
pip install dts
```


## 
