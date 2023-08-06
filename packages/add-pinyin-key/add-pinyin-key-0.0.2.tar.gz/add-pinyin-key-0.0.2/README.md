# 说明

## 安装

```
pip install add_pinyin_key
```

```bash
python setup.py install
```

## 使用示例

```bash
add_pinyin_key demo.bib demo_mod.bib
```

```text
% demo.bib
@article{_ct_2007,
 author = {严汉民 and 黄岗},
 date = {2007},
 journaltitle = {医疗设备信息},
 number = {12},
 pages = {1-5},
 title = {{{降低CT剂量的技术和方法探讨}}},
 urldate = {2018-04-18},
 volume = {22}
}
```

``` text
%demo_mod.bib
@article{_ct_2007,
 author = {严汉民 and 黄岗},
 date = {2007},
 journaltitle = {医疗设备信息},
 key = {yan2han4min2 and huang2gang3},
 number = {12},
 pages = {1-5},
 title = {{{降低CT剂量的技术和方法探讨}}},
 urldate = {2018-04-18},
 volume = {22}
}
```

注意如果输入的bib文件有类似于 `month = jan` 的字符串，你需要使用 `--common-strings` 选项。

```bash
add_pinyin_key --common-strings demo.bib demo_mod.bib
```