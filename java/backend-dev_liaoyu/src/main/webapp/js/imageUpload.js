$(function() {
	// 图片在线预览
	var i = 0;
	(function($) {
		jQuery.fn.extend({
			uploadPreview : function(opts) {
				opts = jQuery.extend({
					scalingWidth : 0,
					scalingHeight : 0,
					imgPreview : null,
					imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
					callback : function() {
						return false;
					}
				}, opts || {});
				var _self = this;
				var _this = $(this);
				var imgPreview = $(opts.imgPreview);
				// file按钮出发事件
				_this.change(function() {
					if (this.value) {
						if (!RegExp("\.(" + opts.imgType.join("|") + ")$", "i").test(this.value.toLowerCase())) {
							alert("图片类型必须是" + opts.imgType.join(",") + "中的一种");
							this.value = "";
							return false;
						}
						// 判断浏览器是否有FileReader接口
						if (typeof FileReader == 'undefined') {
							alert('请使用支持HTML5的浏览器,如IE10,Chrome,FireFox等.');
							return false;
						} else {
							oFReader = new FileReader();
							oFReader.onload = function(oFREvent) {
								imgPreview.attr('src', oFREvent.target.result);
							};
							var oFile = this.files[0];
							oFReader.readAsDataURL(oFile);
						}
						//setTimeout("autoScaling()", 100);
					}
					opts.callback();
				});
			}
		});
	})(jQuery);
	$('#input').uploadPreview({
		imgPreview : ".img",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
	$('#bannerInput').uploadPreview({
		imgPreview : ".bannerImg",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});

	$('#input1').uploadPreview({
		imgPreview : ".img1",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
	$('#input2').uploadPreview({
		imgPreview : ".img2",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
	$('#input3').uploadPreview({
		imgPreview : ".img3",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
	$('#input4').uploadPreview({
		imgPreview : ".img4",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
	$('#input5').uploadPreview({
		imgPreview : ".img5",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
	$('#input6').uploadPreview({
		imgPreview : ".img6",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
	$('#input7').uploadPreview({
		imgPreview : ".img7",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
	$('#input8').uploadPreview({
		imgPreview : ".img8",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
	$('#input9').uploadPreview({
		imgPreview : ".img9",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
	$('#input10').uploadPreview({
		imgPreview : ".img10",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
	$('#iosImageInput').uploadPreview({
		imgPreview : ".iosImage",
		imgType : [ "jpeg", "jpg", "bmp", "png", "gif" ],
		callback : function() {

		}
	});
});