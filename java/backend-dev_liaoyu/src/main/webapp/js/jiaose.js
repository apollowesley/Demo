// JavaScript Document

function menus(str){
var obj, pic;
// 返回 str 对象和 picId 对象是否存在
if (document.getElementByIdx(str)){
obj=document.getElementByIdx(str); //obj 为 DIV 对象
  //pic 为 图片对象

if (obj.style.display == "none"){ //如果DIV对象的 display 样式值为 none 的话
obj.style.display = ""; //就将 display 的样式清空
//pic.src = "0001.gif"; //更改图片对象的路径
}else{
obj.style.display = "none";
//pic.src = "0000.gif";
}
}
}
 function   change(obj) 
  { 
  var   objs=document.getElementsByName(obj.name); 
  
   //如果取消选中某个子,则其父也取消选中
   for(var   i=0;   i<objs.length;   i++) 
  { 
  if(!obj.checked&&obj.id.substr(0,objs[i].id.length)==objs[i].id)
    objs[i].checked=false; 
  }
  //如果选中子,刚其父也被选中
 // for(var   i=0;   i<objs.length;   i++) 
 // { 
 // if(obj.checked&&obj.id.substr(0,objs[i].id.length)==objs[i].id)
 //   objs[i].checked=true; 
 // } 
  //如果选中父,则所有子都被选中
  for(var   i=0;   i<objs.length;   i++) 
  { 
  if(objs[i].id.substr(0,obj.id.length)==obj.id)
    objs[i].checked=obj.checked; 
  } 
  return   true; 
  }
