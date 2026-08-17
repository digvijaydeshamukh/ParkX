document.addEventListener("DOMContentLoaded", function () {

    console.log("ParkX Profile JS Loaded");

    /* =====================================================
       ELEMENTS
    ===================================================== */

    const profileImageWrapper =
        document.getElementById("profileImageWrapper");

    const profileImageMenu =
        document.getElementById("profileImageMenu");

    const addProfileImageBtn =
        document.getElementById("addProfileImageBtn");

    const cropProfileImageBtn =
        document.getElementById("cropProfileImageBtn");

    const profileImageInput =
        document.getElementById("profileImageInput");

    const cropModal =
        document.getElementById("cropModal");

    const cropImage =
        document.getElementById("cropImage");

    const closeCropModal =
        document.getElementById("closeCropModal");

    const cancelCrop =
        document.getElementById("cancelCrop");

    const saveCrop =
        document.getElementById("saveCrop");


    let cropper = null;


    /* =====================================================
       PROFILE IMAGE CLICK
       Click image -> show/hide menu
    ===================================================== */

    if (profileImageWrapper && profileImageMenu) {

        profileImageWrapper.addEventListener("click", function (event) {

            event.stopPropagation();

            profileImageMenu.classList.toggle("show");

        });

    }


    /* =====================================================
       ADD NEW PROFILE IMAGE
    ===================================================== */

    if (addProfileImageBtn && profileImageInput) {

        addProfileImageBtn.addEventListener("click", function (event) {

            event.stopPropagation();

            profileImageInput.click();

        });

    }


    /* =====================================================
       IMAGE SELECTED
    ===================================================== */

    if (profileImageInput) {

        profileImageInput.addEventListener("change", function (event) {

            const file = event.target.files[0];

            if (!file) {
                return;
            }


            /* Check image */

            if (!file.type.startsWith("image/")) {

                alert("Please select a valid image.");

                profileImageInput.value = "";

                return;

            }


            /* Read image */

            const reader = new FileReader();

            reader.onload = function (e) {

                openCropModal(e.target.result);

            };

            reader.readAsDataURL(file);


            /* Hide menu */

            if (profileImageMenu) {

                profileImageMenu.classList.remove("show");

            }

        });

    }


    /* =====================================================
       CROP EXISTING PROFILE IMAGE
    ===================================================== */

    if (cropProfileImageBtn) {

        cropProfileImageBtn.addEventListener("click", function (event) {

            event.stopPropagation();


            const currentImage =
                document.getElementById("profileImagePreview");


            /* No image */

            if (
                !currentImage ||
                currentImage.tagName !== "IMG"
            ) {

                alert("Please add a profile image first.");

                return;

            }


            /* Open crop modal */

            openCropModal(currentImage.src);


            /* Hide menu */

            if (profileImageMenu) {

                profileImageMenu.classList.remove("show");

            }

        });

    }


    /* =====================================================
       OPEN CROP MODAL
    ===================================================== */

    function openCropModal(imageURL) {

        if (!cropModal || !cropImage) {
            return;
        }


        cropModal.classList.add("show");

        cropImage.src = imageURL;


        /* Destroy previous cropper */

        if (cropper) {

            cropper.destroy();

            cropper = null;

        }


        /* Create cropper after image loads */

        cropImage.onload = function () {

            cropper = new Cropper(
                cropImage,
                {
                    aspectRatio: 1,

                    viewMode: 1,

                    dragMode: "move",

                    autoCropArea: 1,

                    responsive: true,

                    background: false
                }
            );

        };

    }


    /* =====================================================
       SAVE CROPPED IMAGE
    ===================================================== */

    if (saveCrop) {

        saveCrop.addEventListener("click", function () {

            if (!cropper) {
                return;
            }


            const canvas =
                cropper.getCroppedCanvas({
                    width: 400,
                    height: 400,
                    imageSmoothingQuality: "high"
                });


            if (!canvas) {
                return;
            }


            const croppedImageURL =
                canvas.toDataURL("image/png");


            const currentPreview =
                document.getElementById(
                    "profileImagePreview"
                );


            /* Existing image */

            if (
                currentPreview &&
                currentPreview.tagName === "IMG"
            ) {

                currentPreview.src =
                    croppedImageURL;

            }


            /* Placeholder */

            else if (currentPreview) {

                const newImage =
                    document.createElement("img");


                newImage.src =
                    croppedImageURL;

                newImage.alt =
                    "Profile Image";

                newImage.className =
                    "profile-image";

                newImage.id =
                    "profileImagePreview";


                currentPreview.replaceWith(
                    newImage
                );

            }


            closeCropModalFunction();

        });

    }


    /* =====================================================
       CLOSE CROP MODAL
    ===================================================== */

    function closeCropModalFunction() {

        if (cropModal) {

            cropModal.classList.remove("show");

        }


        if (cropper) {

            cropper.destroy();

            cropper = null;

        }


        if (cropImage) {

            cropImage.src = "";

        }

    }


    /* =====================================================
       CLOSE BUTTON
    ===================================================== */

    if (closeCropModal) {

        closeCropModal.addEventListener(
            "click",
            closeCropModalFunction
        );

    }


    /* =====================================================
       CANCEL BUTTON
    ===================================================== */

    if (cancelCrop) {

        cancelCrop.addEventListener(
            "click",
            closeCropModalFunction
        );

    }


    /* =====================================================
       CLICK OUTSIDE PROFILE MENU
    ===================================================== */

    document.addEventListener("click", function (event) {

        if (
            profileImageMenu &&
            profileImageWrapper &&
            !profileImageMenu.contains(event.target) &&
            !profileImageWrapper.contains(event.target)
        ) {

            profileImageMenu.classList.remove("show");

        }

    });


    /* =====================================================
       ESCAPE KEY
    ===================================================== */

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {

            if (profileImageMenu) {

                profileImageMenu.classList.remove("show");

            }


            if (
                cropModal &&
                cropModal.classList.contains("show")
            ) {

                closeCropModalFunction();

            }

        }

    });

});