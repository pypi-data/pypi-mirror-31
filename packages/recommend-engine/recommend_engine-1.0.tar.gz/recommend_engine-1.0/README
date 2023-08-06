# レコメンドエンジン

[課題内容](https://gist.github.com/vasily-staff/e207510e514890e9b35e3bd6b67a5573)


### 使用するアルゴリズム

オフライン学習する。

- [Matrix Factorization](https://ameblo.jp/principia-ca/entry-10980281840.html)
- [ALS(alternating least square)](https://qiita.com/ysekky/items/c81ff24da0390a74fc6c)


### モデル評価

- [Precision&Recall, PR曲線&ROC曲線&AUC](http://blog.brainpad.co.jp/entry/2017/08/25/140000)


### データセット

[MovieLens 100K Dataset](http://grouplens.org/datasets/movielens/)

### How to use

```
$ python setup.py install
```

#### evaluate performance
```
$ python main.py evaluate sgd 10 --epoch 100
$ python main.py evaluate als 10 --epoch 10

>AUC average: 0.7865845539854988
```

#### recommend movies to a user
```
$ python main.py recommend sgd 10 --epoch 100

>Who do you recommend to? (User ID: 1~943)
>10
>How many recommendations do you want?
>10
>recommendation rank | movie ID | recommendation score
>                  1 |     1536 |    5.829872760441447
>                  2 |     1467 |    5.595647914719889
>                  3 |     1642 |    5.458006368381115
>                  4 |     1398 |     5.23345094857352
>                  5 |     1653 |    5.150907212785244
>                  6 |     1651 |    5.126329240086269
>                  7 |     1449 |    5.102344229135889
>                  8 |     1645 |    5.066138567660829
>                  9 |     1636 |    5.055601132655621
```

