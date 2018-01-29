
$().ready(function(){
	//-------------制约日期--------------
	$('#create_at_start').datetimepicker({
        language: "zh-CN",
		format: "yyyy-mm-dd",
		autoclose: true,
		minView: "month",
		maxView: "decade",
		endDate: new Date(),
		todayBtn: true
	}).on("click",function(ev){
		$("#create_at_start").datetimepicker("setEndDate", $("#create_at_end").val());
	});
	$('#create_at_end').datetimepicker({
        language: "zh-CN",
		format: "yyyy-mm-dd",
		autoclose: true,
		minView: "month",
		maxView: "decade",
		endDate: new Date(),
		todayBtn: true
	}).on("click",function(ev){
		$("#create_at_end").datetimepicker("setStartDate", $("#create_at_start").val());
	});

	//-------------制约月--------------
	$('#create_at_start_moon').datetimepicker({
        language: 'zh-CN',
		format: 'yyyy-mm',
		autoclose: true,
		todayBtn: true,
		startView: 'year',
		minView:'year',
		maxView:'decade'
	}).on("click",function(ev){
		$("#create_at_start").datetimepicker("setEndDate", $("#create_at_end").val());
	});
	$('#create_at_end_moon').datetimepicker({
        language: 'zh-CN',
		format: 'yyyy-mm',
		autoclose: true,
		todayBtn: true,
		startView: 'year',
		minView:'year',
		maxView:'decade'
	}).on("click",function(ev){
		$("#create_at_end").datetimepicker("setStartDate", $("#create_at_start").val());
	});

	//--------------订单完成时间----------------//-------------制约月--------------
	$('#complete_at_start').datetimepicker({
        language: "zh-CN",
		format: "yyyy-mm-dd hh:ii:00",
		autoclose: true,
		endDate: new Date(),
		todayBtn: true
	}).on("click",function(ev){
		$("#complete_at_start").datetimepicker("setEndDate", $("#complete_at_end").val());
	});
	$('#complete_at_end').datetimepicker({
        language: "zh-CN",
		format: "yyyy-mm-dd hh:ii:00",
		autoclose: true,
		endDate: new Date(),
		todayBtn: true
	}).on("click",function(ev){
		$("#complete_at_end").datetimepicker("setStartDate", $("#complete_at_start").val());
	});

});
