
var addressInit = function(_carea,_cmbProvince, _cmbCity, _cmbArea,defaultarea1, defaultProvince, defaultCity, defaultArea)
{
    var area=document.getElementById(_carea);
    var cmbProvince = document.getElementById(_cmbProvince);
    var cmbCity = document.getElementById(_cmbCity);
    var cmbArea = document.getElementById(_cmbArea);
    function cmbSelect(cmb, str)
    {
        for(var i=0; i<cmb.options.length; i++)
        {
            if(cmb.options[i].value == str)
            {
                cmb.selectedIndex = i;
                return;
            }
        }
    }
    function cmbAddOption(cmb, str, obj)
    {
        var option = document.createElement("OPTION");
        option.innerHTML = str;
        option.value = str;
        option.obj = obj;
        cmb.options.add(option);
    }

    function changeCity()
    {
        cmbArea.options.length = 0;
        if(cmbCity.selectedIndex == -1)return;
        var item = cmbCity.options[cmbCity.selectedIndex].obj;
        for(var i=0; i<item.areaList.length; i++)
        {
            cmbAddOption(cmbArea, item.areaList[i], null);
        }
        cmbSelect(cmbArea, defaultArea);
    }
    function changeProvince()
    {
        cmbCity.options.length = 0;
        cmbCity.onchange = null;
        if(cmbProvince.selectedIndex == -1)return;

        var item = cmbProvince.options[cmbProvince.selectedIndex].obj;
        for(var i=0; i<item[cmbProvince.selectedIndex].cityList.length; i++)
        {
            cmbAddOption(cmbCity, item[cmbProvince.selectedIndex].cityList[i].name, item[cmbProvince.selectedIndex].cityList[i]);
        }
        cmbSelect(cmbCity, defaultCity);
        changeCity();
        cmbCity.onchange = changeCity;
    }
    function changeArea()
    {
        cmbProvince.options.length = 0;
        cmbProvince.onchange = null;
        if(area.selectedIndex == -1)return;
        var item=area.options[area.selectedIndex].obj;
        for(var i=0;i<item.Allcity.length;i++)
        {
            cmbAddOption(cmbProvince,item.Allcity[i].name,item.Allcity);
        }
        cmbSelect(cmbProvince,defaultProvince);
        changeProvince();
        cmbProvince.onchange=changeProvince;
    }
    // function configMchAppConfig(province) {
    //     config = document.getElementById("mch-app-config");
    // }

    for(var i=0; i<provinceList.length; i++)
    {
    //alert(provinceList[i].Allcity[0].name);
    //var mess=provinceList[i].Allcity.join('--');
    //alert(mess);
        cmbAddOption(area, provinceList[i]._area, provinceList[i]);
    }

    cmbSelect(area, defaultarea1);
    changeArea();
    area.onchange = changeArea;
}

