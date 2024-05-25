import datetime
import uuid
import peewee
import logging

from app.classes.shared.console import Console
from app.classes.shared.migration import Migrator, MigrateHistory
from app.classes.models.management import Backups, Schedules

logger = logging.getLogger(__name__)


def migrate(migrator: Migrator, database, **kwargs):
    """
    Write your migrations here.
    """
    db = database

    migrator.add_columns("backups", backup_id=peewee.UUIDField(default=uuid.uuid4))
    migrator.add_columns("backups", backup_name=peewee.CharField(default="Default"))
    migrator.add_columns("backups", backup_location=peewee.CharField(default=""))
    migrator.add_columns("backups", enabled=peewee.BooleanField(default=True))
    migrator.add_columns(
        "schedules", action_id=peewee.CharField(null=True, default=None)
    )

    class Servers(peewee.Model):
        server_id = peewee.CharField(primary_key=True, default=str(uuid.uuid4()))
        created = peewee.DateTimeField(default=datetime.datetime.now)
        server_name = peewee.CharField(default="Server", index=True)
        path = peewee.CharField(default="")
        backup_path = peewee.CharField(default="")
        executable = peewee.CharField(default="")
        log_path = peewee.CharField(default="")
        execution_command = peewee.CharField(default="")
        auto_start = peewee.BooleanField(default=0)
        auto_start_delay = peewee.IntegerField(default=10)
        crash_detection = peewee.BooleanField(default=0)
        stop_command = peewee.CharField(default="stop")
        executable_update_url = peewee.CharField(default="")
        server_ip = peewee.CharField(default="127.0.0.1")
        server_port = peewee.IntegerField(default=25565)
        logs_delete_after = peewee.IntegerField(default=0)
        type = peewee.CharField(default="minecraft-java")
        show_status = peewee.BooleanField(default=1)
        created_by = peewee.IntegerField(default=-100)
        shutdown_timeout = peewee.IntegerField(default=60)
        ignored_exits = peewee.CharField(default="0")

        class Meta:
            table_name = "servers"
            database = db

    class NewBackups(peewee.Model):
        backup_id = peewee.UUIDField(primary_key=True, default=uuid.uuid4)
        backup_name = peewee.CharField(default="New Backup")
        backup_location = peewee.CharField(default="")
        excluded_dirs = peewee.CharField(null=True)
        max_backups = peewee.IntegerField()
        server_id = peewee.ForeignKeyField(Servers, backref="backups_server")
        compress = peewee.BooleanField(default=False)
        shutdown = peewee.BooleanField(default=False)
        before = peewee.CharField(default="")
        after = peewee.CharField(default="")
        enabled = peewee.BooleanField(default=True)

        class Meta:
            table_name = "new_backups"
            database = db

    class NewSchedules(peewee.Model):
        schedule_id = peewee.IntegerField(unique=True, primary_key=True)
        server_id = peewee.ForeignKeyField(Servers, backref="schedule_server")
        enabled = peewee.BooleanField()
        action = peewee.CharField()
        interval = peewee.IntegerField()
        interval_type = peewee.CharField()
        start_time = peewee.CharField(null=True)
        command = peewee.CharField(null=True)
        action_id = peewee.CharField(null=True)
        name = peewee.CharField()
        one_time = peewee.BooleanField(default=False)
        cron_string = peewee.CharField(default="")
        parent = peewee.IntegerField(null=True)
        delay = peewee.IntegerField(default=0)
        next_run = peewee.CharField(default="")

        class Meta:
            table_name = "new_schedules"

    migrator.create_table(NewBackups)
    migrator.create_table(NewSchedules)

    migrator.run()

    # Copy data from the existing backups table to the new one
    for backup in Backups.select():
        # Fetch the related server entry from the Servers table
        server = Servers.get(Servers.server_id == backup.server_id)

        # Create a new backup entry with data from the old backup entry and related server
        NewBackups.create(
            backup_name="Default",
            backup_location=server.backup_path,  # Set backup_location equal to backup_path
            excluded_dirs=backup.excluded_dirs,
            max_backups=backup.max_backups,
            server_id=server.server_id,
            compress=backup.compress,
            shutdown=backup.shutdown,
            before=backup.before,
            after=backup.after,
            enabled=True,
        )

    # Drop the existing backups table
    migrator.drop_table("backups")

    # Rename the new table to backups
    migrator.rename_table("new_backups", "backups")
    migrator.drop_columns("servers", ["backup_path"])

    for schedule in Schedules.select():
        action_id = None
        if schedule.command == "backup_server":
            backup = NewBackups.get(NewBackups.server_id == schedule.server_id)
            action_id = backup.backup_id
        NewSchedules.create(
            schedule_id=schedule.schedule_id,
            server_id=schedule.server_id,
            enabled=schedule.enabled,
            action=schedule.action,
            interval=schedule.interval,
            interval_type=schedule.interval_type,
            start_time=schedule.start_time,
            command=schedule.command,
            action_id=action_id,
            name=schedule.name,
            one_time=schedule.one_time,
            cron_string=schedule.cron_string,
            parent=schedule.parent,
            delay=schedule.delay,
            next_run=schedule.next_run,
        )

    # Drop the existing backups table
    migrator.drop_table("schedules")

    # Rename the new table to backups
    migrator.rename_table("new_schedules", "schedules")


def rollback(migrator: Migrator, database, **kwargs):
    """
    Write your rollback migrations here.
    """
    db = database

    migrator.drop_columns("backups", ["name", "backup_id", "backup_location"])
    migrator.add_columns("servers", backup_path=peewee.CharField(default=""))
