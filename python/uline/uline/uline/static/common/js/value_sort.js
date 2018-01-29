/**
 * Created by liudachu on 19/5/17.
 * 按数组内某个字段排序
 */
function valueSort(order,sortBy){
    var ordAlpah = (order == 'asc') ? '>' : '<';
    var sortFun = new Function('a', 'b', 'return a.' + sortBy + ordAlpah + 'b.' + sortBy + '?1:-1');
    return sortFun;
}





