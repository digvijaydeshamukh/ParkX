document.addEventListener("DOMContentLoaded", () => {
    console.log("PROFILE.JS FILE LOADED");
    console.log("ParkX Profile JS DOM LOADED");

    // =====================================================
    // ELEMENTS
    // =====================================================

    const profileForm = document.getElementById("profileForm");

    const usernameInput = document.getElementById("username");
    const firstNameInput = document.getElementById("first_name");
    const lastNameInput = document.getElementById("last_name");
    const emailInput = document.getElementById("email");
    const phoneInput = document.getElementById("phone");

    // Profile image
    const profileImageWrapper =
        document.getElementById("profileImageWrapper");

    const profileImageInput =
        document.getElementById("profileImageInput");

    // Profile image modal
    const profileImageModal =
        document.getElementById("profileImageModal");

    const closeProfileImageModal =
        document.getElementById("closeProfileImageModal");

    const uploadProfileImageBtn =
        document.getElementById("uploadProfileImageBtn");

    const removeProfileImageBtn =
        document.getElementById("removeProfileImageBtn");

    // Crop modal
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


    console.log("Profile form:", profileForm);
    console.log("Username:", usernameInput);
    console.log("First name:", firstNameInput);
    console.log("Last name:", lastNameInput);
    console.log("Email:", emailInput);
    console.log("Phone:", phoneInput);

    console.log(
        "Profile image wrapper:",
        profileImageWrapper
    );

    console.log(
        "Profile image modal:",
        profileImageModal
    );

    console.log(
        "Upload button:",
        uploadProfileImageBtn
    );

    console.log(
        "Remove button:",
        removeProfileImageBtn
    );

    console.log(
        "File input:",
        profileImageInput
    );


    // =====================================================
    // VARIABLES
    // =====================================================

    let cropper = null;

    // Holds the cropped image file temporarily
    let croppedImageFile = null;


    // =====================================================
    // GET ACCESS TOKEN
    // =====================================================

    function getAccessToken() {

        return localStorage.getItem("access_token");

    }


    // =====================================================
    // LOAD PROFILE
    // =====================================================

    async function loadProfile() {

        console.log("Loading profile...");

        const accessToken = getAccessToken();

        console.log(
            "Access token exists:",
            !!accessToken
        );


        if (!accessToken) {

            console.error(
                "Access token not found."
            );

            return;

        }


        try {

            const response = await fetch(
                "/api/accounts/profile/",
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${accessToken}`,

                        "Content-Type":
                            "application/json"
                    }
                }
            );


            console.log(
                "Profile API status:",
                response.status
            );


            const data = await response.json();


            console.log(
                "Profile API response:",
                data
            );


            if (!response.ok) {

                console.error(
                    "Profile API error:",
                    data
                );


                if (response.status === 401) {

                    console.error(
                        "Access token expired or invalid."
                    );

                    localStorage.removeItem(
                        "access_token"
                    );

                    localStorage.removeItem(
                        "refresh_token"
                    );

                    localStorage.removeItem(
                        "user"
                    );

                    window.location.href = "/login/";
                    return;

                }

                return;

            }


            populateProfile(data);

        } catch (error) {

            console.error(
                "Error loading profile:",
                error
            );

        }

    }


    // =====================================================
// POPULATE PROFILE
// =====================================================

function populateProfile(data) {

    console.log(
        "Populating profile with:",
        data
    );


    // =================================================
    // HANDLE API RESPONSE
    // =================================================

    // Some APIs return:
    //
    // {
    //     username: "...",
    //     phone: "...",
    //     phone_verified: true
    // }
    //
    // Others return:
    //
    // {
    //     user: {
    //         username: "...",
    //         phone: "...",
    //         phone_verified: true
    //     }
    // }

    const userData =
        data.user || data;


    console.log(
        "Actual user data:",
        userData
    );


    // =================================================
    // USERNAME
    // =================================================

    if (usernameInput) {

        usernameInput.value =
            userData.username || "";

    }


    // =================================================
    // FIRST NAME
    // =================================================

    if (firstNameInput) {

        firstNameInput.value =
            userData.first_name || "";

    }


    // =================================================
    // LAST NAME
    // =================================================

    if (lastNameInput) {

        lastNameInput.value =
            userData.last_name || "";

    }


    // =================================================
    // EMAIL
    // =================================================

    if (emailInput) {

        emailInput.value =
            userData.email || "";

    }


    // =================================================
    // PHONE
    // =================================================

    if (phoneInput) {

        phoneInput.value =
            userData.phone || "";

    }


    // =================================================
    // PHONE VERIFICATION
    // =================================================

    updatePhoneVerificationStatus(
        userData.phone_verified
    );


    console.log(
        "Phone:",
        userData.phone
    );

    console.log(
        "Phone Verified:",
        userData.phone_verified
    );


    // =================================================
    // PROFILE IMAGE
    // =================================================

    if (userData.profile_image) {

        updateProfileImage(
            userData.profile_image
        );

        updateSidebarProfileImage(
            userData.profile_image
        );

    }
    else {

        updateSidebarProfileImage(
            null
        );

    }


    console.log(
        "Profile populated successfully."
    );

}


    // =====================================================
    // UPDATE PROFILE IMAGE PREVIEW
    // =====================================================

    function updateProfileImage(imageURL) {

    // =====================================================
    // MAIN PROFILE IMAGE
    // =====================================================

    const currentPreview =
        document.getElementById("profileImagePreview");


    if (currentPreview) {

        if (currentPreview.tagName === "IMG") {

            currentPreview.src = imageURL;

        } else {

            const image =
                document.createElement("img");

            image.src = imageURL;

            image.alt = "Profile Image";

            image.className = "profile-image";

            image.id = "profileImagePreview";

            currentPreview.replaceWith(image);
        }
    }


    // =====================================================
    // MODAL PROFILE IMAGE
    // =====================================================

    const modalPreview =
        document.querySelector(
            ".profile-image-modal-preview"
        );


    if (!modalPreview) {
        return;
    }


    // Remove existing modal content
    modalPreview.innerHTML = "";


    // Create image
    const modalImage =
        document.createElement("img");


    modalImage.src =
        imageURL;

    modalImage.alt =
        "Profile Image";

    modalImage.id =
        "profileModalImage";

    modalImage.className =
        "profile-modal-image";


    modalPreview.appendChild(
        modalImage
    );
}

    // =====================================================
    // PROFILE FORM SUBMIT
    // =====================================================

    if (profileForm) {

        profileForm.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();

                console.log(
                    "Profile form submitted."
                );


                const accessToken =
                    getAccessToken();


                if (!accessToken) {

                    console.error(
                        "Access token not found."
                    );

                    return;

                }


                const formData =
                    new FormData();


                // First name
                if (firstNameInput) {

                    formData.append(
                        "first_name",
                        firstNameInput.value.trim()
                    );

                }


                // Last name
                if (lastNameInput) {

                    formData.append(
                        "last_name",
                        lastNameInput.value.trim()
                    );

                }


                // Profile image
                if (croppedImageFile) {

                    formData.append(
                        "profile_image",
                        croppedImageFile
                    );

                }
                else if (
                    profileImageInput &&
                    profileImageInput.files.length > 0
                ) {

                    formData.append(
                        "profile_image",
                        profileImageInput.files[0]
                    );

                }


                try {

                    const response =
                        await fetch(
                            "/api/accounts/profile/",
                            {
                                method: "PATCH",

                                headers: {
                                    "Authorization":
                                        `Bearer ${accessToken}`
                                },

                                body: formData
                            }
                        );


                    console.log(
                        "Update profile status:",
                        response.status
                    );


                    const data =
                        await response.json();


                    console.log(
                        "Update profile response:",
                        data
                    );


                    if (!response.ok) {

                        console.error(
                            "Profile update failed:",
                            data
                        );

                        return;

                    }


                    console.log(
                        "Profile updated successfully."
                    );


                    if (data.user) {

                        populateProfile(
                            data.user
                        );

                    }


                    // Clear temporary image
                    croppedImageFile = null;

                    if (profileImageInput) {

                        profileImageInput.value =
                            "";

                    }


                } catch (error) {

                    console.error(
                        "Profile update error:",
                        error
                    );

                }

            }
        );

    }


    // =====================================================
    // OPEN PROFILE IMAGE MODAL
    // =====================================================

    if (profileImageWrapper) {

        profileImageWrapper.addEventListener(
            "click",
            (event) => {

                event.preventDefault();
                event.stopPropagation();

                console.log(
                    "Profile image clicked"
                );


                if (profileImageModal) {

                    profileImageModal.classList.add(
                        "show"
                    );

                }

            }
        );

    }


    // =====================================================
    // CLOSE PROFILE IMAGE MODAL
    // =====================================================

    function closeProfileImageModalFunction() {

        if (profileImageModal) {

            profileImageModal.classList.remove(
                "show"
            );

        }

    }


    // Close button
    if (closeProfileImageModal) {

        closeProfileImageModal.addEventListener(
            "click",
            closeProfileImageModalFunction
        );

    }


    // Click outside modal
    if (profileImageModal) {

        profileImageModal.addEventListener(
            "click",
            (event) => {

                if (
                    event.target ===
                    profileImageModal
                ) {

                    closeProfileImageModalFunction();

                }

            }
        );

    }


    // =====================================================
    // UPLOAD IMAGE BUTTON
    // =====================================================

    if (
        uploadProfileImageBtn &&
        profileImageInput
    ) {

        uploadProfileImageBtn.addEventListener(
            "click",
            (event) => {

                event.preventDefault();
                event.stopPropagation();

                console.log(
                    "Upload image clicked"
                );


                profileImageInput.click();

            }
        );

    }


    // =====================================================
    // IMAGE SELECTED
    // =====================================================

    if (profileImageInput) {

        profileImageInput.addEventListener(
            "change",
            (event) => {

                const file =
                    event.target.files[0];


                if (!file) {

                    return;

                }


                console.log(
                    "Selected image:",
                    file
                );


                // Validate file type
                if (
                    !file.type.startsWith(
                        "image/"
                    )
                ) {

                    alert(
                        "Please select a valid image."
                    );


                    profileImageInput.value =
                        "";

                    return;

                }


                // Validate file size
                const maxSize =
                    5 * 1024 * 1024;


                if (file.size > maxSize) {

                    alert(
                        "Image size must be less than 5 MB."
                    );


                    profileImageInput.value =
                        "";

                    return;

                }


                const reader =
                    new FileReader();


                reader.onload =
                    (readerEvent) => {

                        const imageURL =
                            readerEvent.target.result;


                        openCropModal(
                            imageURL
                        );


                        closeProfileImageModalFunction();

                    };


                reader.readAsDataURL(
                    file
                );

            }
        );

    }


    // =====================================================
    // OPEN CROP MODAL
    // =====================================================

    function openCropModal(imageURL) {

        if (
            !cropModal ||
            !cropImage
        ) {

            console.error(
                "Crop modal elements not found."
            );

            return;

        }


        cropModal.classList.add(
            "show"
        );


        // Destroy previous Cropper instance
        if (cropper) {

            cropper.destroy();

            cropper = null;

        }


        cropImage.src =
            imageURL;


        cropImage.onload =
            () => {

                cropper =
                    new Cropper(
                        cropImage,
                        {
                            aspectRatio: 1,

                            viewMode: 1,

                            dragMode: "move",

                            autoCropArea: 1,

                            responsive: true,

                            background: false,

                            movable: true,

                            zoomable: true,

                            rotatable: false,

                            scalable: false
                        }
                    );

            };

    }


    // =====================================================
    // SAVE CROP
    // =====================================================

    if (saveCrop) {

        saveCrop.addEventListener(
            "click",
            () => {

                if (!cropper) {

                    console.error(
                        "Cropper is not initialized."
                    );

                    return;

                }


                const canvas =
                    cropper.getCroppedCanvas(
                        {
                            width: 400,

                            height: 400,

                            imageSmoothingEnabled:
                                true,

                            imageSmoothingQuality:
                                "high"
                        }
                    );


                if (!canvas) {

                    console.error(
                        "Could not create cropped image."
                    );

                    return;

                }


                // Preview image
                const croppedImageURL =
                    canvas.toDataURL(
                        "image/jpeg",
                        0.9
                    );


                updateProfileImage(
                    croppedImageURL
                );


                // Convert canvas to File
                canvas.toBlob(
                    (blob) => {

                        if (!blob) {

                            console.error(
                                "Could not create image blob."
                            );

                            return;

                        }


                        croppedImageFile =
                            new File(
                                [
                                    blob
                                ],
                                "profile_image.jpg",
                                {
                                    type:
                                        "image/jpeg"
                                }
                            );


                        console.log(
                            "Cropped image ready:",
                            croppedImageFile
                        );


                        closeCropModalFunction();

                    },
                    "image/jpeg",
                    0.9
                );

            }
        );

    }


    // =====================================================
    // CLOSE CROP MODAL
    // =====================================================

    function closeCropModalFunction() {

        if (cropModal) {

            cropModal.classList.remove(
                "show"
            );

        }


        if (cropper) {

            cropper.destroy();

            cropper = null;

        }


        if (cropImage) {

            cropImage.src = "";

        }

    }


    // Close crop button
    if (closeCropModal) {

        closeCropModal.addEventListener(
            "click",
            closeCropModalFunction
        );

    }


    // Cancel crop
    if (cancelCrop) {

        cancelCrop.addEventListener(
            "click",
            closeCropModalFunction
        );

    }


    // =====================================================
// REMOVE PROFILE IMAGE
// =====================================================

if (removeProfileImageBtn) {

    removeProfileImageBtn.addEventListener(
        "click",
        async (event) => {

            event.preventDefault();
            event.stopPropagation();

            console.log("Remove image clicked");

            const confirmed = confirm(
                "Are you sure you want to remove your profile image?"
            );

            if (!confirmed) {
                return;
            }

            const accessToken = getAccessToken();

            if (!accessToken) {
                console.error("Access token not found.");
                return;
            }

            try {

                const formData = new FormData();

                // Tell backend to remove the image
                formData.append(
                    "profile_image",
                    ""
                );

                const response = await fetch(
                    "/api/accounts/profile/",
                    {
                        method: "PATCH",

                        headers: {
                            "Authorization":
                                `Bearer ${accessToken}`
                        },

                        body: formData
                    }
                );

                console.log(
                    "Remove image status:",
                    response.status
                );

                const data = await response.json();

                console.log(
                    "Remove image response:",
                    data
                );

                if (!response.ok) {

                    console.error(
                        "Remove image failed:",
                        data
                    );

                    alert(
                        "Unable to remove profile image."
                    );

                    return;
                }


                // =================================================
                // REMOVE IMAGE FROM MAIN PROFILE AREA
                // =================================================

                const currentPreview =
                    document.getElementById(
                        "profileImagePreview"
                    );

                if (currentPreview) {

                    const placeholder =
                        document.createElement("div");

                    placeholder.id =
                        "profileImagePreview";

                    placeholder.className =
                        "profile-image-placeholder";

                    placeholder.innerHTML =
                        '<i class="fa-solid fa-user"></i>';

                    currentPreview.replaceWith(
                        placeholder
                    );
                }


                // =================================================
                // REMOVE IMAGE FROM MODAL
                // =================================================

                const modalPreview =
                    document.querySelector(
                        ".profile-image-modal-preview"
                    );

                if (modalPreview) {

                    modalPreview.innerHTML = `
                        <div
                            id="profileModalPlaceholder"
                            class="profile-modal-placeholder"
                        >
                            <i class="fa-solid fa-user"></i>
                        </div>
                    `;
                }


                // =================================================
                // CLEAR FILE INPUT
                // =================================================

                if (profileImageInput) {

                    profileImageInput.value = "";

                }


                // =================================================
                // CLEAR CROPPED IMAGE
                // =================================================

                croppedImageFile = null;


                // =================================================
                // CLOSE MODAL
                // =================================================

                closeProfileImageModalFunction();


                console.log(
                    "Profile image removed successfully."
                );

            } catch (error) {

                console.error(
                    "Remove image error:",
                    error
                );

            }

        }
    );

}


    // =====================================================
    // ESCAPE KEY
    // =====================================================

    document.addEventListener(
        "keydown",
        (event) => {

            if (event.key !== "Escape") {

                return;

            }


            closeProfileImageModalFunction();

            closeCropModalFunction();

        }
    );

    function updateSidebarProfileImage(imageURL) {

    const sidebarImageContainer =
        document.querySelector(".sidebar-profile-image");

    if (!sidebarImageContainer) {
        console.warn("Sidebar profile image container not found.");
        return;
    }

    if (!imageURL) {
        sidebarImageContainer.innerHTML = `
            <i class="fa-solid fa-user"></i>
        `;
        return;
    }

    sidebarImageContainer.innerHTML = `
        <img
            src="${imageURL}"
            alt="Profile Image"
            class="sidebar-profile-img"
        >
    `;

    console.log(
        "Sidebar profile image updated:",
        imageURL
    );
    }

    // =====================================================
    // UPDATE PHONE NUMBER FUNCTION
    // =====================================================

    // =====================================================
// UPDATE PHONE VERIFICATION STATUS
// =====================================================

function updatePhoneVerificationStatus(phoneVerified) {

    console.log(
        "Phone verification status received:",
        phoneVerified
    );

    const verifyPhoneButton =
        document.getElementById("verify-phone-btn");

    const phoneVerifiedStatus =
        document.getElementById("phone-verified-status");


    console.log(
        "Verify phone button:",
        verifyPhoneButton
    );

    console.log(
        "Phone verified status:",
        phoneVerifiedStatus
    );


    if (!verifyPhoneButton) {

        console.warn(
            "Verify phone button not found."
        );

        return;
    }


    if (!phoneVerifiedStatus) {

        console.warn(
            "Phone verified status element not found."
        );

        return;
    }


    // Convert possible string values to boolean
    const isVerified =
        phoneVerified === true ||
        phoneVerified === "true" ||
        phoneVerified === 1 ||
        phoneVerified === "1";


    // =================================================
    // PHONE VERIFIED
    // =================================================

    if (isVerified) {

        verifyPhoneButton.style.display =
            "none";

        phoneVerifiedStatus.style.display =
            "inline-flex";

        console.log(
            "PHONE VERIFIED -> Verify button hidden."
        );

    }


    // =================================================
    // PHONE NOT VERIFIED
    // =================================================

    else {

        verifyPhoneButton.style.display =
            "inline-flex";

        phoneVerifiedStatus.style.display =
            "none";

        console.log(
            "PHONE NOT VERIFIED -> Verify button shown."
        );

    }

    }


    // =====================================================
    // LOAD PROFILE
    // =====================================================

    loadProfile();

});