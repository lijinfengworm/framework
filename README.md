#jblog
test
deploy on sae:

1. Modify uyan review system's parameters which key name is review in config_default.py .
2. Create storage service in SAE and rewrite your bucket name in config_default.py.
3. Create mysql service in SAE,then source sql script in jblog database.
4. Create kvdb service in SAE.
5. Create sequential taskQueue service in SAE and rewrite your taskqueue name in config_default.py.



insert into `test`.`gather_price` ( `addtime`, `sales`, `id`, `rated`, `price`, `type`, `goods_id`) values ( '20160928', '21', '1', '94', '134', '1', 'B018FTI47S');

Step4:根据 volume(商品销量)对样本数据进行
排序(从大到小) ,选取排在前 30 * 1% 的排序对
16

然后根据 price(商品价格)对样本
言s
象,组成集合 C] ,
数据进行排序(从小到大) ,选取排在前 30 * 2% 的
排序对象,组成集合 C2, Score(商家信誉)对样本数据进行排序(从大到小) , 选取排在前 30 * 3% 的排序对象,组成集合 C3,最 后,选取集合 C] ,C2 ,C3 的交集数据并且不属于集合 B 的数据组成集合 C;
Step5 :根据 volume(商品销量)对样本数据进行 排序(从大到小) ,选取排在前 100% 的排序对象,组 成集合 D] , 然后根据 price(商品价格)对样本数据 进行排序(从小到大) ,选取排在前 100% 的排序对 象,组成集合鸟,再次根据 Seller - Credit - Score (商家信誉)对样本数据进行排序(从大到小) ,选取 排在前 100% 的排序对象,组成集合 D3' 最后,选取 集合矶,鸟,矶的交集数据并且不属于集合 C 的数 据组成集合 D.
Step6 :将集合 A 包含的所有商品数据排在最前 面 ,B 次之, C 再次之 ,D 放到最后.
