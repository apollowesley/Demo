package com.kyl.ps.model.image;

import com.kyl.ps.util.BeanHolder;

/**
 * <p>Title: SortEnum.java</p>
 * <p>Description: com.kyl.ps.interfaces.controller.impl.product</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2014年11月27日
 *
 */
public enum FolderNameEnum {
	NAME_COOL(1, "cool", "image.folder.name.cool"), //骚货
	NAME_BRAND(2, "brand", "image.folder.name.brand"), //品牌
	NAME_RECOMMEND(3, "recommend", "image.folder.name.recommend"), //首页推荐
	NAME_RANKING(4, "ranking", "image.folder.name.ranking"), //排行
	NAME_CATRGORY(5, "category", "image.folder.name.category"), //随便逛目录
	NAME_NAVIGATION(6, "navigation", "image.folder.name.navigation"), //导航
	NAME_PACKAGE(7, "package", "image.foder.name.package"),//锦囊
	NAME_ACTIVITY(8, "activity", "image.foder.name.package"),//活动
	NAME_APK(9, "apk", "image.foder.name.package"),//APK
	NAME_ZIXUN_INFORMATION(10, "zixun", "image.foder.name.zixun");//APK
	
	 private final int    id;
     private final String field;
     private final String name;

     private FolderNameEnum(int id, String field, String name) {
         this.id = id;
         this.field = field;
         this.name = name;
     }

     public int getId() {
         return id;
     }

     public String getField() {
         return field;
     }

     public String getName() {
         return name;
     }

     public static String getNameByField(String field) {
         String res = null;
         FolderNameEnum[] arr = FolderNameEnum.values();
         for (FolderNameEnum t : arr) {
             if (field.equalsIgnoreCase(t.getField())) {
                 res = BeanHolder.getMessage(t.getName());
             }
         }

         return res;
     }
     
     public static FolderNameEnum getEnumByField(String field) {
         FolderNameEnum[] arr = FolderNameEnum.values();
         for (FolderNameEnum t : arr) {
             if (field.equalsIgnoreCase(t.getField())) {
                 return t;
             }
         }

         return null;
     }
}
