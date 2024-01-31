  // 获取画廊和加载提示的元素
  const gallery = document.getElementById('gallery');
  const loading = document.getElementById('loading');

  let loadingPhotos = false; // 是否正在加载图片
  let photos = []; // 存储所有图片数据
  let loadedPhotos = 0; // 已加载的图片数量


  async function loadPhotos() {
    if (loadingPhotos) return; // 如果正在加载，则直接返回
    loadingPhotos = true; // 设置加载状态
  
    try {
      const response = await fetch(photosJsonUrl);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      photos = await response.json();
      photos = photos.sort(() => Math.random() - 0.5);
      loadMorePhotos(); // 加载第一批图片
    } catch (error) {
      console.error('Loading photos failed:', error);
    } finally {
      loadingPhotos = false; // 重置加载状态
    }
  }

// 按需加载更多图片
function loadMorePhotos() {
  const photosToLoad = photos.slice(loadedPhotos, loadedPhotos + 5); // 每次加载5张图片
  photosToLoad.forEach(photo => {
    const imgContainer = document.createElement('div');
    imgContainer.className = 'image-container';
    imgContainer.style.position = 'relative';

    // 假设竖版图片的文件名中包含 "_v"
    if (photo.filename.includes('_v')) {
      imgContainer.style.gridColumn = 'span 1'; // 占据一列
      imgContainer.style.gridRow = 'span 2'; // 占据两行
    } else {
      imgContainer.style.gridColumn = 'span 1'; // 占据一列
      imgContainer.style.gridRow = 'span 1'; // 占据一行
    }

    const img = document.createElement('img');
    img.src = `https://pinganyang.github.io/photos/${photo.filename}`;
    img.alt = photo.title;
    img.onload = () => {
      // 图片加载后，可以获取其尺寸
      const aspectRatio = img.naturalWidth / img.naturalHeight;
      if (aspectRatio > 1) {
          // 横向图片，可以在这里设置跨多列如果需要
          imgContainer.style.gridColumn = 'span 1';
      } else {
          // 竖向图片
          imgContainer.style.gridRow = 'span 2'; // 确保竖版图片跨足够的行
      }
    };

    const info = document.createElement('div');
    info.className = 'image-info';
    info.innerHTML = `
      <p>Camera Model: ${photo.CameraModel}</p>
      <p>Aperture: ${photo.Aperture}</p>
      <p>Exposure Time: ${photo.ExposureTime}</p>
      <p>ISO: ${photo.ISO}</p>
      <p>Exposure Bias Value: ${photo.ExposureBiasValue}</p>
      <p>Focal Length: ${photo.FocalLength}</p>
      <p>Location: ${photo.Location}</p>
      <a href="${photo.Link}" target="_blank">点击查看更多</a>
    `;

    imgContainer.appendChild(img);
    imgContainer.appendChild(info);
    document.querySelectorAll('.gallery .image-container').forEach(container => {
  let timeoutId_blur, timeoutId_info;

  container.addEventListener('mouseover', () => {
      clearTimeout(timeoutId_blur);
      clearTimeout(timeoutId_info);

      timeoutId_blur = setTimeout(() => {
          container.querySelector('img').style.filter = 'blur(4px)';
      }, 1000);
      timeoutId_info = setTimeout(() => {
          container.querySelector('.image-info').style.display = 'block';
      }, 1000);
  });

  container.addEventListener('mouseout', (event) => {
      if (!container.contains(event.relatedTarget)) {
          clearTimeout(timeoutId_blur);
          clearTimeout(timeoutId_info);
          container.querySelector('img').style.filter = '';
          container.querySelector('.image-info').style.display = 'none';
      }
  });
});

    document.querySelector('.gallery').appendChild(imgContainer);
  });

  loadedPhotos += photosToLoad.length; // 更新已加载的图片数量
  if (loadedPhotos >= photos.length) {
    window.removeEventListener('scroll', handleScroll); // 如果所有图片都已加载，移除滚动监听器
  }
}

// 处理滚动事件来按需加载图片
function handleScroll() {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) { // 触发加载的阈值
    loading.style.display = 'block'; // 显示加载提示
    loadMorePhotos(); // 加载更多图片
    loading.style.display = 'none'; // 隐藏加载提示
  }
}

window.addEventListener('scroll', handleScroll);

loadPhotos();

  // 监听滚动事件来加载更多图片
  window.addEventListener('scroll', () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
      // 当滚动到页面底部时，显示加载提示
      loading.style.display = 'block';

      // 模拟网络延迟
      setTimeout(() => {
        loadMorePhotos();
        loading.style.display = 'none';
      }, 1500);
    }
  });
  // 当文档加载完成后执行
    document.addEventListener('DOMContentLoaded', function () {
    // 获取模态框元素
    var modal = document.getElementById('myModal');
    // 获取模态框图片元素
    var modalImg = document.getElementById('img01');
    // 获取模态框的关闭按钮元素
    var captionText = document.getElementById('caption');
    var span = document.getElementsByClassName('close')[0];

    // 为每张图片添加点击事件
    document.getElementById('gallery').addEventListener('click', function(event) {
  // 检查被点击的元素是否是图片
    if (event.target && event.target.nodeName === "IMG") {
        modal.style.display = "block";
        modalImg.src = event.target.src;
        captionText.innerHTML = event.target.alt;
    }
    });

    // 点击模态框任意位置关闭
    modal.addEventListener('click', function (event) {
        if (event.target !== modalImg && event.target !== captionText) {
        modal.style.display = "none";
        }
    });

    // 点击关闭按钮关闭模态框
    span.addEventListener('click', function() {
        modal.style.display = "none";
    });
    });


  