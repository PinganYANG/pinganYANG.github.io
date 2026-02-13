const gallery = document.getElementById('gallery');
const loading = document.getElementById('loading');

// --- 配置参数 ---


const IDEAL_COL_WIDTH = 450;
const BATCH_SIZE = 20;
const MAX_HEIGHT_DIFF = 50;

// 【普通缝隙】随机素材池 (竖构图或方构图)
// 建议放 3-5 个不同的旋转石膏像 GIF
const FILLER_GIFS_NORMAL = [
  'https://pinganyang.github.io/assets/Cinematic_3d_animation_202602132254.gif',
  'https://pinganyang.github.io/assets/Constraint_use_the_202602132217.gif',
  'https://pinganyang.github.io/assets/Constraint_use_the_202602132242.gif',
  'https://pinganyang.github.io/assets/Constraint_use_the_202602132249.gif'
];

// 【扁平缝隙】专用素材 (横构图)
// 比如一个卧倒的石膏像，或者流动的纹理，适合高度较小的缝隙
const FILLER_GIF_FLAT = 'https://pinganyang.github.io/assets/Cinematic_3d_animation_202602132259.gif';

// 【扁平阈值】
// 如果缝隙的高度小于宽度的 0.6 倍，就认为是“扁缝隙”
const FLAT_GAP_THRESHOLD = 0.6;

// 状态变量
let photosData = [];
let loadedCount = 0;
let colHeights = [];
let colCount = 0;
let colWidth = 0;
let gaps = [];

function init() {
  createLightboxDOM();
  calculateLayout();
  window.addEventListener('resize', debounce(() => {
    calculateLayout();
    repositionAll();
  }, 200));
  window.addEventListener('scroll', handleScroll);
  loadPhotos();
}

function calculateLayout() {
  const w = gallery.clientWidth;
  colCount = Math.max(1, Math.floor(w / IDEAL_COL_WIDTH));
  colWidth = w / colCount;

  if (colHeights.length !== colCount) {
    colHeights = new Array(colCount).fill(0);
    gaps = [];
  }
}

async function loadPhotos() {
  if (loading.getAttribute('data-loading') === 'true') return;
  loading.setAttribute('data-loading', 'true');
  loading.style.display = 'block';

  try {
    if (photosData.length === 0) {
      const res = await fetch('./photos_info.json?v=' + new Date().getTime());
      photosData = await res.json();
      photosData.sort(() => Math.random() - 0.5);
    }
    renderBatch();
  } catch (e) {
    console.error("加载失败:", e);
    loading.innerText = '加载出错';
  } finally {
    if (loadedCount >= photosData.length) {
      loading.innerText = '--- End ---';
      // 大结局：再次确保所有缝隙都被填满
      fillAllRemainingGaps();
    } else {
      loading.style.display = 'none';
      loading.setAttribute('data-loading', 'false');
    }
  }
}

function renderBatch() {
  const end = Math.min(loadedCount + BATCH_SIZE, photosData.length);
  if (loadedCount >= end) return;

  const batch = photosData.slice(loadedCount, end);

  // 1. 先让照片挑位置
  batch.forEach(photo => {
    let w = photo.width;
    let h = photo.height;
    if (!w || !h) { w = 3000; h = 2000; }

    const ratio = w / h;
    const isWide = ratio > 1.6;

    const item = {
      data: photo,
      ratio: ratio,
      isWide: isWide,
      element: createItemElement(photo, ratio, isWide)
    };

    placeItem(item);
  });

  loadedCount += batch.length;

  // 2. 【核心修改】照片挑剩下的缝隙，立刻全部用 GIF 填满
  // 不再等待，不再挑剔缝隙大小，统统填上
  fillAllRemainingGaps();

  if (Math.min(...colHeights) < window.innerHeight) {
    requestAnimationFrame(renderBatch);
  }
}

// 【核心修改】无差别填缝函数
// 【核心修改】智能填缝函数
function fillAllRemainingGaps() {
  if (gaps.length === 0) return;

  // 倒序遍历
  for (let i = gaps.length - 1; i >= 0; i--) {
    const gap = gaps[i];

    // 只要有高度就填
    if (gap.height > 0) {
      const div = document.createElement('div');
      div.className = 'image-container filler-item';

      // --- 智能选择逻辑 ---
      let selectedSrc = '';

      // 计算缝隙比例 (高度 / 宽度)
      const gapRatio = gap.height / colWidth;

      if (gapRatio < FLAT_GAP_THRESHOLD) {
        // 情况 A: 缝隙很扁 -> 使用专用素材
        selectedSrc = FILLER_GIF_FLAT;
        console.log(`填充扁缝隙 (H:${Math.round(gap.height)}px)`);
      } else {
        // 情况 B: 普通缝隙 -> 从数组中随机选一个
        const randomIndex = Math.floor(Math.random() * FILLER_GIFS_NORMAL.length);
        selectedSrc = FILLER_GIFS_NORMAL[randomIndex];
      }

      // 生成 DOM
      div.innerHTML = `
                <div class="image-content-wrapper">
                    <img src="${selectedSrc}" alt="decoration" 
                         style="width: 100%; height: 100%; object-fit: contain;">
                </div>
            `;

      setStyles(div, gap.col * colWidth, gap.top, colWidth, gap.height);

      // 填完移除
      gaps.splice(i, 1);
    }
  }
}

