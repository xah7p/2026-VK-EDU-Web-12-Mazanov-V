(function () {
  document.addEventListener("DOMContentLoaded", function () {
    var input = document.getElementById("id_avatar");
    var img = document.getElementById("js-avatar-preview");
    if (!input || !img) {
      return;
    }
    var initialSrc = img.getAttribute("data-initial-src") || img.src;

    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      if (!file) {
        img.src = initialSrc;
        return;
      }
      var reader = new FileReader();
      reader.onload = function (e) {
        img.src = e.target.result;
      };
      reader.readAsDataURL(file);
    });
  });
})();