var provinceList = [

{_area:"企业",Allcity:[

{name:'餐饮/食品', cityList:[
{name:'中餐', areaList:['川菜','湘菜','湖北菜','台湾菜','新疆菜','江浙菜','云南菜','贵州菜','西北菜','东北菜','香锅/烤鱼','海鲜','其它地方菜','粤菜','海南菜','鲁菜','徽菜','晋菜','豫菜','闽菜','上海本帮菜','淮扬菜']},
{name:'火锅', areaList:['麻辣烫/串串香','川味/重庆火锅','云南火锅','老北京涮羊肉','港式火锅','鱼火锅','羊蝎子','炭火锅','韩式火锅','豆捞','其它火锅']},
{name:'烧烤', areaList:['中式烧烤','拉美烧烤','日式烧烤','铁板烧','韩式烧烤','其它烧烤']},
{name:'其他美食', areaList:['自助餐','创意菜','西餐','日韩料理','东南亚菜','素食','其他餐饮美食','清真菜','茶餐厅','土菜/农家菜','采摘/农家乐']},
{name:'汤/粥/煲/砂锅/炖菜', areaList:['粥','汤','砂锅/煲类/炖菜','其它']},
{name:'快餐', areaList:['西式快餐','中式快餐','其它快餐']},
{name:'休闲食品', areaList:['零食','生鲜水果','其它休闲食品','美食特产']},
{name:'小吃', areaList:['熟食','面点','米粉/米线','其它小吃']},
{name:'休闲茶饮', areaList:['咖啡','奶茶','冰激凌','饮品/甜点','咖啡厅','酒吧']},
{name:'烘焙糕点', areaList:['蛋糕','面包','其它烘焙糕点']}
]},

{name:'零售/批发', cityList:[
{name:'超市便利店', areaList:['超市','个人护理','烟酒杂货','自动售卖机']},
{name:'其他综合零售', areaList:['特色集市','菜市场']},
{name:'烟花爆竹', areaList:['烟花爆竹']},
{name:'其他综合零售', areaList:['国外代购及免税店']},
{name:'百货/商圈/购物中心', areaList:['购物中心','百货','机场','火车站','商旅文综合体']},
{name:'汽车/运输工具/配件', areaList:['汽车销售','二手车销售','车饰','机动车/配件批发','活动房车销售商','汽车轮胎经销','汽车零配件','船舶及配件','拖车篷车娱乐用车','轨道交通设备器材','飞机/配件','运输搬运设备','起重装卸设备','摩托车及配件','电动车及配件','露营及旅行汽车','雪车']},
{name:'办公用品批发', areaList:['商务家具批发','办公器材批发','办公用品文具批发']},
{name:'工业产品批发零售', areaList:['金属产品/服务','电气产品/设备','五金器材/用品','管道/供暖设备批发','工业设备/制成品','工业耐用品','化工产品','石油/石油产品']},
{name:'药品医疗批发', areaList:['医疗器械','药品批发商','康复/身体辅助品']}
]},

{name:'娱乐/美容/健身服务', cityList:[
{name:'K歌', areaList:['量贩式KTV','会所型KTV','录音棚']},
{name:'休闲娱乐', areaList:['亲子游乐','科普场馆','亲子DIY','棋牌休闲','中医养生','足疗按摩','洗浴/桑拿会所','网吧网咖','游乐游艺','图书馆','密室','桌面游戏','真人CS']},
{name:'美发/美容/美甲', areaList:['美甲/手护','SPA/美容/美体','美容美发','美容美甲','美发美甲','美发','彩妆造型','美睫','产后塑形','纹绣','纹身','祛痘','整形']},
{name:'运动健身', areaList:['篮球场','舞蹈','网球场','乒乓球馆','游泳馆','羽毛球馆','桌球馆','瑜伽','足球场','武术场馆','溜冰场','保龄球馆','壁球场','排球场','高尔夫球场','体育场馆','健身中心']}
]},

{name:'生活/家居', cityList:[
{name:'宠物', areaList:['宠物店','宠物医院']},
{name:'服饰/箱包/饰品', areaList:['男性服装','女性成衣','内衣','家居服','皮草皮具','高档时装正装定制','裁缝','综合服饰','儿童服饰','剃须刀','瑞士军刀','烟酒具','配饰商店','假发','饰物','鞋类','行李箱包']},
{name:'美妆/护肤', areaList:['化妆品']},
{name:'黄金珠宝/钻石/玉石', areaList:['珠宝','金银']},
{name:'钟表/眼镜', areaList:['钟表店','眼镜店']},
{name:'婚庆用品', areaList:['婚庆用品']},
{name:'母婴用品/儿童玩具', areaList:['母婴用品/儿童玩具']},
{name:'户外/运动/健身器材/安防', areaList:['运动户外安防用品']},
{name:'文化艺术店', areaList:['文具','乐器','二手商品店','文物古董','古玩复制品','礼品','卡片','纪念品','瓷器','玻璃和水晶摆件','工艺美术用品','艺术品和画廊','邮票/纪念币','宗教物品']},
{name:'数码家电/办公设备', areaList:['手机','通讯设备','数码产品及配件','专业摄影器材','计算机/服务器','打字/打印/扫描','家用电器']},
{name:'家居家纺', areaList:['草坪和花园用品','地毯窗帘等家纺','帷幕','室内装潢壁炉','屏风','家庭装饰','花木栽种用品']},
{name:'建材', areaList:['油漆','清漆用品','大型建材卖场卖场','木材与建材商店','玻璃','墙纸']},
{name:'计生用品', areaList:['计生用品']},
{name:'报刊/音像/书籍', areaList:['音像制品租售','音像制品/书籍','书籍','报纸杂志']},
{name:'鲜花/盆栽', areaList:['鲜花/盆栽']}
]},

{name:'生活/咨询服务', cityList:[
{name:'婚庆/摄影', areaList:['婚礼策划','婚纱/礼服','婚车租赁','旅拍/本地婚纱摄影','本地婚纱摄影','儿童摄影','孕妇摄影','跟拍','证件照','商业摄影']},
{name:'亲子服务', areaList:['亲子游泳','亲子服务','产后恢复','月子服务']},
{name:'洗衣', areaList:['洗衣家纺','鞋帽清洗','奢侈品养护','自助洗衣']},
{name:'咨询/法律咨询/金融咨询', areaList:['咨询/法律咨询/金融咨询']},
{name:'家政/维修服务', areaList:['洗车','拖车','维修','保养','汽车美容','送水站','搬家','回收','开锁','管道疏通','家电维修','焊接维修','家居维修、翻新','家政','灭虫/消毒','清洁/保养/门卫']},
{name:'装饰/设计', areaList:['装饰/设计']},
{name:'广告/会展/活动策划', areaList:['广告/会展/活动策划']},
{name:'农业合作与农具', areaList:['农业合作与农具']},
{name:'丧仪殡葬服务', areaList:['丧仪殡葬服务']}
]},

{name:'教育/培训', cityList:[
{name:'教育/培训/考试缴费/学费', areaList:['早教中心','少儿外语','少儿才艺','职业技术培训','外语','音乐','升学辅导','体育','美术','留学','驾校','兴趣生活','成人教育/函授','商业/文秘学校','福清市','长乐市']},
{name:'私立院校', areaList:['中小学校','大学与学院','儿童保育/学前']}
]},

{name:'金融', cityList:[
{name:'保险业务', areaList:['保险业务']}
]},

{name:'交通运输服务类', cityList:[
{name:'租车', areaList:['汽车租赁','租车']},
{name:'加油', areaList:['加油']},
{name:'货运代理/报关行', areaList:['货运代理/报关行']},
{name:'铁路客运', areaList:['铁路客运']},
{name:'公共交通', areaList:['公共交通']},
{name:'长途公路客运', areaList:['长途公路客运']},
{name:'游轮/巡游航线', areaList:['游轮/巡游航线']},
{name:'出租船只', areaList:['出租船只']},
{name:'港口经营\港口理货', areaList:['港口经营\港口理货']},
{name:'机场服务', areaList:['贵宾服务','行李打包','wifi租赁']},
{name:'高铁服务', areaList:['高铁贵宾服务','高铁行李打包']},
{name:'物流/快递', areaList:['物流货运','铁路货运','公共仓储','集装整理','快递服务']}
]},

{name:'生活缴费', cityList:[
{name:'停车缴费', areaList:['停车缴费']},
{name:'路桥通行费', areaList:['路桥通行费']},
{name:'水电煤缴费/交通罚款等生活缴费', areaList:['电力缴费','煤气缴费','自来水缴费']},
{name:'自来水缴费', areaList:['自来水缴费']}
]},

{name:'医疗', cityList:[
{name:'私立/民营医院/诊所', areaList:['社区医院','正骨医生','按摩医生','眼科医疗服务','手足病医疗服务','护理/照料服务','中医','齿科','药店','急救服务','妇幼医院','体检中心']}
]},

{name:'票务/旅游', cityList:[
{name:'景区', areaList:['门票','景区生活服务','景区购物']},
{name:'旅馆/酒店/度假区', areaList:['客栈单体','客栈连锁','酒店单体','酒店连锁','酒店式公寓','度假别墅服务','运动和娱乐露营','活动房车和野营']},
{name:'票务', areaList:['交通票务']},
{name:'旅行社', areaList:['旅行社']},
{name:'机票/机票代理社', areaList:['航空公司','机票平台']}
]},

{name:'政府/社会组织', cityList:[
{name:'社会组织', areaList:['慈善/社会公益','行业协会/社团','宗教组织']},
{name:'游艺厅/KTV/网吧', areaList:['电影院','私人影院']}
]},

{name:'通信', cityList:[
{name:'电信运营商', areaList:['电信运营商']},
{name:'话费充值与缴费', areaList:['话费充值与缴费']},
{name:'互联网IDC服务', areaList:['互联网IDC服务']},
{name:'网络电话传真', areaList:['网络电话传真']},
{name:'通信营业厅', areaList:['通信营业厅']},
{name:'付费电话', areaList:['付费电话']}
]},

{name:'网络虚拟服务', cityList:[
{name:'门户/资讯/论坛', areaList:['门户/资讯/论坛']},
{name:'软件/建站/技术开发', areaList:['软件/建站/技术开发']},
{name:'游戏', areaList:['游戏']},
{name:'在线图书/视频/音乐', areaList:['在线图书/视频/音乐']},
{name:'网络推广/网络广告', areaList:['网络推广/网络广告']}
]},

]
},


{_area:"个体工商户",Allcity:[

{name:'餐饮/食品', cityList:[
{name:'中餐', areaList:['川菜','湘菜','湖北菜','台湾菜','新疆菜','江浙菜','云南菜','贵州菜','西北菜','东北菜','香锅/烤鱼','海鲜','其它地方菜','粤菜','海南菜','鲁菜','徽菜','晋菜','豫菜','闽菜','上海本帮菜','淮扬菜']},
{name:'火锅', areaList:['麻辣烫/串串香','川味/重庆火锅','云南火锅','老北京涮羊肉','港式火锅','鱼火锅','羊蝎子','炭火锅','韩式火锅','豆捞','其它火锅']},
{name:'烧烤', areaList:['中式烧烤','拉美烧烤','日式烧烤','铁板烧','韩式烧烤','其它烧烤']},
{name:'其他美食', areaList:['自助餐','创意菜','西餐','日韩料理','东南亚菜','素食','其他餐饮美食','清真菜','茶餐厅','土菜/农家菜','采摘/农家乐']},
{name:'汤/粥/煲/砂锅/炖菜', areaList:['粥','汤','砂锅/煲类/炖菜','其它']},
{name:'快餐', areaList:['西式快餐','中式快餐','其它快餐']},
{name:'休闲食品', areaList:['零食','生鲜水果','其它休闲食品','美食特产']},
{name:'小吃', areaList:['熟食','面点','米粉/米线','其它小吃']},
{name:'休闲茶饮', areaList:['咖啡','奶茶','冰激凌','饮品/甜点','咖啡厅','酒吧']},
{name:'烘焙糕点', areaList:['蛋糕','面包','其它烘焙糕点']}
]},

{name:'零售/批发', cityList:[
{name:'超市便利店', areaList:['个人护理','便利店','烟酒杂货']},
{name:'其他综合零售', areaList:['特色集市']},
{name:'汽车/运输工具/配件', areaList:['汽车销售','二手车销售','车饰','机动车/配件批发','活动房车销售商','汽车轮胎经销','汽车零配件','船舶及配件','拖车篷车娱乐用车','轨道交通设备器材','飞机/配件','运输搬运设备','起重装卸设备','摩托车及配件','电动车及配件','露营及旅行汽车','雪车']},
{name:'办公用品批发', areaList:['商务家具批发','办公器材批发','办公用品文具批发']},
{name:'工业产品批发零售', areaList:['金属产品/服务','电气产品/设备','五金器材/用品','管道/供暖设备批发','工业设备/制成品','工业耐用品','化工产品','石油/石油产品']},
{name:'药品医疗批发', areaList:['医疗器械','药品批发商','康复/身体辅助品']}
]},

{name:'娱乐/美容/健身服务', cityList:[
{name:'K歌', areaList:['量贩式KTV','会所型KTV','录音棚']},
{name:'休闲娱乐', areaList:['亲子游乐','科普场馆','亲子DIY','棋牌休闲','中医养生','足疗按摩','洗浴/桑拿会所','网吧网咖','游乐游艺','图书馆','密室','桌面游戏','真人CS']},
{name:'美发/美容/美甲', areaList:['美甲/手护','SPA/美容/美体','美容美发','美容美甲','美发美甲','美发','彩妆造型','美睫','产后塑形','纹绣','纹身','祛痘','整形']},
{name:'运动健身', areaList:['篮球场','舞蹈','网球场','乒乓球馆','游泳馆','羽毛球馆','桌球馆','瑜伽','足球场','武术场馆','溜冰场','保龄球馆','壁球场','排球场','高尔夫球场','体育场馆','健身中心']}
]},

{name:'生活/家居', cityList:[
{name:'宠物', areaList:['宠物店','宠物医院']},
{name:'服饰/箱包/饰品', areaList:['男性服装','女性成衣','内衣','家居服','皮草皮具','高档时装正装定制','裁缝','综合服饰','儿童服饰','剃须刀','瑞士军刀','烟酒具','配饰商店','假发','饰物','鞋类','行李箱包']},
{name:'美妆/护肤', areaList:['化妆品']},
{name:'钟表/眼镜', areaList:['钟表店']},
{name:'婚庆用品', areaList:['婚庆用品']},
{name:'母婴用品/儿童玩具', areaList:['母婴用品/儿童玩具']},
{name:'户外/运动/健身器材/安防', areaList:['运动户外安防用品']},
{name:'文化艺术店', areaList:['文具','乐器','二手商品店','礼品','卡片','纪念品','瓷器','玻璃和水晶摆件','工艺美术用品','宗教物品']},
{name:'数码家电/办公设备', areaList:['手机','通讯设备','数码产品及配件','专业摄影器材','计算机/服务器','打字/打印/扫描','家用电器']},
{name:'家居家纺', areaList:['草坪和花园用品','地毯窗帘等家纺','帷幕','室内装潢壁炉','屏风','家庭装饰','花木栽种用品']},
{name:'建材', areaList:['油漆','清漆用品','大型建材卖场卖场','木材与建材商店','玻璃','墙纸']},
{name:'鲜花/盆栽', areaList:['鲜花/盆栽']}
]},

{name:'生活/咨询服务', cityList:[
{name:'婚庆/摄影', areaList:['婚礼策划','婚纱/礼服','婚车租赁','旅拍/本地婚纱摄影','本地婚纱摄影','儿童摄影','孕妇摄影','艺术写真','跟拍','证件照','商业摄影']},
{name:'亲子服务', areaList:['亲子游泳','亲子服务','产后恢复','月子服务']},
{name:'家政/维修服务', areaList:['洗车','拖车','维修','保养','汽车美容','送水站','搬家','回收','开锁','管道疏通','家电维修','焊接维修','家居维修、翻新','家政','灭虫/消毒','清洁/保养/门卫']},
{name:'装饰/设计', areaList:['装饰/设计']},
{name:'农业合作与农具', areaList:['农业合作与农具']},
{name:'丧仪殡葬服务', areaList:['丧仪殡葬服务']},
{name:'广告/会展/活动策划', areaList:['广告/会展/活动策划']}
]},

{name:'教育/培训', cityList:[
{name:'教育/培训/考试缴费/学费', areaList:['早教中心','少儿外语','少儿才艺','职业技术培训','外语','音乐','升学辅导','体育','美术','留学','驾校','兴趣生活','成人教育/函授','商业/文秘学校','福清市','长乐市']},
{name:'私立院校', areaList:['中小学校','大学与学院','儿童保育/学前']},
{name:'洗衣', areaList:['洗衣家纺','鞋帽清洗','奢侈品养护','自助洗衣']},
]},

{name:'医疗', cityList:[
{name:'私立/民营医院/诊所', areaList:['社区医院','正骨医生','按摩医生','眼科医疗服务','手足病医疗服务','护理/照料服务','中医','齿科','药店','急救服务','妇幼医院','体检中心']}
]},

{name:'票务/旅游', cityList:[
{name:'旅馆/酒店/度假区', areaList:['客栈单体','客栈连锁','酒店单体','酒店连锁','酒店式公寓','度假别墅服务','运动和娱乐露营','活动房车和野营']},
{name:'票务', areaList:['交通票务']}
]},

{name:'娱乐/健身服务', cityList:[
{name:'游艺厅/KTV/网吧', areaList:['电影院','私人影院']},
]},

{name:'通信', cityList:[
{name:'话费充值与缴费', areaList:['话费充值与缴费']},
{name:'付费电话', areaList:['付费电话']},
]},

{name:'网络虚拟服务', cityList:[
{name:'软件/建站/技术开发', areaList:['软件/建站/技术开发']},
{name:'游戏', areaList:['游戏']},
{name:'在线图书/视频/音乐', areaList:['在线图书/视频/音乐']},
{name:'网络推广/网络广告', areaList:['网络推广/网络广告']}
]},

]
},




{_area:"事业单位",Allcity:[

{name:'教育/培训', cityList:[
{name:'公立院校', areaList:['中小学校','大学与学院','儿童保育/学前']},
]},

{name:'医疗', cityList:[
{name:'公立医院', areaList:['手足病医疗服务','社区医院','眼科医疗服务','护理/照料服务','公立医院','中医','齿科','药店','急救服务','妇幼医院','体检中心']},
]},

{name:'政府/社会组织', cityList:[
{name:'政府服务', areaList:['法庭费用','社区医院','行政费用和罚款','保释金','税务/海关医院','社会保障服务','使领馆','国家邮政','政府采购','政府贷款']},
]},

{name:'生活缴费', cityList:[
{name:'水电煤缴费/交通罚款等生活缴费', areaList:['交通罚款','电力缴费','煤气缴费','自来水缴费']},
{name:'路桥通行费', areaList:['路桥通行费']},
{name:'物业管理费', areaList:['物业管理费']},
{name:'停车缴费', areaList:['停车缴费']},
]},

]
},


];