import logging
from pathlib import PurePosixPath, Path

logger = logging.Logger(__name__)

OUTPUT_FILE_NAME = "hytale.zip"


class Hytale:
    def __init__(self, server_instance):
        self.server = server_instance

    def install_or_update(self):
        bb_cache = self.server.big_bucket.get_bucket_data()
        unix_exe = PurePosixPath(bb_cache["linux_installer"]).name
        windows_exe = PurePosixPath(bb_cache["windows_installer"]).name
        install_command = (
            f"./{unix_exe} {bb_cache["download_path_command"]} {OUTPUT_FILE_NAME}"
        )
        if self.server.helper.is_os_windows():
            install_command = (
                f"{self.server.server_path}/{windows_exe} "
                f"{bb_cache["download_path_command"]} {OUTPUT_FILE_NAME}"
            )

        # Unzip downloaded archive.
        self.server.file_helper.unzip_file(
            Path(self.server.server_path, OUTPUT_FILE_NAME),
            self.server.server_path,
        )

    def install_or_update_monitoring_plugins(self):
        bb_cache = self.server.big_bucket.get_bucket_data()
        logger.info(
            "Installing Nitrado Webserver Plugin to server %s", self.server.name
        )
        # make sure our mods dir exists before doing anything
        # Download webserver plugin required for query plugin
        self.server.helper.ensure_dir_exists(Path(self.server.server_path, "mods"))
        self.server.file_helper.ssl_get_file(
            bb_cache["plugins"]["webserver_plugin"],
            Path(self.server.server_path, "mods"),
            "nitrado-webserver.jar",
        )
        # Download query plugin
        logger.info("Installing Nitrado Query Plugin to server %s", self.server.name)
        self.server.file_helper.ssl_get_file(
            bb_cache["plugins"]["query_plugin"],
            Path(self.server.server_path, "mods"),
            "nitrado-query.jar",
        )
