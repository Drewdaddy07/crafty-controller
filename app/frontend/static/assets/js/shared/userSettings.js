$(document).on("submit", ".bootbox form", function (e) {
    e.preventDefault();
    $(".bootbox .btn-primary").click();
});

$(".edit_password").on("click", async function () {
    const token = getCookie("_xsrf");
    let user_id = $(this).data('id');
    bootbox.dialog({
        message: `
    <form class="form" id='infos' action=''>
      <div class="form-group">
        <label for="new_password">${$(this).data("translate1")}</label>
        <input class="form-control" type='password' id="password0" name='new_password' /><br>
      </div>
      <div class="form-group">
        <label for="confirm_password">${$(this).data("translate2")}</label>
        <input class="form-control" type='password' id="password1" name='confirm_password' />
      </div>
    </form>
  `,
        buttons: {
            cancel: {
                label: "Cancel",
                className: "btn-secondary"
            },
            confirm: {
                label: "OK",
                className: "btn-primary",
                callback: function () {
                    let pw0 = document.getElementById("password0").value;
                    let pw1 = document.getElementById("password1").value;
                    if (!pw0 || pw0 !== pw1) {
                        bootbox.alert({
                            title: "Error",
                            message: "Passwords must match"
                        });
                        return false;
                    }

                    (async () => {
                        let res = await fetch(`/api/v2/users/${user_id}`, {
                            method: 'PATCH',
                            headers: { 'X-XSRFToken': token },
                            body: JSON.stringify({ "password": pw0.toString() }),
                        });
                        let responseData = await res.json();

                        if (responseData.status === "ok") {
                            bootbox.hideAll();
                        } else {
                            bootbox.hideAll();
                            bootbox.alert({
                                title: responseData.status,
                                message: responseData.error_data
                            });
                        }
                    })();
                }
            }
        }
    });
});

$(".edit_user").on("click", function () {
    const token = getCookie("_xsrf");
    let username = $(this).data('name');
    let user_id = $(this).data('id');
    bootbox.confirm(`<form class="form" id='infos' action=''>\
      <div class="form-group">
      <label for="username">${$(this).data("translate")}</label>
      <input class="form-control" type='text' name='username' id="username_field" value=${username} /><br/>\
      </div>
      </form>`, async function (result) {
        if (result) {
            let new_username = $("#username_field").val();
            let res = await fetch(`/api/v2/users/${user_id}`, {
                method: 'PATCH',
                headers: {
                    'X-XSRFToken': token
                },
                body: JSON.stringify({ "username": new_username }),
            });
            let responseData = await res.json();
            if (responseData.status === "ok") {
                $(`#user_${user_id}`).html(` ${new_username}`)
                $(`#username_${user_id}`).data('name', new_username);
            } else {

                bootbox.alert({
                    title: responseData.error,
                    message: responseData.error_data
                });
            }
        }
    }
    )
});

function generatePassword(length) {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let pass = '';
    const array = new Uint32Array(length);
    crypto.getRandomValues(array);
    for (let i = 0; i < length; i++) {
        pass += chars[array[i] % chars.length];
    }
    return pass;
}

