/**
 * Created by base on 19/7/17.
 * 金额格式化  .formatting-money
 */
function formatNumber(num, precision, separator) {
    var parts;
    // 判断是否为数字
    if (!isNaN(parseFloat(num)) && isFinite(num)) {
        num = Number(num);
        num = (typeof precision !== 'undefined' ? num.toFixed(precision) : num).toString();
        parts = num.split('.');
        parts[0] = parts[0].toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1' + (separator || ','));

        return parts.join('.');
    }
}

$('.formatting-money').each(function(){
    var moneyNum=$(this).text();
    if(!(isNaN(moneyNum))){
        moneyNum=formatNumber(moneyNum);
        if($(this).text() != '' ){
            $(this).text(moneyNum);
        }
    }

});