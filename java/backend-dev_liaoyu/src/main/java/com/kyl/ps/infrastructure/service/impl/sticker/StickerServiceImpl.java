package com.kyl.ps.infrastructure.service.impl.sticker;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.kyl.ps.infrastructure.dao.impl.sticker.StickerDao;
import com.kyl.ps.infrastructure.service.AbstractService;
import com.kyl.ps.model.manageruser.ManagerUser;
import com.kyl.ps.pojo.BaseInputMessage;

@Service
public class StickerServiceImpl extends AbstractService {

	@Autowired
	private StickerDao stickerDao;

	@Override
	public void invoke() throws Exception {
	}

	@Override
	protected void beforeInvoke() throws Exception {

	}

	@Override
	protected void afterInvoke() throws Exception {

	}

	public void insertTemplate(BaseInputMessage inMessage) throws Exception {
		stickerDao.insertTemplate(StickerDao.class, inMessage);
	}
	public void updateCreation(BaseInputMessage inMessage) throws Exception {
		stickerDao.updateCreation(StickerDao.class, inMessage);
	}
	public void updateCreationByName(BaseInputMessage inMessage) throws Exception {
		stickerDao.updateCreationByName(StickerDao.class, inMessage);
	}

	public List<Map<String, Object>> selectTemplates(BaseInputMessage inMessage) {
		return stickerDao.selectTemplates(StickerDao.class, inMessage);
	}

	public void insertCreationsRetKey(ManagerUser managerUser, int areaCode) throws Exception {
		// 该批次要生成的贴纸卷数
		int rolls = managerUser.getRolls();
		Map<String, Object> map = new HashMap<String, Object>();
		map.put("expiration_time", managerUser.getExpirationTime());
		map.put("creator_id", managerUser.getAccountId());
		for (int i = 1; i <= rolls; i++) {
			// 创建批次里的每一卷
			stickerDao.insertCreationsRetKey(StickerDao.class, managerUser);
			int keyId = managerUser.getKeyId();

			// 每一卷生成罗马标记， 记录贴纸信息
			String remoSign = genRemoSign(i);
			//  插入贴纸信息
			map.put("creation_id", keyId);
			map.put("roll_tag", remoSign);
			
			// TODO sticker_id  按区域生成，  查询当前区域编号对应贴纸的的最大使用值
			map.put("prefix_code", areaCode);
			int count = stickerDao.selectStickerCountByAreaCode(StickerDao.class,map);
			
			
			int stickerId = areaCode * 10000000 + count + 1;
			map.put("prefix_code", areaCode);
			map.put("count", count + 1);
			map.put("sticker_id", stickerId);
			stickerDao.insertStickers(StickerDao.class, map);
		}
	}

	
	
	
	// 根据数字生成对应的罗马标记
	public static String genRemoSign(int num) {
		String remoSign = "";
		String count = String.valueOf(num % 10);
		switch (count) {
		case "1":
			remoSign = "Ⅰ";
			break;
		case "2":
			remoSign = "Ⅱ";
			break;
		case "3":
			remoSign = "Ⅲ";
			break;
		case "4":
			remoSign = "Ⅳ";
			break;
		case "5":
			remoSign = "Ⅴ";
			break;
		case "6":
			remoSign = "Ⅵ";
			break;
		case "7":
			remoSign = "Ⅶ";
			break;
		case "8":
			remoSign = "Ⅷ";
			break;
		case "9":
			remoSign = "Ⅸ";
			break;
		case "0":
			remoSign = "Ⅹ";
			break;
		}
		return remoSign;
	}

	public List<Map<String, Object>> selectCreations(BaseInputMessage inMessage) {
		return stickerDao.selectCreations(StickerDao.class, inMessage);
	}
	public List<Map<String, Object>> selectAllCreations(BaseInputMessage inMessage) {
		return stickerDao.selectAllCreations(StickerDao.class, inMessage);
	}

	public List<Map<String, Object>> selectStickers(BaseInputMessage inMessage) {
		return stickerDao.selectStickers(StickerDao.class, inMessage);
	}
	public List<Map<String, Object>> selectStickersBycreationName(BaseInputMessage inMessage) {
		return stickerDao.selectStickersBycreationName(StickerDao.class, inMessage);
	}
	public int selectStickersCount(BaseInputMessage inMessage) {
		return stickerDao.selectStickersCount(StickerDao.class, inMessage);
	}
	public int selectCreationsCount(BaseInputMessage inMessage) {
		return stickerDao.selectCreationsCount(StickerDao.class, inMessage);
	}
	
	
	@SuppressWarnings("unchecked")
	public int selectAreaPrefixCode(BaseInputMessage inMessage) {
		return stickerDao.selectAreaPrefixCode(StickerDao.class, inMessage.getRequestMap());
	}
}
