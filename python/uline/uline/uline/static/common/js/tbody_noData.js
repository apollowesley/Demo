
$().ready(function(){

	//-------------table无数据判断--------------
	if($('#tbodyBox>tr').length == 0 ){
	   $('#tbodyBox').html('<tr class="tr_data"><td colspan="10">暂无数据</td></tr>')
   	}

   	//清空textarea内容
	var remarks = document.getElementById("turnDownInpt");
	if(remarks !== null){
		remarks.oninput = function() {myRemarks()};
	}
	function myRemarks() {
		var oImg = document.getElementsByClassName("turnDownImg")[0];
		oImg.onclick = function(){
			remarks.value = "";
			oImg.style.display = "none";
			remarks.focus();
		}
		if(remarks.value != ""){
			oImg.style.display = "block";
		}else{
			oImg.style.display = "none";
		};
	}

	//监听输入数字变化
	(function($) {
		$.fn.limitTextarea = function(opts) {
			var defaults = {
				maxNumber: 0, //开始
				position: 'top', //提示文字的位置，top：文本框上方，bottom：文本框下方
				onOk: function() {}, //输入后，字数未超出时调用的函数
				onOver: function() {} //输入后，字数超出时调用的函数
			}
			var option = $.extend(defaults, opts);
			this.each(function() {
				var _this = $(this);
				var info = '<div id="info"><b>' + (option.maxNumber + _this.val().length) + '</b>/500</div>';
				var fn = function() {
					var $info = $('#info');
					var extraNumber = option.maxNumber + _this.val().length;

					if (extraNumber >= 0) {
						$info.html('<b>' + extraNumber + '</b>/500');
						option.onOk();
					} else {
						$info.html('已经超出<b style="color:red;">' + (-extraNumber) + '</b>个字');
						option.onOver();
					}
				};
				switch (option.position) {
					case 'top':
						_this.before(info);
						break;
					case 'bottom':
					default:
						_this.after(info);
				}
				//绑定输入事件监听器
				if (window.addEventListener) { //先执行W3C
					_this.get(0).addEventListener("input", fn, false);
				} else {
					_this.get(0).attachEvent("onpropertychange", fn);
				}
				if (window.VBArray && window.addEventListener) { //IE9
					_this.get(0).attachEvent("onkeydown", function() {
						var key = window.event.keyCode;
						(key == 8 || key == 46) && fn(); //处理回退与删除
					});
					_this.get(0).attachEvent("oncut", fn); //处理粘贴
				}
			});
		}
	})(jQuery)
	//插件调用；
	$(function() {
		$('#turnDownInpt').limitTextarea({
			maxNumber: 0, //开始数字
			position: 'bottom', //提示文字的位置，top：文本框上方，bottom：文本框下方
			onOk: function() {
				$('#turnDownInpt').css('background-color', 'white');
			}, //输入后，字数未超出时调用的函数
			onOver: function() {
				$('#turnDownInpt').css('background-color', 'lightpink');
			} //输入后，字数超出时调用的函数，这里把文本区域的背景变为粉红色
		});
	});


	//银行后台确认驳回 关闭弹框
	$("#centDown").click(function(){
		$('#turnDown').modal('hide');
	})
});


  