package com.demo.file;

import java.io.IOException;

public class 文件加密 {
	public static void main(String[] args) throws IOException {
		//132e8a57b4f6139b3a5de9g4
		String fileAllNameZip = "D:/filedes/aaa.zip";//加密后的文件完整路径
		String fileName = "aaa.txt";//待加密文件名
		String fileAllName = "D:/filedes/aaa.txt";//待加密文件完整路径
		String key = "182e8a57b4f6139b3a5de9g4";//加密key
		TripleDes.makeZipfile(fileAllNameZip, fileName, fileAllName, key);
	}
}