// 排版逻辑
function placeItem(item) {
  let bestGapIndex = -1;
  let minGapDiff = Infinity;

  // 【核心修改】移除了“清理扁缝隙”的代码
  // 之前这里会删除 MIN_GAP_ASPECT_RATIO < 0.5 的缝隙
  // 现在保留它们，照片填不进去没关系，后面会有 GIF 来填

  if (!item.isWide && gaps.length > 0) {
    for (let i = 0; i < gaps.length; i++) {
      const gap = gaps[i];
      const imgIdealHeight = colWidth / item.ratio;
      const diff = Math.abs(imgIdealHeight - gap.height);

      // 照片依然保持挑剔，只进合适的坑
      if (diff <= MAX_HEIGHT_DIFF) {
        if (diff < minGapDiff) {
          minGapDiff = diff;
          bestGapIndex = i;
        }
      }
    }
  }

  if (bestGapIndex !== -1) {
    const gap = gaps[bestGapIndex];
    setStyles(item.element, gap.col * colWidth, gap.top, colWidth, gap.height);
    gaps.splice(bestGapIndex, 1);
  } else {
    placeAtBottom(item);
  }
}

function placeAtBottom(item) {
  let span = (item.isWide && colCount > 1) ? 2 : 1;
  let targetCol = 0;
  let targetTop = 0;

  if (span === 1) {
    let minH = Math.min(...colHeights);
    targetCol = colHeights.indexOf(minH);
    targetTop = minH;

    const h = colWidth / item.ratio;
    colHeights[targetCol] += h;
    setStyles(item.element, targetCol * colWidth, targetTop, colWidth, h);

  } else {
    let minPairH = Infinity;
    let idx = 0;
    for (let i = 0; i < colCount - 1; i++) {
      const maxH = Math.max(colHeights[i], colHeights[i + 1]);
      if (maxH < minPairH) { minPairH = maxH; idx = i; }
    }
    targetCol = idx;
    targetTop = minPairH;

    if (Math.floor(colHeights[targetCol]) < Math.floor(targetTop)) {
      gaps.push({ col: targetCol, top: colHeights[targetCol], height: targetTop - colHeights[targetCol] });
    }
    if (Math.floor(colHeights[targetCol + 1]) < Math.floor(targetTop)) {
      gaps.push({ col: targetCol + 1, top: colHeights[targetCol + 1], height: targetTop - colHeights[targetCol + 1] });
    }

    const h = (colWidth * 2) / item.ratio;
    colHeights[targetCol] = targetTop + h;
    colHeights[targetCol + 1] = targetTop + h;
    setStyles(item.element, targetCol * colWidth, targetTop, colWidth * 2, h);
  }

  gallery.style.height = Math.max(...colHeights) + 'px';
}

function setStyles(el, x, y, w, h) {
  el.style.width = w + 'px';
  el.style.height = h + 'px';
  el.style.transform = `translate3d(${x}px, ${y}px, 0)`;
  el.style.left = 0;
  el.style.top = 0;
  if (!el.isConnected) gallery.appendChild(el);
  requestAnimationFrame(() => el.style.opacity = 1);
}

function createItemElement(data, ratio, isWide) {
  const div = document.createElement('div');
  div.className = 'image-container';
  div.dataset.ratio = ratio;
  div.dataset.isWide = isWide;
  const imgSrc = `https://pinganyang.github.io/photos/${data.filename}`;
  div.innerHTML = `
        <div class="image-content-wrapper" style="background-color: #eee;">
            <img src="${imgSrc}" loading="lazy" alt="${data.title || ''}" style="opacity:0;transition:opacity 0.5s ease;" onload="this.style.opacity=1" onerror="this.parentElement.style.backgroundColor='#f8d7da'">
        </div>`;
  div.addEventListener('click', () => openLightbox(data, imgSrc));
  return div;
}

// 灯箱逻辑
function createLightboxDOM() {
  if (document.getElementById('lightbox')) return;
  const lightbox = document.createElement('div');
  lightbox.id = 'lightbox';
  lightbox.innerHTML = `<div id="lightbox-close">&times;</div><img src="" alt=""><div id="lightbox-info"><h3 id="lb-title"></h3><p id="lb-meta"></p></div>`;
  document.body.appendChild(lightbox);
  lightbox.addEventListener('click', (e) => { if (e.target !== lightbox.querySelector('img')) closeLightbox(); });
}
function openLightbox(data, src) {
  const lightbox = document.getElementById('lightbox');
  const img = lightbox.querySelector('img');
  const title = document.getElementById('lb-title');
  const meta = document.getElementById('lb-meta');
  img.src = src;
  title.innerText = data.title || '';
  const metaParts = [];
  if (data.CameraModel) metaParts.push(data.CameraModel.trim());
  if (data.FocalLength) metaParts.push(data.FocalLength.trim());
  if (data.Aperture) metaParts.push(data.Aperture.trim());
  if (data.ExposureTime) metaParts.push(data.ExposureTime.trim());
  if (data.ISO) metaParts.push("ISO " + data.ISO.trim());
  meta.innerText = metaParts.join('  |  ');
  lightbox.classList.add('active');
  document.body.style.overflow = 'hidden';
}
function closeLightbox() {
  const lightbox = document.getElementById('lightbox');
  lightbox.classList.remove('active');
  document.body.style.overflow = '';
}

function repositionAll() {
  colHeights = new Array(colCount).fill(0);
  gaps = [];
  const els = Array.from(document.querySelectorAll('.image-container'));
  els.forEach(el => {
    if (el.classList.contains('filler-item')) { el.remove(); return; }
    const ratio = parseFloat(el.dataset.ratio);
    const isWide = el.dataset.isWide === 'true';
    const item = { element: el, ratio: ratio, isWide: isWide };
    placeAtBottom(item);
  });
  gallery.style.height = Math.max(...colHeights) + 'px';
}

function debounce(fn, t) {
  let timer;
  return () => { clearTimeout(timer); timer = setTimeout(fn, t); }
}

function handleScroll() {
  if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 800) {
    loadPhotos();
  }
}

init();