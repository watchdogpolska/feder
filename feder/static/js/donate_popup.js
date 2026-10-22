function fadeIn(el) {
  el.style.display = "block";
  requestAnimationFrame(function () {
    requestAnimationFrame(function () {
      el.style.opacity = "1";
    });
  });
}

function fadeOut(el) {
  el.style.opacity = "0";
  window.setTimeout(function () {
    el.style.display = "none";
  }, 400);
}

(function () {
  var alreadyDonated = Cookies.get("alreadyDonated");
  var popupShown = Cookies.get("popupShown");
  // // for debug purposes
  // if (Cookies.get('popupShown')) {
  //     Cookies.remove('popupShown');
  //     Cookies.remove('alreadyDonated');
  // };
  if (!(alreadyDonated || popupShown)) {
    // Show the popup if the 'popupShown' or 'alreadyDonated' cookie is not set
    fadeIn(document.getElementById("popup-container"));
  }

  function adjustPopupContainer() {
    var popupContainer = document.getElementById("popup-container");
    if (window.innerWidth < 1000) {
      popupContainer.style.whiteSpace = "normal";
      popupContainer.style.overflow = "auto";
      popupContainer.style.maxHeight = "90vh";
      popupContainer.style.maxWidth = "90vw";
    } else {
      popupContainer.style.whiteSpace = "nowrap";
    }
  }

  // Call adjustPopupContainer when the document is ready and when the window is resized
  adjustPopupContainer();
  window.addEventListener("resize", adjustPopupContainer);
})();

function closePopup() {
  fadeOut(document.getElementById("popup-container"));
  // Set a cookie to remember that the popup has been shown, expires in 1 day
  Cookies.set("popupShown", "true", { expires: 1 });
}

document
  .getElementById("alreadyDonated")
  .addEventListener("change", function () {
    if (this.checked) {
      Cookies.set("alreadyDonated", "true", { expires: 60 }); // expires in 60 days
    } else {
      Cookies.remove("alreadyDonated");
    }
  });
