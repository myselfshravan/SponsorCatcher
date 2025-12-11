the login component:

```html
<div id="main_content_Login_LoginPanel" class="login-form" onkeypress="javascript:return WebForm_FireDefaultButton(event, 'LoginButton')" bis_skin_checked="1">
   
    <a class="login-help" href="javascript:void(0);" onclick="javascript:dialog.open({ 'title': 'How to Log In?', 'url': '/help/loginhelp.aspx?dialog=yes', 'refreshParent': false, 'resizeButton': false, 'openButton': false, 'feedbackButton': false });" title="Click here for help logging in"><i class="icon-question-circle"></i></a>
    <h3 class="form-title">Login to your account </h3>
    <p>
        Login Instructions:

Enter your primary email address (the email at which you receive MHI communications). If this is your first time logging into your account, please click below on forgot your password. You will receive an email with a link to reset your password. If you do not see the email to reset your password, please check your spam folder. If you have any questions, contact registration@mfghome.org.
    </p>
    
    <div id="main_content_Login_pnlLogin" bis_skin_checked="1">
    
        <div id="main_content_Login_LoginValidationSummary" class="alert alert-danger login-validation" style="display:none;" bis_skin_checked="1">

    </div>
        <div class="form-group" bis_skin_checked="1">
            <label class="control-label visible-ie8 visible-ie9 visible-inline">Email:</label>
            <span id="main_content_Login_LoginEmailRequired" title="Email is required to login." class="has-error" style="visibility:hidden;">
                <i class="icon-exclamation-sign tooltips" data-original-title="Email is required to login." data-container="body"></i>
            </span>
            <span id="main_content_Login_LoginEmailExpressionValidator" title="Email is not in a valid format." class="has-error" style="visibility:hidden;">
                <i class="icon-exclamation-sign tooltips" data-original-title="Email is not in a valid format." data-container="body"></i>
            </span>
            <div class="input-icon" bis_skin_checked="1">
                <i class="icon-user"></i>
                <input name="main$content$Login$txtLoginUserName" type="text" maxlength="100" id="main_content_Login_txtLoginUserName" class="form-control placeholder-no-fix login-email" placeholder="Email">
            </div>
        </div>
        <div class="form-group" bis_skin_checked="1">
            <label class="control-label visible-ie8 visible-ie9 visible-inline">Password:</label>
            <span id="main_content_Login_LoginPasswordRequired" title="Password is required to login." class="has-error" style="visibility:hidden;">
                <i class="icon-exclamation-sign tooltips" data-original-title="Password is required to login." data-container="body"></i>
            </span>
            <div id="main_content_Login_ctlLoginPassword_ctl00" bis_skin_checked="1">
     <span id="main_content_Login_ctlLoginPassword_MC"></span>
    </div><div id="main_content_Login_ctlLoginPassword_divPassword" class="input-icon" bis_skin_checked="1">
    <i id="main_content_Login_ctlLoginPassword_lockIcon" class="icon-lock"></i>
    <a href="../Controls/Account/#" id="main_content_Login_ctlLoginPassword_lnkPeek" style="text-decoration: none;" tabindex="-1" onclick="PasswordPeek.showPassword(event,'main_content_Login_ctlLoginPassword_txtPassword','main_content_Login_ctlLoginPassword_showPasswordIcon');">
        <i id="main_content_Login_ctlLoginPassword_showPasswordIcon" class="icon-eye" style="right: 0px; margin: 11px 10px 4px 2px !important;"></i>
    </a>
    <input name="main$content$Login$ctlLoginPassword$txtPassword" type="password" maxlength="50" id="main_content_Login_ctlLoginPassword_txtPassword" class="form-control placeholder-no-fix login-password html-box" placeholder="Password" autocomplete="off">
</div>

        </div>
        <div class="form-actions" bis_skin_checked="1">
            <label class="checkbox">
                <div class="checker" id="uniform-main_content_Login_chkLoginRememberMe" bis_skin_checked="1"><span><input id="main_content_Login_chkLoginRememberMe" type="checkbox" name="main$content$Login$chkLoginRememberMe"></span></div><label for="main_content_Login_chkLoginRememberMe">Remember Me</label>
            </label>
            <div class="form-group" bis_skin_checked="1">
                <div id="captchaV2Container" style="display: none;" bis_skin_checked="1"></div> 
            </div>
                      
            <input type="submit" name="main$content$Login$LoginButton" value="Login" onclick="javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions(&quot;main$content$Login$LoginButton&quot;, &quot;&quot;, true, &quot;LoginValidationSummary&quot;, &quot;&quot;, false, false))" id="LoginButton" class="btn green pull-right">
        </div>
        
        <div id="main_content_Login_divForgotPassword" class="forgot-password" bis_skin_checked="1">
            <a class="forgot-password-help" href="javascript:void(0);" onclick="javascript:dialog.open({ 'title': 'Forgot Your Password?', 'url': '/help/forgotpasswordhelp.aspx?dialog=yes', 'refreshParent': false, 'resizeButton': false, 'openButton': false, 'feedbackButton': false });" title="Click here for help if you forgot your password"><i class="icon-question-circle"></i></a>
            <h4>Forgot your password? </h4>
            <p>
                Click <a onclick="javascript:Login.switchPanels(1);" id="main_content_Login_lnkLoginGoToForgot" href="javascript:__doPostBack('main$content$Login$lnkLoginGoToForgot','')">here</a> to reset your password.
            </p>
        </div>
        <div id="main_content_Login_divSignup" class="create-account" bis_skin_checked="1">
            <p>
                Don't have an account yet?&nbsp;&nbsp;<a onclick="javascript:Login.switchPanels(2);" id="main_content_Login_lnkLoginGoToSignup" href="javascript:__doPostBack('main$content$Login$lnkLoginGoToSignup','')">Create an account.</a>
            </p>
        </div>
    
   </div>
    
    <p class="copyright">
        <span id="main_content_Login_lblVersion" title="Version:9.5.0.18437 Date:11/18/2025 10:14:58 AM LIVE_4">© 2025 - MHI</span>
    </p>

  </div>
  
```
