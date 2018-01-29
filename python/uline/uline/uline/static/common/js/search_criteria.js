/**
 *公用搜索条件查询方法
 * 只适用于input,select搜索条件框
 * 使用方法：在input,select标签添加 class="search-criteria"
 */

;(function(){
    var _params='';
    $('.search-criteria').each(function(){
        if(!$(this).attr('disabled')) {
            _params += '&' + $(this).attr('name') + '=' + $(this).val();
        }
    });
    var _href=$('#pagination a');
    for (var i = 0; i < (_href.length - 3); i++) {
        var item_href= _href[i].getAttribute('href');
        if (typeof(item_href) != 'undefined' || item_href != null && item_href && item_href.match(/\?p=/)) {
            _href[i].setAttribute('href', item_href + _params);
        }
    }
})(jQuery);









