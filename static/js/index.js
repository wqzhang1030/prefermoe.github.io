function copyBibTeX() {
  const bibtexElement = document.getElementById('bibtex-code');
  const button = document.querySelector('.copy-bibtex-btn');

  if (!bibtexElement || !button) {
    return;
  }

  const copyText = button.querySelector('.copy-text');
  const bibtex = bibtexElement.textContent.trim();

  const showCopied = () => {
    button.classList.add('copied');
    if (copyText) {
      copyText.textContent = 'Copied';
    }

    window.setTimeout(() => {
      button.classList.remove('copied');
      if (copyText) {
        copyText.textContent = 'Copy';
      }
    }, 1600);
  };

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(bibtex).then(showCopied).catch(() => {
      fallbackCopy(bibtex);
      showCopied();
    });
    return;
  }

  fallbackCopy(bibtex);
  showCopied();
}

function fallbackCopy(text) {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.setAttribute('readonly', '');
  textArea.style.position = 'absolute';
  textArea.style.left = '-9999px';
  document.body.appendChild(textArea);
  textArea.select();
  document.execCommand('copy');
  document.body.removeChild(textArea);
}