$(".reset_password").on("click", function () {
    const token = getCookie("_xsrf");
    let el = $(this);
    let resetUserId = el.data("id");
    let resetUsername = $("<div>").text(el.data("username")).html();

    // Read translations from data attributes
    let tResetPassword = el.data("t-reset-password") || "Reset Password";
    let tNewPassword = el.data("t-new-password") || "New Password";
    let tGenerateRandom = el.data("t-generate-random") || "Generate Random";
    let tPasswordLength = el.data("t-password-length") || "Password Length";
    let tRequireChangeLabel = el.data("t-require-change-label") || "Require password change on next login";
    let tExpiresIn = el.data("t-expires-in") || "Expires In";
    let tSetPassword = el.data("t-set-password") || "Set Password";
    let tPasswordGenerated = el.data("t-password-generated") || "Password Set Successfully";
    let tCopyPassword = el.data("t-copy-password") || "Copy Password";
    let tCancel = el.data("t-cancel") || "Cancel";
    let tResetError = el.data("t-reset-error") || "Failed to reset password. Please try again.";

    // Build expiry options from presets
    let presets = el.data("presets") || [];
    let defaultExpiry = el.data("default-expiry");
    let expiryOptions = '';
    for (let i = 0; i < presets.length; i++) {
        let p = presets[i];
        let safeLabel = $("<div>").text(p.label).html();
        let selected = (String(p.hours) === String(defaultExpiry)) ? ' selected' : '';
        let val = (p.hours === null) ? -1 : p.hours;
        expiryOptions += '<option value="' + val + '"' + selected + '>' + safeLabel + '</option>';
    }

    bootbox.dialog({
        title: tResetPassword + " - " + resetUsername,
        message: `
        <form class="form" id="reset-password-form">
          <div class="form-group">
            <label for="reset_password_field">${tNewPassword}</label>
            <div class="input-group">
              <input type="text" class="form-control" id="reset_password_field"
                placeholder="${tNewPassword}" autocomplete="off">
              <div class="input-group-append">
                <button class="btn btn-outline-info" type="button" id="btn_generate_password">
                  <i class="ph-fill ph-dice-five"></i>
                  ${tGenerateRandom}
                </button>
              </div>
            </div>
          </div>
          <div class="form-group mt-3">
            <label for="reset_pw_length">${tPasswordLength}</label>
            <input type="number" class="form-control" id="reset_pw_length" value="16" min="8" max="128">
          </div>
          <div class="form-group mt-3">
            <div class="form-check" style="text-align:left">
              <input type="checkbox" class="form-check-input" id="require_change" checked>
              <label class="form-check-label" for="require_change">
                ${tRequireChangeLabel}
              </label>
            </div>
          </div>
          <div class="form-group mt-3" id="expiry_group">
            <label for="reset_expires">${tExpiresIn}</label>
            <select class="form-control" id="reset_expires" name="expires">
              ${expiryOptions}
            </select>
          </div>
        </form>
      `,
        buttons: {
            cancel: {
                label: tCancel,
                className: "btn-secondary"
            },
            confirm: {
                label: tSetPassword,
                className: "btn-warning",
                callback: function () {
                    let password = $("#reset_password_field").val();
                    if (!password || password.length < 8) {
                        bootbox.alert({
                            title: "Error",
                            message: "Password must be at least 8 characters."
                        });
                        return false;
                    }
                    let requireChange = $("#require_change").is(":checked");
                    let body = {
                        password: password,
                        require_password_change: requireChange,
                    };
                    if (requireChange) {
                        body.expires_hours = parseInt($("#reset_expires").val());
                    }

                    (async () => {
                        try {
                            let res = await fetch(`/api/v2/users/${resetUserId}/reset-password`, {
                                method: 'POST',
                                headers: {
                                    'X-XSRFToken': token,
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify(body),
                            });
                            let responseData = await res.json();

                            if (responseData.status === "ok") {
                                let noticeText = "";
                                if (requireChange) {
                                    noticeText += '<p class="text-info mt-2"><i class="ph-fill ph-info"></i> ' + tRequireChangeLabel + '</p>';
                                    if (responseData.data.expires) {
                                        noticeText += '<small class="text-muted">Expires: '
                                            + $("<div>").text(responseData.data.expires).html() + '</small>';
                                    }
                                }
                                bootbox.alert({
                                    title: tPasswordGenerated,
                                    message: `
                      <div class="form-group">
                        <label>${tNewPassword}</label>
                        <div class="input-group">
                          <input type="text" class="form-control" id="generated-password" readonly>
                          <div class="input-group-append">
                            <button class="btn btn-outline-primary" type="button"
                              onclick="navigator.clipboard.writeText(document.getElementById('generated-password').value)">
                              <i class="ph-fill ph-copy"></i>
                              ${tCopyPassword}
                            </button>
                          </div>
                        </div>
                        ` + noticeText + `
                      </div>
                    `,
                                });
                                setTimeout(function () {
                                    document.getElementById('generated-password').value = responseData.data.password;
                                }, 100);
                            } else {
                                bootbox.alert({
                                    title: $("<div>").text(responseData.error).html(),
                                    message: $("<div>").text(responseData.error_data).html()
                                });
                            }
                        } catch (error) {
                            bootbox.alert({
                                title: "Error",
                                message: tResetError
                            });
                        }
                    })();
                }
            }
        }
    });

    // Wire up generate button after dialog renders
    setTimeout(function () {
        $("#btn_generate_password").on("click", function () {
            let len = parseInt($("#reset_pw_length").val()) || 16;
            $("#reset_password_field").val(generatePassword(len));
        });
        // Toggle expiry visibility based on require change checkbox
        $("#require_change").on("change", function () {
            if ($(this).is(":checked")) {
                $("#expiry_group").show();
            } else {
                $("#expiry_group").hide();
            }
        });
    }, 200);
});
