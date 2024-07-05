function emptyDiv(n) {
  while (n.hasChildNodes()) n.removeChild(n.lastChild);
}

function newElement(type, parent, classes = []) {
  const n = document.createElement(type);
  for (const cls of classes) n.classList.add(cls);
  if (parent != null) parent.appendChild(n);
  return n;
}

function newImage(url, classes = []) {
  return new Promise((resolve, reject) => {
    const img = newElement('img', null, classes);
    img.src = url;
    img.addEventListener('load', () => resolve(img));
  });
}

let _images = null;
function getImages() {
  if (_images != null) return _images;
  const imgPromises = [];
  for (const filename of albumFileList) {
    imgPromises.push(newImage(filename));
  }
  return _images = Promise.all(imgPromises).then((images) => {
    return _images = images;
  });
}

class AlbumViewImpl {
  constructor(node) {
    this.node = node;
    this.epoch = 0;
  }

  rebuild() {
    ++this.epoch;
    const myEpoch = this.epoch;
    window.setTimeout(async () => {
      let images = getImages();
      if (this.epoch != myEpoch) return;
      emptyDiv(this.node);
      if (images instanceof Promise) {
        this.node.classList.add('loading');
        images = await images;
        if (this.epoch != myEpoch) return;
        this.node.classList.remove('loading');
      }
      // TODO: Create columns.
      for (const img of images) {
        this.addImage(img);
      }
    }, 0);
  }

  addImage(img) { this.node.appendChild(img); }
}

class AlbumView extends HTMLElement {
  constructor() {
    super();
    this.impl = new AlbumViewImpl(this);
  }

  connectedCallback() { this.impl.rebuild(); }
  attributeChangedCallback() { this.impl.rebuild(); }
}

window.addEventListener(
    'load', () => customElements.define('album-view', AlbumView));
