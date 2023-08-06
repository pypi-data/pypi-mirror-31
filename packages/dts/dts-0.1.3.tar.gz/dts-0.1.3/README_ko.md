dts: seq와 비슷하지만 연속된 시간 문자열을 생성합니다
==========================================

## 연속된 시간 문자열

`dts` 는 연속된 시간 문자열을 생성합니다. 시작 시간과 마지막 시간을 필수 인자로 받습니다. 

```
$ dts 20180401 20180403
20180401
20180402
20180403
```

리눅스에 포함된 `seq` 명령은 연속된 숫자를 생성해주기 때문에 범용적으로 사용하기에 좋습니다. 
하지만, 시간을 다루기에는 불편합니다.

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

`dts`는 번거로운 시간 연산을 내장하고 있기 때문에, 간결하고 에러가 적습니다. 

```
$ dts 20171228 20180103
20171228
20171229
20171230
20171231
20180101
20180102
20180103
```

## 설치

```bash
pip install dts
```


## 사용법

`dts`는 `-i`로 시간 간격, `-f`로 시간 포맷을 인자로 받아서 다양한 표현이 가능합니다. 


```bash
$ dts -h
usage: dts [-h] [-i INTERVAL] [-f FORMAT] FIRST LAST

seq for datetime

positional arguments:
  FIRST                 first date of the seq. For example, 2018-05-01,
                        20180501, 20180501-0900, 2018-05-01T09:00
  LAST                  last date of the seq. See also, FIRST

optional arguments:
  -h, --help            show this help message and exit
  -i INTERVAL, --interval INTERVAL
                        interval: h1, d1, w1. default value is d1
  -f FORMAT, --format FORMAT
                        see also, datetime.strftime
```

* `-i`: 이 인자는 두 부분으로 구성됩니다. (시간 단위) + (간격)
  - 시간 단위: `h`은 시간, `d`은 일, `w`는 주를 의미합니다. 
  - 간격: 숫자
  - 예를들어, `h1`는 1시간 간격, `d3`는 3일 간격입니다.
  - 기본 값은 `d1`, 1일 간격입니다.

* `-f`: 파이선의 datetime format을 따릅니다. 다음을 참고하세요.(https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior)


### 단순 사용 예

시간 포맷은 다양하게 사용할 수 있습니다. 

```bash
$ dts 20180401 20180430 -i d7
20180401
20180408
20180415
20180422
20180429

$ dts 20180510-0900 20180510-1400 -i h1 -f '%Y%m%d-%H00'
20180510-0900
20180510-1000
20180510-1100
20180510-1200
20180510-1300
20180510-1400

$ dts 20180510-0900 20180510-1400 -i h1 -f '%Y-%m-%dT%H:00'
2018-05-10T09:00
2018-05-10T10:00
2018-05-10T11:00
2018-05-10T12:00
2018-05-10T13:00
2018-05-10T14:00
```


### Pipeline과 함께 사용 예

`credit`이라는 하이브 테이블이 있고, 파티션 컬럼이 `yyyymmdd` 인 경우에 hdfs 경로는 아래와 비슷하게 만들어집니다. 

```bash
hadoop fs -ls /hive/warehouse/sales.db/credit/yyyymmdd=20180401
```

이때 특정 기간의 파티션 크기를 알아보고 싶으면 `dts`와 `hadoop fs -ls` 명령을 파이프로 연결해서 사용합니다. 

```bash
$ dts 20180401 20180410 | xargs -I {} hadoop fs -ls /hive/warehouse/sales.db/credit/yyyymmdd={}
```

