// 获取模态框元素
var modal = document.getElementById('myModal');

// 获取图片插入到模态框 - 使用它的 "alt" 文本作为标题
var img = document.getElementById('myImg');
var modalImg = document.getElementById('img01');
var captionText = document.getElementById('caption');
img.onclick = function(){
  modal.style.display = "block";
  modalImg.src = this.src;
  captionText.innerHTML = this.alt;
}

// 获取 <span> 元素，设置关闭模态框的功能
var span = document.getElementsByClassName('close')[0];
span.onclick = function() { 
  modal.style.display = "none";
}

// 应用于画廊中的所有图片
document.querySelectorAll('.gallery img').forEach(item => {
  item.onclick = function(){
    modal.style.display = "block";
    modalImg.src = this.src;
    captionText.innerHTML = this.alt;
  }
});
