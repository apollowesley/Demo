package com.kyl.ps.util;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Date;
import java.util.Map;

import org.apache.poi.hssf.usermodel.HSSFCell;
import org.apache.poi.hssf.usermodel.HSSFRow;
import org.apache.poi.hssf.usermodel.HSSFSheet;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;

public class ExcelUtil {

	
	 // 导出excel
	  public static Boolean  CreateExcel(String path, String fileName, String fileType, Map<String, Object> creation,String manager_name) {
	    Boolean flag = true;
	    int downloads = null==creation.get("downloads")?0:(int)creation.get("downloads");
	    downloads = downloads + 1;// 算上该次下载数
	    
	    // 创建一个工作簿
	    HSSFWorkbook workBook = new HSSFWorkbook();
	    // 创建一个工作表，名为：第一页
	    HSSFSheet sheet = workBook.createSheet("贴纸批次信息");

	    // 设置单元格的宽度(0:表示第一行的第一个单元格，1：第一行的第二个单元格)
	    sheet.setColumnWidth((short) 0, 4000);
	    sheet.setColumnWidth((short) 1, 4000);
	    sheet.setColumnWidth((short) 2, 3000);
	    sheet.setColumnWidth((short) 3, 8000);
	    sheet.setColumnWidth((short) 4, 3000);
	    sheet.setColumnWidth((short) 5, 15000);
	    sheet.setColumnWidth((short) 6, 8000);
	    sheet.setColumnWidth((short) 7, 4000);
	    sheet.setColumnWidth((short) 8, 3000);

	   
	      
	      // 创建一个单元格，从0开始
	      HSSFRow row = sheet.createRow((short) 0);
	      // 构造一个数组设置第一行之后的单元格
	      HSSFCell cell[] = new HSSFCell[9];
	      for (int i = 0; i < 9; i++) {
	        cell[i] = row.createCell(i);
	      }
	      cell[0].setCellValue("批次编号");
	      cell[1].setCellValue("印刷批次");
	      cell[2].setCellValue("每卷个数");
	      cell[3].setCellValue("到期时间");
	      cell[4].setCellValue("卷数");
	      cell[5].setCellValue("字符前缀");
	      cell[6].setCellValue("创建时间");
	      cell[7].setCellValue("创建者");
	      cell[8].setCellValue("下载次数");
	      
	      
	        HSSFRow dataRow = sheet.createRow(1);
	        HSSFCell data[] = new HSSFCell[9];
	        for (int j = 0; j < 9; j++) {
	          data[j] = dataRow.createCell(j);
	        }
	        data[0].setCellValue(null==creation.get("creation_id")?"":creation.get("creation_id").toString());
	        data[1].setCellValue(null==creation.get("name")?"":creation.get("name").toString());
	        data[2].setCellValue(null==creation.get("rolls_quantity")?"0":creation.get("rolls_quantity").toString());
	        data[3].setCellValue(null==creation.get("expiration_time")?"":DateUtils.date2StrInSecond((Date)creation.get("expiration_time")));
	        data[4].setCellValue(null==creation.get("rolls")?"0":creation.get("rolls").toString());
	        data[5].setCellValue(null==creation.get("prefix")?"":creation.get("prefix").toString());
	        data[6].setCellValue(null==creation.get("creation_time")?"":DateUtils.date2StrInSecond((Date)creation.get("creation_time")));
	        data[7].setCellValue(manager_name);
	        data[8].setCellValue(downloads);
	    

	    try {
	    // 输出成XLS文件 
	    File file = new File(path);
	    if(!file.exists()){
	    	file.mkdir();
	    }
	    FileOutputStream fos = new FileOutputStream(file+"/"+fileName + fileType);
	    // 写入数据，并关闭文件
	    workBook.write(fos);
	    fos.close();

	    } catch (FileNotFoundException e) {
	    e.printStackTrace();
	    flag = false;
	    } catch (IOException e) {
	    e.printStackTrace();
	    flag = false;
	    }
	    return flag;
	    }
	  
}
