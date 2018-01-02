package com.demo.file;

import java.io.IOException;

public class 文件解密 {
	public static void main(String[] args) throws IOException {
		
		String fileAllNameZip = "D:/filedes/C19_BANKOUTORINPR_JHALIPAY_201709080001.zip.ret"; // 待解密的压缩文件完整路径
		String fileAllNameTxt = "D:/fileyzy/C19_BANKOUTORINPR_JHALIPAY_201709080001.txt.ret"; // 解密后的文件完整路径
		String key = "182e8a57b4f6139b3a5de9g4";//加密key
		TripleDes.makeUnZipfile(fileAllNameZip, fileAllNameTxt, key);
	}
}
