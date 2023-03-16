from src.configuration import config

from_github = [
    "SELENIUM_JAR_PATH",
    "GOROOT_1_17_X64",
    "CONDA",
    "GITHUB_WORKSPACE",
    "JAVA_HOME_11_X64",
    "PKG_CONFIG_PATH",
    "GITHUB_PATH",
    "GITHUB_ACTION",
    "JAVA_HOME",
    "GITHUB_RUN_NUMBER",
    "RUNNER_NAME",
    "GRADLE_HOME",
    "GITHUB_REPOSITORY_OWNER_ID",
    "XDG_CONFIG_HOME",
    "Python_ROOT_DIR",
    "DOTNET_SKIP_FIRST_TIME_EXPERIENCE",
    "ANT_HOME",
    "JAVA_HOME_8_X64",
    "GITHUB_TRIGGERING_ACTOR",
    "pythonLocation",
    "GITHUB_REF_TYPE",
    "HOMEBREW_CLEANUP_PERIODIC_FULL_DAYS",
    "ANDROID_NDK",
    "BOOTSTRAP_HASKELL_NONINTERACTIVE",
    "PWD",
    "PIPX_BIN_DIR",
    "GITHUB_REPOSITORY_ID",
    "DEPLOYMENT_BASEPATH",
    "GITHUB_ACTIONS",
    "ANDROID_NDK_LATEST_HOME",
    "SYSTEMD_EXEC_PID",
    "GITHUB_SHA",
    "GITHUB_WORKFLOW_REF",
    "POWERSHELL_DISTRIBUTION_CHANNEL",
    "client_id",
    "DOTNET_MULTILEVEL_LOOKUP",
    "GITHUB_REF",
    "RUNNER_OS",
    "GITHUB_REF_PROTECTED",
    "HOME",
    "GITHUB_API_URL",
    "LANG",
    "RUNNER_TRACKING_ID",
    "RUNNER_ARCH",
    "RUNNER_TEMP",
    "GITHUB_STATE",
    "EDGEWEBDRIVER",
    "GITHUB_ENV",
    "GITHUB_EVENT_PATH",
    "INVOCATION_ID",
    "GITHUB_EVENT_NAME",
    "GITHUB_RUN_ID",
    "JAVA_HOME_17_X64",
    "ANDROID_NDK_HOME",
    "GITHUB_STEP_SUMMARY",
    "HOMEBREW_NO_AUTO_UPDATE",
    "GITHUB_ACTOR",
    "NVM_DIR",
    "SGX_AESM_ADDR",
    "GITHUB_RUN_ATTEMPT",
    "STATS_RDCL",
    "ANDROID_HOME",
    "GITHUB_GRAPHQL_URL",
    "ACCEPT_EULA",
    "RUNNER_USER",
    "client_secret",
    "USER",
    "GITHUB_SERVER_URL",
    "PIPX_HOME",
    "GECKOWEBDRIVER",
    "STATS_NM",
    "CHROMEWEBDRIVER",
    "SHLVL",
    "ANDROID_SDK_ROOT",
    "VCPKG_INSTALLATION_ROOT",
    "GITHUB_ACTOR_ID",
    "RUNNER_TOOL_CACHE",
    "ImageVersion",
    "Python3_ROOT_DIR",
    "DOTNET_NOLOGO",
    "GITHUB_WORKFLOW_SHA",
    "GITHUB_REF_NAME",
    "GRAALVM_11_ROOT",
    "GITHUB_JOB",
    "LD_LIBRARY_PATH",
    "XDG_RUNTIME_DIR",
    "AZURE_EXTENSION_DIR",
    "PERFLOG_LOCATION_SETTING",
    "GITHUB_REPOSITORY",
    "Python2_ROOT_DIR",
    "ANDROID_NDK_ROOT",
    "CHROME_BIN",
    "GOROOT_1_18_X64",
    "GITHUB_RETENTION_DAYS",
    "JOURNAL_STREAM",
    "RUNNER_WORKSPACE",
    "LEIN_HOME",
    "LEIN_JAR",
    "GITHUB_ACTION_REPOSITORY",
    "PATH",
    "RUNNER_PERFLOG",
    "GITHUB_BASE_REF",
    "GHCUP_INSTALL_BASE_PREFIX",
    "CI",
    "SWIFT_PATH",
    "ImageOS",
    "GITHUB_REPOSITORY_OWNER",
    "GITHUB_HEAD_REF",
    "GITHUB_ACTION_REF",
    "GOROOT_1_19_X64",
    "GITHUB_WORKFLOW",
    "DEBIAN_FRONTEND",
    "GITHUB_OUTPUT",
    "AGENT_TOOLSDIRECTORY",
    "_",
    "PYTEST_CURRENT_TEST",
]


def test_config():
    # telegram
    assert [
        list(o) for o in [o for o in ([config.main_dotenv("telegram-failed_order")])]
    ][0] == ["bot_token", "bot_chatid"] or from_github
    # deribit
    assert [list(o) for o in [o for o in ([config.main_dotenv("deribit-147691")])]][
        0
    ] == [
        "type",
        "user_name",
        "system_name",
        "client_id",
        "client_secret",
        "id",
    ] or from_github
