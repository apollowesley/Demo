package com.demo.file;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;
import org.apache.commons.io.IOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public  class TripleDes {
	private static final Logger log = LoggerFactory.getLogger(TripleDes.class);

	/**
	 * 将文件压缩并加密
	 * 
	 * @param fileAllNameZip 加密后的文件完整路径
	 * @param fileName 待加密文件名
	 * @param fileAllName 待加密文件完整路径
	 * @throws IOException
	 * @throws TranFailException
	 */
	public static void makeZipfile(String fileAllNameZip, String fileName, String fileAllName,String threeDesKey) throws IOException {
		log.info("将文件：{}加密到：{}，开始", fileAllName,fileAllNameZip);
		// 将生成文件压缩并加密。
		OutputStream out = null;
		FileOutputStream fos = null;
		FileInputStream fis = null;
		try {
			fos = new FileOutputStream(fileAllNameZip);
			out = alipayUploadOuputStream(threeDesKey, fos, fileName);
			fis = new FileInputStream(fileAllName);
			IOUtils.copy(fis, out);
		} catch (FileNotFoundException e) {
			log.error(e.getMessage());
			log.error("文件压缩加密失败", e);
			throw e;
		} catch (IOException e) {
			log.error(e.getMessage());
			log.error("文件压缩加密失败", e);
			throw e;
		} finally {
			if(null != fis){
				try {
					fis.close();
				} catch (IOException e) {
					log.error(e.getMessage(), e);
					throw e;
				}
			}
			if(null != out){
				try {
					out.close();
				} catch (IOException e) {
					log.error("关闭流发生异常", e);
				}
			}
			if(null != fos){
				try {
					fos.close();
				} catch (IOException e) {
					log.error(e.getMessage(), e);
					throw e;
				}
			}
		}
		log.info("将文件：{}加密到：{}，完成", fileAllName,fileAllNameZip + File.separator + fileName);
	}

	private static OutputStream alipayUploadOuputStream(String threeDesKey, OutputStream fileOuputStream, String zipEntryName)
			throws IOException {
		// 设置流以加密模式输出
		OutputStream encryptOutPutStream = TripleDesTool.encryptMode(threeDesKey, fileOuputStream);
		// 设置流以压缩模式输出
		ZipOutputStream zipOutPutStream = new ZipOutputStream(encryptOutPutStream);
		zipOutPutStream.putNextEntry(new ZipEntry(zipEntryName));
		return zipOutPutStream;

	}

	/**
	 * 该方法对一个加密的Zip文件进行解密输出。
	 * @param fileAllNameZip 待解密的压缩文件完整路径
	 * @param fileAllNameTxt 解密后的文件完整路径
	 * @throws IOException
	 * @author CAO_Z
	 * @sinece 2015年11月11日 下午5:32:06
	 */
	public static void makeUnZipfile(String fileAllNameZip, String fileAllNameTxt,String threeDesKey) throws IOException {
		log.info("将文件：{}解密到：{}，开始", fileAllNameZip,fileAllNameTxt);
		// 对一个加密的Zip文件进行解密输出。
		InputStream in = null;
		FileOutputStream fos = null;
		FileInputStream fis = null;
		try {
			fis = new FileInputStream(fileAllNameZip);
			in = alipayDownloadInputStream(threeDesKey, fis);
			fos = new FileOutputStream(new File(fileAllNameTxt));
			IOUtils.copy(in, fos);
		} catch (FileNotFoundException e) {
			log.error("文件解密解压失败,文件路径：" + fileAllNameZip + "解密路径：" + fileAllNameTxt);
			log.error("文件解密解压失败", e);
			throw e;
		} catch (IOException e) {
			log.error("文件解密解压失败,文件路径：" + fileAllNameZip + "解密路径：" + fileAllNameTxt);
			log.error("文件解密解压失败", e);
			throw e;
		} finally {
			try {
				if (null != fos) {
					fos.close();
				}
				if (null != in) {
					in.close();
				}
				if (null != fis) {
					fis.close();
				}
			} catch (IOException e) {
				log.error("文件解密失败，关闭流失败");
				throw e;
			}
		}
		log.info("将文件：{}解密到：{}，完成", fileAllNameZip,fileAllNameTxt);
	}

	private static InputStream alipayDownloadInputStream(String threeDesKey, InputStream fileInputStream) throws IOException {
		InputStream decryptInputStream = TripleDesTool.decryptMode(threeDesKey, fileInputStream);
		// 设置流以解密模式输出
		ZipInputStream zipIn = new ZipInputStream(decryptInputStream);
		if (zipIn.getNextEntry() == null) {
			return null;
		}
		return zipIn;
	}
}
