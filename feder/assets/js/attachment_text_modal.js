(function () {
    "use strict";

    var MODAL_ID = "attachmentTextModal";
    var BACKDROP_ID = "attachmentTextModalBackdrop";

    function openModal(title) {
        var modal = document.getElementById(MODAL_ID);
        if (!modal) return;

        var label = document.getElementById("attachmentTextModalLabel");
        if (label) label.textContent = title || "";

        var body = document.getElementById("attachmentTextModalBody");
        if (body) body.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

        modal.classList.add("in");
        modal.style.display = "block";
        modal.removeAttribute("aria-hidden");
        document.body.classList.add("modal-open");

        if (!document.getElementById(BACKDROP_ID)) {
            var backdrop = document.createElement("div");
            backdrop.id = BACKDROP_ID;
            backdrop.className = "modal-backdrop fade in";
            document.body.appendChild(backdrop);
        }
    }

    function closeModal() {
        var modal = document.getElementById(MODAL_ID);
        if (!modal) return;

        modal.classList.remove("in");
        modal.style.display = "none";
        modal.setAttribute("aria-hidden", "true");
        document.body.classList.remove("modal-open");

        var backdrop = document.getElementById(BACKDROP_ID);
        if (backdrop) backdrop.remove();
    }

    document.addEventListener("click", function (event) {
        var trigger = event.target.closest(".js-attachment-text-btn");
        if (trigger) {
            openModal(trigger.getAttribute("data-modal-title"));
            return;
        }
        if (event.target.closest(".js-attachment-text-modal-close")) {
            closeModal();
            return;
        }
        if (event.target.id === MODAL_ID || event.target.id === BACKDROP_ID) {
            closeModal();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") closeModal();
    });
})();
