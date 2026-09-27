# SPDX-License-Identifier: AGPL-3.0-or-later
# Data migration: copy the per-device management-reach / toggle custom-field values into
# SystemConfig, creating the row for a device that has values but no SystemConfig yet.
#
# Reads each device's `custom_field_data` JSON column directly, so it needs no CustomField lookup
# and is unaffected by a field having been renamed or removed. IDEMPOTENT: a field already set on
# the SystemConfig row is left alone, so re-running after a partial apply cannot overwrite an edit.
# REVERSIBLE: the backward pass writes the values back into `custom_field_data`. The custom fields
# themselves are NOT dropped here — that waits until every consumer reads the model.
from django.db import migrations

# custom field name -> (SystemConfig field, kind). "str" values are stripped; "bool" coerced.
FIELDS = {
    "ssh_host": ("ssh_host", "str"),
    "ssh_user": ("ssh_user", "str"),
    "ssh_identity": ("ssh_identity", "str"),
    "login_banner": ("login_banner", "str"),
    "manage_interface_baseline": ("manage_interface_baseline", "bool"),
    "manage_base_lan": ("manage_base_lan", "bool"),
    "manage_lan": ("manage_lan", "bool"),
    "manage_timezone": ("manage_timezone", "bool"),
    "manage_reconcile": ("manage_reconcile", "bool"),
    "manage_plugin_aliases": ("manage_plugin_aliases", "bool"),
    "wan_proto": ("wan_proto", "str"),
    "lan_if": ("lan_if", "str"),
    "vlan_trunk": ("vlan_trunk", "str"),
    "vlanif_pfstyle": ("vlanif_pfstyle", "bool"),
    "openwrt_native_dsa": ("openwrt_native_dsa", "bool"),
    "openwrt_network_reload": ("openwrt_network_reload", "bool"),
    "dhcp_engine": ("dhcp_engine", "str"),
    "haproxy_setpath_separate_type": ("haproxy_setpath_separate_type", "bool"),
}
_BOOL_DEFAULTS = {
    "manage_interface_baseline": False, "manage_base_lan": False, "manage_lan": True,
    "manage_timezone": True, "manage_reconcile": True, "manage_plugin_aliases": True,
    "vlanif_pfstyle": False, "openwrt_native_dsa": False, "openwrt_network_reload": True,
    "haproxy_setpath_separate_type": False,
}


def _present(value):
    """An unset custom field means "no override", exactly as a lookup() default did. A literal
    False IS a value for a boolean, so it must not be treated as absent."""
    return value is not None and value != "" and value != [] and value != {}


def forward(apps, schema_editor):
    Device = apps.get_model("dcim", "Device")
    SystemConfig = apps.get_model("netbox_system_services", "SystemConfig")

    for device in Device.objects.all().iterator():
        data = device.custom_field_data or {}
        wanted = {}
        for cf_name, (field, kind) in FIELDS.items():
            raw = data.get(cf_name)
            if not _present(raw):
                continue
            wanted[field] = bool(raw) if kind == "bool" else str(raw).strip()
        if not wanted:
            continue
        cfg = SystemConfig.objects.filter(device_id=device.pk).first()
        if cfg is None:
            SystemConfig.objects.create(device_id=device.pk, **wanted)
            continue
        # Only fill a field the row has not already been given a non-default value for.
        changed = []
        for field, value in wanted.items():
            current = getattr(cfg, field)
            default = _BOOL_DEFAULTS.get(field, "")
            if current == default:
                setattr(cfg, field, value)
                changed.append(field)
        if changed:
            cfg.save(update_fields=changed)


def backward(apps, schema_editor):
    Device = apps.get_model("dcim", "Device")
    SystemConfig = apps.get_model("netbox_system_services", "SystemConfig")

    for cfg in SystemConfig.objects.all().iterator():
        device = Device.objects.filter(pk=cfg.device_id).first()
        if device is None:
            continue
        data = dict(device.custom_field_data or {})
        for cf_name, (field, kind) in FIELDS.items():
            value = getattr(cfg, field)
            default = _BOOL_DEFAULTS.get(field, "")
            if value != default:
                data[cf_name] = value
        device.custom_field_data = data
        device.save(update_fields=["custom_field_data"])


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_system_services", "0009_systemconfig_mgmt_reach_and_toggles"),
        ("dcim", "__first__"),
    ]
    operations = [migrations.RunPython(forward, backward)]
