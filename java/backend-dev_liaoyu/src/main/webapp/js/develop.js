// JavaScript Document
function show(t){
t.parentNode.style.height=t.parentNode.style.height=='auto'?'34px':'auto';
t.innerHTML=t.innerHTML=="展开"?"收回":"展开"
}
window.onload=function(){
    var divs = document.getElementsByTagName("DIV");
    for(var i=0;i<divs.length;i++){
        if(divs[i].id=="box"){
            if(divs[i].offsetHeight>34){
                divs[i].style.height = "34px";
            }else{
                divs[i].firstChild.style.display = "none";
            }
        }
    }
};