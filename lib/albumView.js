function emptyDiv(n) {
  while (n.hasChildNodes()) n.removeChild(n.lastChild);
}

class Image {
  constructor(node) {
    this.node = node;
    this.width = node.width;
    this.height = node.height;
  }
};

function newImage(url) {
  return new Promise((resolve, reject) => {
    const img = document.createElement('img');
    img.addEventListener('load', () => resolve(new Image(img)));
    img.src = url;
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

    this.loader = document.createElement('div');
    this.loader.classList.add('loader');
  }

  rebuild() {
    ++this.epoch;
    const myEpoch = this.epoch;
    window.setTimeout(async () => {
      let images = getImages();
      if (this.epoch != myEpoch) return;
      emptyDiv(this.node);
      if (images instanceof Promise) {
        this.node.appendChild(this.loader);
        images = await images;
        if (this.epoch != myEpoch) return;
        this.node.removeChild(this.loader);
      }
      for (const img of images) this.addImage(img);
    }, 0);
  }

  addImage(img) {
    img.node.height = 400;
    this.node.appendChild(img.node);
  }
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
