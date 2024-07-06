class AlbumView extends HTMLElement {
  constructor() { super(); }
  connectedCallback() { this.rebuild(); }
  attributeChangedCallback() { this.rebuild(); }

  rebuild() {
    for (const url of albumFileList) {
      const img = document.createElement('img');
      img.src = url;
      img.height = 400;
      this.appendChild(img);
    }
  }
}

window.addEventListener(
    'load', () => customElements.define('album-view', AlbumView));
